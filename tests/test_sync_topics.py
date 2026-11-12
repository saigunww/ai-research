"""Privacy and evidence regressions for the unattended topic publisher."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "sync_topics.py"
SPEC = importlib.util.spec_from_file_location("sync_topics", MODULE)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def translated(text):
    return {lang: text for lang in sync.LANGUAGES}


class TopicSyncTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.sources = self.base / "sources"
        self.source = self.sources / "approved-direction"
        self.source.mkdir(parents=True)
        self.readme = self.source / "README.md"
        self.readme.write_text("Private student and experimental details must never be published.")
        self.config_path = self.base / "config.private.json"
        self.state_path = self.base / "state.private.json"
        self.pending_path = self.base / "pending.private.json"
        self.config = {
            "schemaVersion": 1,
            "discoveryRoots": [str(self.sources)],
            "categories": [{"id": "life", "label": translated("Life science")}],
            "topics": [{"approved": True, "reviewedAt": "2026-11-12",
                        "public": {"id": "biology", "category": "life", "stage": "proposal",
                                   "title": translated("Biological data"),
                                   "summary": translated("Develop research literacy through biological data."),
                                   "tags": {lang: ["Life science"] for lang in sync.LANGUAGES}},
                        "sources": [str(self.source)],
                        "practiceRunRoots": [str(self.source / "runs")]}],
        }

    def run_sync(self, day="2026-11-12"):
        self.config_path.write_text(json.dumps(self.config))
        return sync.sync_topics(self.config_path, self.state_path, self.pending_path, today=day)

    def test_whitelist_does_not_publish_source_text_or_paths(self):
        result = self.run_sync()
        public = json.dumps({key: result[key] for key in ("categories", "topics")})
        self.assertNotIn(str(self.base), public)
        self.assertNotIn("Private student", public)
        self.assertEqual(set(result["topics"][0]), sync.PUBLIC_TOPIC_FIELDS | {"updatedAt"})
        self.assertEqual(self.state_path.stat().st_mode & 0o777, 0o600)

    def test_unchanged_scan_is_stable_and_changed_source_updates_date(self):
        first = self.run_sync()
        second = self.run_sync("2026-11-13")
        self.assertTrue(first["sourceChanged"])
        self.assertFalse(second["sourceChanged"])
        self.assertEqual(first["topics"], second["topics"])
        self.readme.write_text("New private research notes, never a public summary.")
        third = self.run_sync("2026-11-14")
        self.assertTrue(third["sourceChanged"])
        self.assertEqual(third["topics"][0]["updatedAt"], "2026-11-14")
        self.assertEqual(first["topics"][0]["summary"], third["topics"][0]["summary"])

    def test_unknown_direction_is_only_in_private_pending(self):
        unknown = self.sources / "private-name-unknown-topic"
        unknown.mkdir()
        (unknown / "statement.txt").write_text("Secret details")
        result = self.run_sync()
        self.assertEqual(len(result["topics"]), 1)
        self.assertEqual(result["pendingCount"], 1)
        self.assertNotIn(unknown.name, json.dumps(result))
        pending = json.loads(self.pending_path.read_text())
        self.assertEqual(pending["unmappedSources"][0]["path"], str(unknown))

    def test_new_reviewed_direction_automatically_publishes(self):
        self.run_sync()
        source = self.sources / "new-direction"
        source.mkdir()
        row = json.loads(json.dumps(self.config["topics"][0]))
        row["public"]["id"] = "new-biology"
        row["sources"] = [str(source)]
        row["practiceRunRoots"] = []
        row["reviewedAt"] = "2026-11-13"
        self.config["topics"].append(row)
        result = self.run_sync("2026-11-13")
        self.assertEqual(len(result["topics"]), 2)
        self.assertEqual(result["pendingCount"], 0)

    def test_empty_results_and_placeholder_summary_do_not_upgrade(self):
        run = self.source / "runs" / "job_1"
        run.mkdir(parents=True)
        (run / "SUCCESS").touch()
        (run / "summary.md").write_text("Placeholder")
        (run / "metrics.csv").write_text("model,r2\n")
        self.assertEqual(self.run_sync()["topics"][0]["stage"], "proposal")

    def make_run(self, name="job_1", metrics="model,r2\nexample,0.72\n"):
        run = self.source / "runs" / name
        run.mkdir(parents=True)
        (run / "summary.md").write_text("Real report with interpreted results. " * 5)
        (run / "metrics.csv").write_text(metrics)
        (run / "SUCCESS").touch()
        return run

    def test_complete_formal_results_upgrade_and_do_not_downgrade(self):
        self.run_sync()
        run = self.make_run()
        result = self.run_sync("2026-11-13")
        self.assertEqual(result["topics"][0]["stage"], "practice")
        self.assertEqual(result["topics"][0]["updatedAt"], "2026-11-13")
        (run / "SUCCESS").unlink()
        self.assertEqual(self.run_sync("2026-11-14")["topics"][0]["stage"], "practice")

    def test_pilot_run_does_not_become_formal_practice(self):
        self.config["topics"][0]["public"]["stage"] = "pilot"
        self.make_run("smoke_verified")
        self.make_run("pilot_2")
        self.assertEqual(self.run_sync()["topics"][0]["stage"], "pilot")

    def test_nonfinite_metrics_and_failed_marker_do_not_upgrade(self):
        self.make_run("job_1", "model,r2\nexample,nan\n")
        failed = self.make_run("job_2")
        (failed / "FAILED").touch()
        self.assertEqual(self.run_sync()["topics"][0]["stage"], "proposal")

    def test_stale_completion_flag_does_not_upgrade_a_rewritten_run(self):
        run = self.make_run()
        os.utime(run / "SUCCESS", (1000, 1000))
        self.assertEqual(self.run_sync()["topics"][0]["stage"], "proposal")

    def test_missing_mapped_source_retains_audited_stage_and_warns(self):
        self.config["topics"][0]["public"]["stage"] = "practice"
        self.run_sync()
        self.readme.unlink()
        self.source.rmdir()
        result = self.run_sync("2026-11-13")
        self.assertEqual(result["topics"][0]["stage"], "practice")
        self.assertEqual(result["warningCount"], 1)

    def test_missing_root_fails_without_replacing_state(self):
        self.run_sync()
        before = self.state_path.read_bytes()
        self.config["discoveryRoots"] = [str(self.base / "unmounted")]
        with self.assertRaises(sync.TopicSyncError):
            self.run_sync()
        self.assertEqual(self.state_path.read_bytes(), before)

    def test_unreviewed_fields_or_private_text_are_rejected(self):
        self.config["topics"][0]["public"]["evidence"] = "/private/path"
        with self.assertRaises(sync.TopicSyncError):
            self.run_sync()
        del self.config["topics"][0]["public"]["evidence"]
        self.config["topics"][0]["public"]["summary"]["en"] = "Read /work/private/results.json"
        with self.assertRaises(sync.TopicSyncError):
            self.run_sync()

    def test_symlink_sources_and_shared_stores_are_not_scanned(self):
        link = self.sources / "link"
        link.symlink_to(self.source, target_is_directory=True)
        self.config["topics"][0]["sources"] = [str(link)]
        with self.assertRaises(sync.TopicSyncError):
            self.run_sync()
        with self.assertRaises(sync.TopicSyncError):
            sync._source_path("/work/shared/models", [Path("/work")])

    def test_model_data_and_log_directories_are_not_scanned(self):
        self.run_sync()
        for name in ("models", "data", "logs", "checkpoints"):
            path = self.source / name
            path.mkdir()
            (path / "sensitive.json").write_text("Private and not needed")
        result = self.run_sync("2026-11-13")
        self.assertFalse(result["sourceChanged"])


if __name__ == "__main__":
    unittest.main()
