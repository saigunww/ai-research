"""Offline regressions for official-source monitoring and public-data boundaries."""

import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "sync_admissions.py"
SPEC = importlib.util.spec_from_file_location("sync_admissions", MODULE)
admissions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(admissions)


def translations(text):
    return {language: text for language in admissions.LANGUAGES}


def document(text="Admissions research experience and extracurricular activities.", url="https://example.ac.jp/admissions/"):
    return {"sha256": admissions._sha(text), "finalUrl": url, "kind": "html", "bytes": len(text), "text": text}


class FakeResponse:
    def __init__(self, body=b"", status=200, headers=None):
        self.body = io.BytesIO(body)
        self.status = status
        self.headers = headers or {"Content-Type": "text/html"}
        self.closed = False

    def read(self, size, decode_content=True):
        return self.body.read(size)

    def close(self):
        self.closed = True


class AdmissionsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.config_path, self.state_path = self.base / "config.private.json", self.base / "state.private.json"
        self.public = {
            "id": "example-undergrad", "level": "undergraduate", "academicYear": "2027",
            "university": translations("Example University"), "program": translations("Science"),
            "route": translations("Comprehensive selection"),
            "scope": translations("This information applies to the named admission route only."),
            "summary": translations("Applicants may discuss research and extracurricular experience."),
            "tags": {lang: ["Research experience"] for lang in admissions.LANGUAGES},
            "sourceUrl": "https://example.ac.jp/admissions/", "verifiedAt": "2026-11-12",
        }
        self.config = {"items": [{"public": self.public, "revision": "2026-11-12-v1"}]}

    def run_build(self, feed=None, content=None, error=None, timestamp="2026-11-12T19:00:00+09:00"):
        self.config_path.write_text(json.dumps(self.config))
        kwargs = {"side_effect": error} if error else {"return_value": content or document()}
        with mock.patch.object(admissions, "fetch_document", **kwargs):
            return admissions.build_admissions(self.config_path, self.state_path, feed, timestamp)

    def test_baseline_stable_change_persists_and_revision_accepts(self):
        first, _ = self.run_build()
        self.assertEqual(first["items"][0]["status"], "verified")
        second, _ = self.run_build(first, document("A changed official requirement with enough public text."))
        self.assertEqual(second["items"][0]["status"], "changed")
        third, _ = self.run_build(second, document("A changed official requirement with enough public text."))
        self.assertEqual(third["items"][0]["status"], "changed")
        self.config["items"][0]["revision"] = "2026-11-12-v2"
        self.public["summary"] = translations("A newly reviewed high-level summary.")
        fourth, _ = self.run_build(third, document("A changed official requirement with enough public text."))
        self.assertEqual(fourth["items"][0]["status"], "verified")
        self.assertEqual(fourth["items"][0]["summary"], self.public["summary"])

    def test_unchanged_recovery_restores_verified(self):
        first, _ = self.run_build()
        second, _ = self.run_build(first, error=admissions.FetchError("connection_failed"))
        self.assertEqual(second["items"][0]["status"], "unavailable")
        third, _ = self.run_build(second)
        self.assertEqual(third["items"][0]["status"], "verified")
        changed, _ = self.run_build(third, document("Temporary modified official requirements."))
        self.assertEqual(changed["items"][0]["status"], "changed")
        recovered, _ = self.run_build(changed)
        self.assertEqual(recovered["items"][0]["status"], "verified")

    def test_failed_new_revision_retains_last_published_summary(self):
        first, _ = self.run_build()
        self.config["items"][0]["revision"] = "new-revision"
        self.public["summary"] = translations("A new summary that has not yet passed source verification.")
        failed, report = self.run_build(first, error=admissions.FetchError("http_unavailable"))
        self.assertEqual(failed["items"][0]["summary"], first["items"][0]["summary"])
        self.assertEqual(report["counts"]["unavailable"], 1)
        state = json.loads(self.state_path.read_text())
        self.assertEqual(state["items"]["example-undergrad"]["revision"], "2026-11-12-v1")

    def test_partial_initial_failure_never_establishes_baseline(self):
        pdf = "https://example.ac.jp/admissions/requirements.pdf"
        self.config["items"][0]["monitorUrls"] = [self.public["sourceUrl"], pdf]
        self.config_path.write_text(json.dumps(self.config))

        def fetched(url):
            if url == pdf:
                raise admissions.FetchError("pdf_extraction_failed")
            return document()

        with mock.patch.object(admissions, "fetch_document", side_effect=fetched):
            feed, _ = admissions.build_admissions(self.config_path, self.state_path, None, "2026-11-12T19:00:00+09:00")
        self.assertEqual(feed["items"][0]["status"], "unavailable")
        state = json.loads(self.state_path.read_text())
        self.assertNotIn("baselineSha256", state["items"]["example-undergrad"])

    def test_pdf_content_change_is_detected_without_html_change(self):
        pdf = "https://example.ac.jp/admissions/requirements.pdf"
        self.config["items"][0]["monitorUrls"] = [self.public["sourceUrl"], pdf]
        self.config_path.write_text(json.dumps(self.config))
        content = {self.public["sourceUrl"]: document(), pdf: document("Original PDF requirement", pdf)}
        with mock.patch.object(admissions, "fetch_document", side_effect=lambda url: content[url]):
            first, _ = admissions.build_admissions(self.config_path, self.state_path, None, "2026-11-12T19:00:00+09:00")
            content[pdf] = document("Changed PDF requirement", pdf)
            second, _ = admissions.build_admissions(self.config_path, self.state_path, first, "2026-11-12T20:00:00+09:00")
        self.assertEqual(first["items"][0]["status"], "verified")
        self.assertEqual(second["items"][0]["status"], "changed")

    def test_required_terms_are_case_insensitive_and_never_exported(self):
        self.config["items"][0]["requiredTerms"] = ["ADMISSIONS", "Research"]
        feed, _ = self.run_build()
        self.assertEqual(feed["items"][0]["status"], "verified")
        failed, report = self.run_build(feed, document("A different page without the required matching phrases."))
        self.assertEqual(failed["items"][0]["status"], "unavailable")
        self.assertEqual(report["errors"][0]["code"], "required_text_missing")
        self.assertNotIn("requiredTerms", json.dumps(feed))
        self.assertNotIn("Admissions research experience", self.state_path.read_text())

    def test_public_whitelist_rejects_private_fields_and_paths(self):
        self.public["evidencePath"] = "/work/private/file"
        with self.assertRaises(admissions.AdmissionsSyncError):
            self.run_build()
        del self.public["evidencePath"]
        self.public["summary"]["en"] = "See /home/private/file"
        with self.assertRaises(admissions.AdmissionsSyncError):
            self.run_build()

    def test_requirement_name_statement_of_purpose_is_allowed(self):
        self.public["summary"] = translations("Official requirements mention 志望理由书 and a statement of purpose.")
        feed, _ = self.run_build()
        self.assertEqual(feed["items"][0]["status"], "verified")

    def test_summary_edit_requires_revision_change(self):
        first, _ = self.run_build()
        state = self.state_path.read_bytes()
        self.public["summary"] = translations("A different summary without a revision bump.")
        with self.assertRaises(admissions.AdmissionsSyncError):
            self.run_build(first)
        self.assertEqual(self.state_path.read_bytes(), state)

    def test_invalid_feed_is_rejected_before_fetch_and_no_state_written(self):
        self.config_path.write_text(json.dumps(self.config))
        with mock.patch.object(admissions, "fetch_document") as fetch:
            with self.assertRaises(admissions.AdmissionsSyncError):
                admissions.build_admissions(self.config_path, self.state_path, {"private": "secret"}, "2026-11-12T19:00:00+09:00")
            fetch.assert_not_called()
        self.assertFalse(self.state_path.exists())

    def test_max_workers_is_three(self):
        real_executor = admissions.ThreadPoolExecutor
        with mock.patch.object(admissions, "ThreadPoolExecutor", wraps=real_executor) as executor:
            self.run_build()
        self.assertEqual(executor.call_args.kwargs["max_workers"], 3)

    def test_bad_domains_and_excess_monitor_urls_fail_before_fetch(self):
        for url in ("http://example.ac.jp/", "https://example.com/", "https://ac.jp/", "https://example.ac.jp.evil.com/",
                    "https://localhost/", "https://user:password@example.ac.jp/", "https://example.ac.jp:444/"):
            with self.subTest(url=url), self.assertRaises(admissions.AdmissionsSyncError):
                admissions.validate_official_url(url)
        self.config["items"][0]["monitorUrls"] = ["https://example.ac.jp/" + str(index) for index in range(4)]
        with self.assertRaises(admissions.AdmissionsSyncError):
            self.run_build()

    def test_private_dns_answer_is_blocked(self):
        answers = [(2, 1, 6, "", ("127.0.0.1", 443)), (2, 1, 6, "", ("8.8.8.8", 443))]
        with mock.patch.object(admissions.socket, "getaddrinfo", return_value=answers):
            with self.assertRaises(admissions.FetchError) as error:
                admissions._public_addresses("example.ac.jp")
        self.assertEqual(error.exception.code, "nonpublic_address_blocked")

    def test_waseda_exception_is_exact_and_not_a_domain_wildcard(self):
        approved = "https://www.waseda.jp/admission/"
        self.assertEqual(admissions.validate_official_url(approved), approved)
        for url in ("https://foo.waseda.jp/", "https://waseda.jp/", "https://www.waseda.jp.evil.com/"):
            with self.subTest(url=url), self.assertRaises(admissions.AdmissionsSyncError):
                admissions.validate_official_url(url)

    def test_redirect_cannot_escape_official_domain(self):
        response = FakeResponse(status=302, headers={"Location": "https://attacker.example/private"})
        with mock.patch.object(admissions, "_public_addresses", return_value=["8.8.8.8"]), \
             mock.patch.object(admissions, "_open_https", return_value=(response, mock.Mock())) as connection:
            with self.assertRaises(admissions.FetchError) as error:
                admissions.fetch_document("https://example.ac.jp/admissions/")
        self.assertEqual(error.exception.code, "redirect_domain_blocked")
        self.assertEqual(connection.call_count, 1)
        self.assertTrue(response.closed)

    def test_official_redirect_rechecks_dns(self):
        response = FakeResponse(status=302, headers={"Location": "https://other.ac.jp/admissions/"})
        with mock.patch.object(admissions, "_public_addresses", side_effect=[["8.8.8.8"], admissions.FetchError("nonpublic_address_blocked")]) as resolve, \
             mock.patch.object(admissions, "_open_https", return_value=(response, mock.Mock())):
            with self.assertRaises(admissions.FetchError):
                admissions.fetch_document("https://example.ac.jp/admissions/")
        self.assertEqual(resolve.call_count, 2)

    def test_normalization_removes_navigation_and_scripts(self):
        first = b"<html><header>Old heading</header><nav>Menu one</nav><main>Real admission requirements. Research experience is considered alongside application documents.</main><script>private()</script></html>"
        second = first.replace(b"Old heading", b"Changed heading").replace(b"Menu one", b"Menu two")
        self.assertEqual(admissions._html_text(first), admissions._html_text(second))
        self.assertNotIn("private", admissions._html_text(first))

    def test_challenge_and_oversized_documents_never_become_baselines(self):
        challenge = b"<html><body>Just a moment. Please verify you are human before viewing this admissions page.</body></html>"
        fixtures = [(FakeResponse(challenge), "verification_page"),
                    (FakeResponse(b"", headers={"Content-Length": str(admissions.MAX_BYTES + 1)}), "document_too_large")]
        for response, code in fixtures:
            with self.subTest(code=code), \
                 mock.patch.object(admissions, "_public_addresses", return_value=["8.8.8.8"]), \
                 mock.patch.object(admissions, "_open_https", return_value=(response, mock.Mock())):
                with self.assertRaises(admissions.FetchError) as error:
                    admissions.fetch_document("https://example.ac.jp/admissions/")
                self.assertEqual(error.exception.code, code)

    def test_ordinary_html_fetch_returns_only_internal_text_and_digest(self):
        body = b"<html><body><main>Official admission requirements include research experience and extracurricular activities for the specified route.</main></body></html>"
        with mock.patch.object(admissions, "_public_addresses", return_value=["8.8.8.8"]), \
             mock.patch.object(admissions, "_open_https", return_value=(FakeResponse(body), mock.Mock())):
            result = admissions.fetch_document("https://example.ac.jp/admissions/")
        self.assertEqual(result["kind"], "html")
        self.assertEqual(len(result["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
