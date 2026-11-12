"""Regression tests for the public-data boundary and unattended Git publication.

All files and Git repositories are temporary; no network or live checkout writes.
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("sync_publisher_under_test", SCRIPTS / "sync_and_publish.py")
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)


def localized(value):
    return {language: value for language in publisher.LANGUAGES}


def catalog():
    return {
        "updatedAt": "2026-11-12",
        "categories": [{"id": "life", "label": localized("Life science")}],
        "topics": [{"id": "biology", "category": "life", "stage": "practice",
                    "title": localized("Biology"),
                    "summary": localized("Develop research literacy."),
                    "tags": {language: ["Science"] for language in publisher.LANGUAGES}}],
        "honors": [{"id": "he-doshisha-2027", "year": 2027,
                    "student": {"zh-CN": "何同学", "zh-TW": "何同學", "ja": "何さん", "en": "Student He"},
                    "university": localized("Doshisha University"),
                    "school": localized("Science and Engineering"),
                    "department": localized("Chemistry"), "program": localized("Undergraduate admission"),
                    "poster": {"src": "images/honors/approved.png", "width": 16, "height": 24}}],
    }


def admissions_feed():
    return {
        "updatedAt": "2026-11-12", "checkedAt": "2026-11-12T20:00:00+09:00",
        "items": [{
            "id": "sample-university-graduate", "level": "graduate", "academicYear": "2027",
            "sourceUrl": "https://www.example.ac.jp/admissions/", "verifiedAt": "2026-11-12",
            "checkedAt": "2026-11-12T20:00:00+09:00", "status": "verified",
            "university": localized("Example University"), "program": localized("Graduate admission"),
            "route": localized("International admission"), "scope": localized("Official application guidance"),
            "summary": localized("Consult the university for current eligibility and requirements."),
            "tags": {language: ["Graduate"] for language in publisher.LANGUAGES},
        }],
    }


class PublisherTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "repo"
        self.state = self.base / "private-state"
        self.mirror = self.base / "mirror"
        (self.root / "images/honors").mkdir(parents=True)
        self.state.mkdir()
        self.image = self.root / "images/honors/approved.png"
        Image.new("RGB", (16, 24), "red").save(self.image)
        self.data = catalog()
        self.feed = admissions_feed()
        publisher.save(self.root / publisher.CATALOG, self.data)
        publisher.save(self.root / publisher.ADMISSIONS, self.feed)
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(publisher, "ROOT", self.root).start()
        mock.patch.object(publisher, "STATE", self.state).start()
        mock.patch.object(publisher, "MIRROR", self.mirror).start()

    def validate(self, value=None):
        publisher.validate_catalog(self.data if value is None else value, self.root)

    def test_valid_catalog_and_poster_are_accepted(self):
        self.validate()

    def test_private_fields_are_rejected_at_every_public_boundary(self):
        for location in ((), ("categories", 0), ("topics", 0), ("honors", 0), ("honors", 0, "poster")):
            with self.subTest(location=location):
                data = copy.deepcopy(self.data)
                record = data
                for key in location:
                    record = record[key]
                record["private_source"] = "/work/student/internal-proposal.pdf"
                with self.assertRaises(ValueError):
                    self.validate(data)

    def test_private_paths_and_statement_text_are_rejected_in_all_languages(self):
        for language in publisher.LANGUAGES:
            for value in ("Read /work/private/a.pdf", "Read /home/student/result", "file:///etc/passwd",
                          "A 志望理由 document", "statement of purpose", "result.private.json"):
                with self.subTest(language=language, value=value):
                    data = copy.deepcopy(self.data)
                    data["topics"][0]["summary"][language] = value
                    with self.assertRaises(ValueError):
                        self.validate(data)

    def test_missing_translation_duplicate_id_and_unknown_category_are_rejected(self):
        values = []
        data = copy.deepcopy(self.data)
        del data["topics"][0]["title"]["en"]
        values.append(data)
        data = copy.deepcopy(self.data)
        data["topics"].append(copy.deepcopy(data["topics"][0]))
        values.append(data)
        data = copy.deepcopy(self.data)
        data["topics"][0]["category"] = "unknown"
        values.append(data)
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.validate(value)

    def test_full_student_name_and_external_poster_are_rejected(self):
        for name, src in (("何某某", "images/honors/approved.png"),
                          ("何同学", "https://example.com/private.png"),
                          ("何同学", "images/honors/../../private.png")):
            with self.subTest(name=name, src=src):
                data = copy.deepcopy(self.data)
                data["honors"][0]["student"]["zh-CN"] = name
                data["honors"][0]["poster"]["src"] = src
                with self.assertRaises(ValueError):
                    self.validate(data)

    def test_mismatched_or_nonimage_poster_is_rejected(self):
        self.data["honors"][0]["poster"]["height"] = 25
        with self.assertRaises(ValueError):
            self.validate()
        self.data["honors"][0]["poster"]["height"] = 24
        self.image.write_text("private document disguised as PNG")
        with self.assertRaises((ValueError, OSError)):
            self.validate()

    def test_traversal_absolute_and_symlink_destinations_are_rejected(self):
        for name in ("../private.txt", "images/../../private.txt", "/tmp/private.txt", "images\\private.txt"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    publisher.safe_path(self.root, name)
        outside = self.base / "outside"
        outside.mkdir()
        (self.root / "linked").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            publisher.safe_path(self.root, "linked/anything.txt")
        self.image.unlink()
        self.image.symlink_to(outside / "private.png")
        with self.assertRaises(ValueError):
            self.validate()

    def test_atomic_write_does_not_follow_symlinks(self):
        outside = self.base / "private.txt"
        outside.write_text("private original")
        link = self.root / "alias.txt"
        link.symlink_to(outside)
        with self.assertRaises(ValueError):
            publisher.atomic_write(link, b"replacement")
        self.assertEqual(outside.read_text(), "private original")

    def test_generated_path_whitelist_excludes_site_code_and_private_data(self):
        for name in ("data/catalog.json", "data/admissions.json", "images/honors/checksum-123.webp", "images/honors/a.png"):
            self.assertTrue(publisher.generated(name), name)
        for name in ("index.html", "assets/site.js", "data/topic_state.private.json", "scripts/sync_topics.py",
                     "data/admissions_state.private.json", "admissions_state.private.json",
                     "images/honors/../statement.png", "images/honors/private.pdf", "images/other.png"):
            self.assertFalse(publisher.generated(name), name)

    def test_dirty_checkout_stops_before_fetch_or_source_read(self):
        with mock.patch.object(publisher, "git", return_value=" M index.html") as git, \
                mock.patch.object(publisher, "prepare") as prepare:
            with self.assertRaisesRegex(RuntimeError, "Local changes"):
                publisher.run(publish=True)
        self.assertEqual(git.call_args_list, [mock.call("status", "--porcelain")])
        prepare.assert_not_called()

    def test_nonmain_branch_is_never_published(self):
        def git(*args, **kwargs):
            if args == ("status", "--porcelain"):
                return ""
            if args == ("branch", "--show-current"):
                return "feature/user-work"
            self.fail("Unexpected Git operation: " + repr(args))
        with mock.patch.object(publisher, "git", side_effect=git):
            with self.assertRaisesRegex(RuntimeError, "main branch"):
                publisher.integrate_remote()

    def test_new_user_edit_during_prepare_is_preserved(self):
        original = (self.root / publisher.CATALOG).read_bytes()
        def prepare(stage):
            (self.root / "index.html").write_text("User is editing this")
            publisher.save(stage / publisher.CATALOG, {**self.data, "updatedAt": "2026-11-13"})
            return self.data, [publisher.CATALOG], {}
        with mock.patch.object(publisher, "integrate_remote"), \
                mock.patch.object(publisher, "prepare", side_effect=prepare), \
                mock.patch.object(publisher, "git", return_value=" M index.html") as git:
            with self.assertRaisesRegex(RuntimeError, "Local changes"):
                publisher.run(publish=True)
        self.assertEqual((self.root / publisher.CATALOG).read_bytes(), original)
        self.assertEqual((self.root / "index.html").read_text(), "User is editing this")
        self.assertEqual(git.call_args_list, [mock.call("status", "--porcelain")])

    def source_mocks(self, data=None, feed=None):
        value = self.data if data is None else data
        public_feed = self.feed if feed is None else feed
        publisher.save(self.state / "sources.private.json", {
            "honors_json": str(self.base / "source.json"),
            "honors_site_root": str(self.base / "upstream"),
            "honors_originals": str(self.base / "originals"),
        })
        mock.patch.object(publisher, "sync_topics", return_value={
            "categories": value["categories"], "topics": value["topics"], "pendingCount": 0}).start()
        mock.patch.object(publisher, "build_honors", return_value=(value["honors"], {"status": "ok"})).start()
        def admissions(config, state, current, *, checked_at):
            self.assertEqual(config, self.state / "admissions_sources.private.json")
            self.assertEqual(current, self.feed)
            self.assertTrue(str(state).startswith(str(self.state / "staging-")))
            publisher.save(state, {"internalFingerprint": "private-monitor-state"})
            return public_feed, {"status": "ok"}
        mock.patch.object(publisher, "build_admissions", side_effect=admissions).start()

    def test_invalid_import_never_reaches_public_checkout_or_git_add(self):
        before = (self.root / publisher.CATALOG).read_bytes()
        bad = copy.deepcopy(self.data)
        bad["topics"][0]["evidence"] = "/work/internal/proposal.pdf"
        self.source_mocks(bad)
        with mock.patch.object(publisher, "integrate_remote"), mock.patch.object(publisher, "git") as git:
            with self.assertRaises(ValueError):
                publisher.run(publish=True)
        self.assertEqual((self.root / publisher.CATALOG).read_bytes(), before)
        git.assert_not_called()
        self.assertFalse((self.state / "topic_state.private.json").exists())

    def test_prepare_is_staged_and_preview_does_not_mutate_public_files(self):
        before = (self.root / publisher.CATALOG).read_bytes()
        updated = copy.deepcopy(self.data)
        updated["topics"][0]["summary"] = localized("Updated approved overview.")
        self.source_mocks(updated)
        with mock.patch.object(publisher, "git") as git:
            result = publisher.run(publish=False)
        self.assertEqual(result["changedFiles"], [publisher.CATALOG])
        self.assertEqual(result["status"], "preview")
        self.assertEqual((self.root / publisher.CATALOG).read_bytes(), before)
        self.assertTrue((self.state / "preview.private.json").exists())
        self.assertFalse((self.state / "admissions_state.private.json").exists())
        git.assert_not_called()

    def test_invalid_admissions_feed_blocks_all_public_changes(self):
        before_catalog = (self.root / publisher.CATALOG).read_bytes()
        before_admissions = (self.root / publisher.ADMISSIONS).read_bytes()
        updated = copy.deepcopy(self.data)
        updated["topics"][0]["summary"] = localized("A valid updated overview.")
        bad = copy.deepcopy(self.feed)
        bad["items"][0]["privateMonitorState"] = {"source": "/work/private/source.pdf"}
        self.source_mocks(updated, feed=bad)
        with mock.patch.object(publisher, "integrate_remote"), mock.patch.object(publisher, "git") as git:
            with self.assertRaises(ValueError):
                publisher.run(publish=True)
        self.assertEqual((self.root / publisher.CATALOG).read_bytes(), before_catalog)
        self.assertEqual((self.root / publisher.ADMISSIONS).read_bytes(), before_admissions)
        self.assertFalse((self.state / "admissions_state.private.json").exists())
        git.assert_not_called()

    def test_unexpected_staged_file_blocks_commit_and_push(self):
        self.source_mocks()
        self.data["topics"][0]["summary"] = localized("Changed approved overview.")
        calls = []
        def git(*args, **kwargs):
            calls.append(args)
            if args == ("status", "--porcelain"):
                return ""
            if args[0] == "add":
                self.assertEqual(args, ("add", "--", publisher.CATALOG))
                return ""
            if args == ("diff", "--cached", "--name-only"):
                return publisher.CATALOG + "\nindex.html"
            self.fail("Unexpected Git operation: " + repr(args))
        with mock.patch.object(publisher, "integrate_remote"), mock.patch.object(publisher, "git", side_effect=git):
            with self.assertRaisesRegex(RuntimeError, "Unexpected staged"):
                publisher.run(publish=True)
        self.assertFalse(any(args[0] in ("commit", "push") for args in calls))

    def test_only_validated_generated_paths_are_added_committed_and_pushed(self):
        updated = copy.deepcopy(self.data)
        updated["topics"][0]["summary"] = localized("Changed approved overview.")
        self.source_mocks(updated)
        calls = []
        def git(*args, **kwargs):
            calls.append(args)
            if args == ("status", "--porcelain"):
                return ""
            if args[0] == "add":
                self.assertEqual(args, ("add", "--", publisher.CATALOG))
                return ""
            if args == ("diff", "--cached", "--name-only"):
                return publisher.CATALOG
            if args[0] == "commit":
                self.assertTrue(args[2].startswith(publisher.PREFIX))
                return ""
            if args == ("rev-parse", "HEAD"):
                return "approved-commit"
            if args == ("rev-parse", "HEAD^{tree}"):
                return "approved-tree"
            if args == ("push", "origin", "main"):
                # A retry may only publish this commit after recording its provenance.
                receipt = publisher.load(self.state / "publisher_commits.private.json")
                self.assertEqual(receipt["approved-commit"]["tree"], "approved-tree")
                return ""
            self.fail("Unexpected Git operation: " + repr(args))
        with mock.patch.object(publisher, "integrate_remote"), \
                mock.patch.object(publisher, "git", side_effect=git), \
                mock.patch.object(publisher, "pending_commits", return_value=["approved-commit"]), \
                mock.patch.object(publisher, "mirror") as mirror:
            result = publisher.run(publish=True)
        self.assertEqual(result["status"], "published")
        self.assertEqual(result["changedFiles"], [publisher.CATALOG])
        self.assertEqual(publisher.load(self.root / publisher.CATALOG)["topics"], updated["topics"])
        self.assertEqual(sum(args[0] == "push" for args in calls), 1)
        mirror.assert_called_once_with("approved-commit")

    def test_admissions_update_is_published_but_monitor_state_stays_private(self):
        updated = copy.deepcopy(self.feed)
        updated["items"][0]["status"] = "changed"
        self.source_mocks(feed=updated)
        calls = []
        def git(*args, **kwargs):
            calls.append(args)
            if args == ("status", "--porcelain"):
                return ""
            if args[0] == "add":
                self.assertEqual(args, ("add", "--", publisher.ADMISSIONS))
                return ""
            if args == ("diff", "--cached", "--name-only"):
                return publisher.ADMISSIONS
            if args[0] == "commit":
                return ""
            if args == ("rev-parse", "HEAD"):
                return "admissions-commit"
            if args == ("rev-parse", "HEAD^{tree}"):
                return "admissions-tree"
            if args == ("push", "origin", "main"):
                return ""
            self.fail("Unexpected Git operation: " + repr(args))
        with mock.patch.object(publisher, "integrate_remote"), \
                mock.patch.object(publisher, "git", side_effect=git), \
                mock.patch.object(publisher, "pending_commits", return_value=["admissions-commit"]), \
                mock.patch.object(publisher, "mirror"):
            result = publisher.run(publish=True)
        self.assertEqual(result["changedFiles"], [publisher.ADMISSIONS])
        self.assertEqual(publisher.load(self.root / publisher.ADMISSIONS), updated)
        self.assertEqual(publisher.load(self.state / "admissions_state.private.json"),
                         {"internalFingerprint": "private-monitor-state"})
        self.assertEqual((self.state / "admissions_state.private.json").stat().st_mode & 0o777, 0o600)
        self.assertFalse(list(self.root.rglob("*.private.json")))
        self.assertEqual(sum(args[0] == "push" for args in calls), 1)

    def test_mirror_copies_public_admissions_but_never_private_monitor_state(self):
        files = "data/admissions.json\ndata/admissions_state.private.json\nscripts/sync_admissions.py"
        with mock.patch.object(publisher, "git", return_value=files), \
                mock.patch.object(publisher.subprocess, "check_output", return_value=b"public admissions") as show:
            publisher.mirror("approved-commit")
        show.assert_called_once_with(["git", "show", "approved-commit:data/admissions.json"],
                                     cwd=self.root, timeout=30)
        self.assertEqual((self.mirror / publisher.ADMISSIONS).read_bytes(), b"public admissions")
        self.assertFalse((self.mirror / "data/admissions_state.private.json").exists())

    def test_diverged_remote_never_resets_rebases_merges_or_pushes(self):
        calls = []
        def git(*args, **kwargs):
            calls.append(args)
            if args == ("status", "--porcelain"):
                return ""
            if args == ("branch", "--show-current"):
                return "main"
            if args == ("fetch", "origin", "main"):
                return ""
            if args == ("rev-list", "HEAD..origin/main"):
                return "remote-new-commit"
            self.fail("Unexpected Git operation: " + repr(args))
        with mock.patch.object(publisher, "git", side_effect=git), \
                mock.patch.object(publisher, "pending_commits", return_value=["local-auto-commit"]):
            with self.assertRaisesRegex(RuntimeError, "Remote changed"):
                publisher.integrate_remote()
        self.assertFalse(any(args[0] in ("reset", "rebase", "merge", "push") for args in calls))

    def init_git(self):
        self.repo_git("init", "-b", "main")
        self.repo_git("config", "user.name", "Temporary Test")
        self.repo_git("config", "user.email", "test@example.invalid")
        self.repo_git("add", ".")
        self.repo_git("commit", "-m", "Initial approved site")
        self.repo_git("update-ref", "refs/remotes/origin/main", "HEAD")

    def repo_git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def test_unpushed_manual_commit_is_not_automatically_pushed(self):
        self.init_git()
        self.data["updatedAt"] = "2026-11-13"
        publisher.save(self.root / publisher.CATALOG, self.data)
        self.repo_git("add", publisher.CATALOG)
        self.repo_git("commit", "-m", "User edited catalog")
        with self.assertRaises(RuntimeError):
            publisher.pending_commits()

    def test_automatic_subject_does_not_allow_commit_of_code(self):
        self.init_git()
        (self.root / "index.html").write_text("User changed the homepage")
        self.repo_git("add", "index.html")
        self.repo_git("commit", "-m", publisher.PREFIX + "2026-11-12T20:00:00+09:00")
        self.record_receipt()
        with self.assertRaises(RuntimeError):
            publisher.pending_commits()

    def record_receipt(self, tree=None):
        commit = self.repo_git("rev-parse", "HEAD")
        publisher.save(self.state / "publisher_commits.private.json", {
            commit: {"tree": tree or self.repo_git("rev-parse", "HEAD^{tree}")}})
        return commit

    def test_manual_commit_reusing_auto_subject_needs_private_receipt(self):
        self.init_git()
        self.data["updatedAt"] = "2026-11-13"
        publisher.save(self.root / publisher.CATALOG, self.data)
        self.repo_git("add", publisher.CATALOG)
        self.repo_git("commit", "-m", publisher.PREFIX + "2026-11-12T20:00:00+09:00")
        with self.assertRaisesRegex(RuntimeError, "receipt"):
            publisher.pending_commits()
        self.record_receipt(tree="not-the-approved-tree")
        with self.assertRaisesRegex(RuntimeError, "receipt"):
            publisher.pending_commits()
        commit = self.record_receipt()
        self.assertEqual(publisher.pending_commits(), [commit])


if __name__ == "__main__":
    unittest.main()
