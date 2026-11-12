"""Exercise the public import boundary and preservation on source failures."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_honors import build_honors


def picture(color="red", format="PNG"):
    stream = io.BytesIO()
    Image.new("RGB", (32, 48), color).save(stream, format=format)
    return stream.getvalue()


class HonorSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "upstream"
        self.site = self.root / "website"
        self.posters = self.root / "posters"
        self.source.mkdir()
        (self.site / "images").mkdir(parents=True)
        self.feed = self.source / "honors_data.json"
        self.original = picture()
        self.row = self.source_row(self.original)
        (self.site / "images/existing.png").write_bytes(self.original)
        self.current = [{
            "id": "he-doshisha-2027", "year": 2027,
            "student": {"zh-CN": "何同学", "zh-TW": "何同學", "ja": "何さん", "en": "Student He"},
            "university": {"zh-CN": "同志社大学", "zh-TW": "同志社大學", "ja": "同志社大学", "en": "Doshisha University"},
            "school": {"zh-CN": "理工学部", "zh-TW": "理工學部", "ja": "理工学部", "en": "Faculty of Science and Engineering"},
            "department": {"zh-CN": "机能分子・生命化学科", "en": "Department of Molecular Chemistry and Biochemistry"},
            "program": {"zh-CN": "学部合格", "en": "Undergraduate admission"},
            "poster": {"src": "images/existing.png", "width": 32, "height": 48},
        }]

    def source_row(self, original, name="何同学", university="同志社大学理工学部", year="2027", color="red"):
        digest = hashlib.sha256(original).hexdigest()
        relative = "assets/honors/" + digest[:24] + ".webp"
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(picture(color, "WEBP"))
        return {"id": digest, "name": name, "university": university, "year": year, "subject": "ai-research", "image": relative}

    def write_feed(self, items):
        self.feed.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")

    def sync(self, current=None, **kwargs):
        return build_honors(self.feed, self.source, self.current if current is None else current, self.site / "images", **kwargs)

    def add_original(self, data, name="approved.png"):
        path = self.posters / "2027年度/AI科研背景提升" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_preserves_existing_high_resolution_and_all_translations(self):
        self.write_feed([self.row])
        honors, report = self.sync()
        self.assertEqual(honors, self.current)
        self.assertEqual(report["accepted_count"], 1)
        self.assertFalse(report["changed"])
        self.assertEqual(report["image_operations"], [])
        self.assertEqual(report["status"], "ok")

    def test_new_public_record_copies_only_checksum_verified_original(self):
        original = picture("blue")
        row = self.source_row(original, "张三同学", "東京大学工学系研究科", color="blue")
        row["statement"] = "PRIVATE-UNPUBLISHED-DOCUMENT"
        row["private_path"] = "/work/student/statement.pdf"
        self.add_original(original)
        (self.posters / "private_statement.pdf").write_text("not a poster")
        self.write_feed([self.row, row])
        honors, report = self.sync(source_posters_root=self.posters)
        self.assertEqual(len(honors), 2)
        added = honors[1]
        self.assertEqual(added["student"]["zh-CN"], "张同学")
        self.assertEqual(added["university"]["ja"], "東京大学工学系研究科")
        self.assertEqual(added["department"]["zh-CN"], "")
        self.assertEqual((self.site / added["poster"]["src"]).read_bytes(), original)
        self.assertNotIn("PRIVATE", json.dumps(honors))
        self.assertNotIn("/work/", json.dumps(honors))
        self.assertEqual(report["added"], 1)
        operation = report["image_operations"][0]
        self.assertTrue(operation["path"].startswith("images/honors/"))
        self.assertEqual(operation["sha256"], hashlib.sha256(original).hexdigest())
        json.dumps(report)

    def test_wrong_original_is_ignored_and_public_preview_used(self):
        self.add_original(picture("green"))
        self.write_feed([self.row])
        honors, _ = self.sync(current=[], source_posters_root=self.posters)
        self.assertEqual((self.site / honors[0]["poster"]["src"]).read_bytes(), (self.source / self.row["image"]).read_bytes())
        self.assertTrue(honors[0]["poster"]["src"].endswith(".webp"))

    def test_unavailable_malformed_empty_sources_keep_published_entries(self):
        for text in (None, "{broken", "[]", '{"items": []}', '{"items": [{"subject": "bio"}]}'):
            with self.subTest(text=text):
                if text is not None:
                    self.feed.write_text(text)
                elif self.feed.exists():
                    self.feed.unlink()
                honors, report = self.sync()
                self.assertEqual(honors, self.current)
                self.assertEqual(report["status"], "source-error")
                self.assertFalse(report["changed"])

    def test_missing_image_keeps_existing_but_valid_other_record_can_import(self):
        second = self.source_row(picture("blue"), "李同学", "京都大学理学研究科", color="blue")
        self.write_feed([self.row, second])
        (self.source / self.row["image"]).unlink()
        honors, report = self.sync()
        self.assertEqual(honors[0], self.current[0])
        self.assertEqual(len(honors), 2)
        self.assertEqual(report["status"], "warning")

    def test_public_image_traversal_and_symlinks_are_rejected(self):
        row = {**self.row, "image": "../../private.png"}
        self.write_feed([row])
        honors, report = self.sync(current=[])
        self.assertEqual(honors, [])
        self.assertEqual(report["warnings"][0]["code"], "unexpected_public_image_path")
        public = self.source / self.row["image"]
        public.unlink()
        public.symlink_to(self.site / "images/existing.png")
        self.write_feed([self.row])
        honors, report = self.sync(current=[])
        self.assertEqual(honors, [])
        self.assertEqual(report["status"], "warning")

    def test_invalid_image_content_does_not_replace_published_record(self):
        self.write_feed([self.row])
        (self.source / self.row["image"]).write_bytes(b"not an image")
        honors, report = self.sync()
        self.assertEqual(honors, self.current)
        self.assertFalse(report["changed"])
        self.assertEqual(report["status"], "warning")

    def test_original_symlink_cannot_leak_unpublished_local_file(self):
        original = self.add_original(self.original)
        original.unlink()
        original.symlink_to(self.site / "images/existing.png")
        self.write_feed([self.row])
        honors, report = self.sync(current=[], source_posters_root=self.posters)
        self.assertTrue(honors[0]["poster"]["src"].endswith(".webp"))
        self.assertEqual(report["status"], "warning")

    def test_duplicate_or_same_surname_ambiguous_records_do_not_overwrite(self):
        for rows in ([self.row, self.row], [self.row, self.source_row(picture("blue"), color="blue")]):
            self.write_feed(rows)
            honors, report = self.sync()
            self.assertEqual(honors, self.current)
            self.assertEqual(report["accepted_count"], 0)
            self.assertIn("duplicate_or_ambiguous_source_records", [warning["code"] for warning in report["warnings"]])

    def test_changed_poster_preserves_id_and_manual_translations(self):
        replacement = picture("blue")
        row = self.source_row(replacement, color="blue")
        self.add_original(replacement)
        self.write_feed([row])
        honors, report = self.sync(source_posters_root=self.posters)
        self.assertEqual(len(honors), 1)
        self.assertEqual(honors[0]["id"], self.current[0]["id"])
        self.assertEqual(honors[0]["department"], self.current[0]["department"])
        self.assertEqual(honors[0]["student"], self.current[0]["student"])
        self.assertEqual((self.site / honors[0]["poster"]["src"]).read_bytes(), replacement)
        self.assertEqual(report["updated"], 1)

    def test_dry_run_produces_plan_without_writes(self):
        self.write_feed([self.row])
        honors, report = self.sync(current=[], dry_run=True)
        self.assertEqual(len(honors), 1)
        self.assertTrue(report["changed"])
        self.assertFalse((self.site / "images/honors").exists())
        self.assertEqual(report["image_operations"][0]["action"], "copy")

    def test_second_run_and_reordered_source_do_not_change_output(self):
        second = self.source_row(picture("blue"), "李同学", "京都大学理学研究科", color="blue")
        self.write_feed([self.row, second])
        honors, _ = self.sync(current=[])
        self.write_feed([second, self.row])
        again, report = self.sync(current=honors)
        self.assertEqual(again, honors)
        self.assertFalse(report["changed"])
        self.assertTrue(all(op["action"] == "verify" for op in report["image_operations"]))

    def test_missing_fields_private_name_or_non_ai_record_cannot_be_imported(self):
        for changes in ({"year": "未分年度"}, {"name": "张三"}, {"university": ""}, {"subject": "bio"}, {"university": "https://private.example/statement"}):
            self.write_feed([{**self.row, **changes}])
            honors, report = self.sync(current=[])
            self.assertEqual(honors, [])
            self.assertNotEqual(report["status"], "ok")

    def test_symlink_destination_does_not_write_outside_website(self):
        external = self.root / "outside"
        external.mkdir()
        (self.site / "images/honors").symlink_to(external, target_is_directory=True)
        self.write_feed([self.row])
        honors, report = self.sync(current=[])
        self.assertEqual(honors, [])
        self.assertEqual(list(external.iterdir()), [])
        self.assertEqual(report["status"], "warning")

    def test_removed_source_entry_does_not_implicitly_delete_published_result(self):
        other = self.source_row(picture("blue"), "李同学", "京都大学理学研究科", color="blue")
        self.write_feed([other])
        honors, _ = self.sync()
        self.assertEqual(honors[0], self.current[0])
        self.assertEqual(len(honors), 2)


if __name__ == "__main__":
    unittest.main()
