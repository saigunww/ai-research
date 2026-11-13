"""Import AI admission posters from the already-public admissions catalog.

Only ``subject == 'ai-research'`` is considered. The source catalog is the
publication boundary: this module does not parse student spreadsheets, proposals,
statements, or arbitrary local documents. Local originals are optional and used
only when their bytes match an approved public record's SHA-256 exactly.

``build_honors`` returns ``(honors, report)``. The caller owns catalog writes,
private reports, validation, and publication. Missing/bad sources never remove
previously published entries. Pillow is required to validate image content.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import unicodedata

from PIL import Image


LANGUAGES = ("zh-CN", "zh-TW", "ja", "en")
MAX_IMAGE_BYTES = 40 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
COMPOUND_SURNAMES = frozenset(("欧阳", "歐陽", "司马", "司馬", "上官", "诸葛", "諸葛", "司徒", "司空", "东方", "東方", "皇甫", "夏侯", "南宫", "南宮", "慕容", "宇文", "令狐", "长孙", "長孫", "尉迟", "尉遲", "公孙", "公孫", "端木"))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative_file(root: Path, relative: str, prefix: str) -> Path:
    """Accept only a regular, non-symlink file contained in a specific subtree."""
    if not isinstance(relative, str) or "\\" in relative or "\x00" in relative:
        raise ValueError("unsafe_path")
    parts = PurePosixPath(relative).parts
    if not parts or PurePosixPath(relative).is_absolute() or any(p in (".", "..") for p in parts):
        raise ValueError("unsafe_path")
    if not relative.startswith(prefix + "/"):
        raise ValueError("unsafe_path")
    path = root.joinpath(*parts)
    boundary = root.resolve()
    path.resolve().relative_to(boundary)
    for parent in [path, *path.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError("symlink_source")
    if not path.is_file():
        raise ValueError("missing_image")
    return path


def _image(path: Path) -> tuple[bytes, int, int, str]:
    if path.suffix.lower() not in IMAGE_EXTENSIONS or path.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError("invalid_image")
    data = path.read_bytes()
    with Image.open(io.BytesIO(data)) as image:
        width, height = image.size
        if not width or not height or width * height > MAX_IMAGE_PIXELS or image.format not in ("PNG", "JPEG", "WEBP"):
            raise ValueError("invalid_image")
        actual_extension = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}[image.format]
        if path.suffix.lower() not in ({".jpg", ".jpeg"} if image.format == "JPEG" else {actual_extension}):
            raise ValueError("image_extension_mismatch")
        image.verify()
    return data, width, height, actual_extension


def _normalize(value: str) -> str:
    return re.sub(r"[\s・·／/|｜()（）,，.。_-]", "", unicodedata.normalize("NFKC", value)).casefold()


def _public_name(value: str) -> tuple[str, dict[str, str]]:
    # Never export a full student name, even if an upstream filename contains it.
    if not isinstance(value, str) or not re.fullmatch(r"[\u3400-\u9fff]{1,8}同[学學]", value):
        raise ValueError("unrecognized_student_alias")
    surname = value[:2] if value[:2] in COMPOUND_SURNAMES else value[:1]
    return surname, {"zh-CN": surname + "同学", "zh-TW": surname + "同學", "ja": surname + "さん", "en": "Student " + surname}


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 180 or any(ord(c) < 32 for c in value) or re.search(r"[<>]|https?://|[/\\](?:home|work|tmp)/", value):
        raise ValueError("invalid_public_text")
    return value.strip()


def _record(row: object) -> dict:
    if not isinstance(row, dict) or row.get("subject") != "ai-research":
        raise ValueError("invalid_record")
    source_id = row.get("id")
    if not isinstance(source_id, str) or not re.fullmatch(r"[a-f0-9]{64}", source_id):
        raise ValueError("invalid_source_id")
    year = str(row.get("year", ""))
    if not re.fullmatch(r"20\d{2}", year):
        raise ValueError("missing_admission_year")
    surname, student = _public_name(row.get("name"))
    university = _text(row.get("university"))
    if not any(word in university for word in ("大学", "大學", "University", "Institute", "College")):
        raise ValueError("unrecognized_university")
    expected_image = "assets/honors/" + source_id[:24] + ".webp"
    if row.get("image") != expected_image:
        raise ValueError("unexpected_public_image_path")
    return {"source_id": source_id, "year": int(year), "surname": surname, "student": student, "university": university, "image": expected_image}


def _existing_keys(honor: dict) -> set[tuple[int, str, str]]:
    keys = set()
    student = honor.get("student", {}).get("zh-CN", "")
    try:
        surname, _ = _public_name(student)
        year = int(honor["year"])
    except (ValueError, KeyError, TypeError):
        return keys
    for language in LANGUAGES:
        university = honor.get("university", {}).get(language, "")
        school = honor.get("school", {}).get(language, "")
        if university:
            keys.add((year, surname, _normalize(university + school)))
            if not school:
                keys.add((year, surname, _normalize(university)))
    return keys


def _originals(root: Path | None, requested: set[str], warn) -> dict[str, Path]:
    originals = {}
    if root is None or not root.is_dir():
        return originals
    # No recursive search through private student or research directories.
    for path in sorted(root.glob("20[0-9][0-9]年度/AI科研背景提升/*")):
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        try:
            relative = path.relative_to(root).as_posix()
            path = _relative_file(root, relative, relative.split("/")[0] + "/AI科研背景提升")
            if path.stat().st_size > MAX_IMAGE_BYTES:
                continue
            digest = _sha(path.read_bytes())
            if digest in requested:
                originals.setdefault(digest, path)
        except (OSError, ValueError):
            warn("unreadable_original")
    return originals


def _new_honor(row: dict) -> dict:
    # Keep the upstream original university/faculty label. Do not invent a
    # department, English translation, or undergraduate/graduate distinction.
    label = {language: row["university"] for language in LANGUAGES}
    empty = {language: "" for language in LANGUAGES}
    return {
        "id": "ai-admission-" + row["source_id"][:20],
        "year": row["year"], "student": row["student"],
        "university": label, "school": empty.copy(), "department": empty.copy(),
        "program": {"zh-CN": "科研背景提升", "zh-TW": "科研背景提升", "ja": "研究実践プログラム", "en": "Research Program"},
    }


def build_honors(
    source_json: Path,
    source_images_root: Path,
    current_honors: list,
    destination_images: Path,
    dry_run: bool = False,
    *,
    source_posters_root: Path | None = None,
) -> tuple[list, dict]:
    """Merge public AI outcomes, retaining previous entries on every failure.

    ``source_images_root`` is the university site's repository root.
    ``destination_images`` is the AI site's ``images`` directory (the
    ``images/honors`` subdirectory is also accepted for direct module use).
    ``source_posters_root`` optionally points to the local acceptance root.
    Planned image operations are returned in dry-run mode without writing files.
    Reports belong in private automation state, never in the public catalog.
    """
    source_json, source_images_root, destination_images = map(Path, (source_json, source_images_root, destination_images))
    source_posters_root = Path(source_posters_root) if source_posters_root is not None else None
    if destination_images.name == "images":
        destination_images = destination_images / "honors"
    if destination_images.name != "honors" or destination_images.parent.name != "images":
        raise ValueError("destination_images must end in images or images/honors")
    if not isinstance(current_honors, list):
        raise ValueError("current_honors must be a list")
    current = deepcopy(current_honors)
    result = deepcopy(current_honors)
    report = {"status": "ok", "source_count": 0, "accepted_count": 0, "added": 0, "updated": 0, "changed": False, "dry_run": dry_run, "image_operations": [], "warnings": []}

    def warn(code: str, row: int | None = None):
        item = {"code": code}
        if row is not None:
            item["row"] = row
        report["warnings"].append(item)

    try:
        source = json.loads(source_json.read_text(encoding="utf-8"))
        if not isinstance(source, dict) or not isinstance(source.get("items"), list):
            raise ValueError("invalid_catalog")
        candidates = [(index, row) for index, row in enumerate(source["items"]) if isinstance(row, dict) and row.get("subject") == "ai-research"]
        report["source_count"] = len(candidates)
        if not candidates:
            raise ValueError("empty_ai_catalog")
    except (OSError, UnicodeError, ValueError):
        warn("source_unavailable_or_empty")
        report["status"] = "source-error"
        return current, report

    rows = []
    for index, raw in candidates:
        try:
            row = _record(raw)
            row["row_index"] = index
            rows.append(row)
        except (ValueError, TypeError) as error:
            warn(str(error) if isinstance(error, ValueError) else "invalid_record", index)

    # Repeated source records or ambiguous identity pairs must not produce new
    # duplicate cards or overwrite one another in a partially corrupt catalog.
    by_id: dict[str, list] = {}
    by_identity: dict[tuple, list] = {}
    for row in rows:
        by_id.setdefault(row["source_id"], []).append(row)
        by_identity.setdefault((row["year"], row["surname"], _normalize(row["university"])), []).append(row)
    rows = [row for row in rows if len(by_id[row["source_id"]]) == 1 and len(by_identity[(row["year"], row["surname"], _normalize(row["university"]))]) == 1]
    if len(rows) < sum(len(v) for v in by_id.values()):
        warn("duplicate_or_ambiguous_source_records")

    website_root = destination_images.parent.parent
    current_images = {}
    for index, honor in enumerate(current):
        if not isinstance(honor, dict):
            continue
        try:
            path = _relative_file(website_root, honor.get("poster", {}).get("src"), "images")
            content = _image(path)
            current_images[index] = (path, content, _sha(content[0]))
        except (OSError, ValueError, TypeError, SyntaxError, Image.DecompressionBombError):
            pass
    originals = _originals(source_posters_root, {row["source_id"] for row in rows}, warn)

    for row in sorted(rows, key=lambda r: (-r["year"], r["university"], r["surname"], r["source_id"])):
        identity = (row["year"], row["surname"], _normalize(row["university"]))
        matches = {index for index, honor in enumerate(current) if isinstance(honor, dict) and identity in _existing_keys(honor)}
        matches.update(index for index, image in current_images.items() if image[2] == row["source_id"])
        matches.update(index for index, honor in enumerate(current) if isinstance(honor, dict) and honor.get("id") == "ai-admission-" + row["source_id"][:20])
        if len(matches) > 1:
            warn("ambiguous_existing_match", row["row_index"])
            continue
        match = next(iter(matches)) if matches else None
        try:
            # Require the referenced public image even if a local original exists:
            # a partially completed upstream export must not be published here.
            public_path = _relative_file(source_images_root, row["image"], "assets/honors")
            public_image = _image(public_path)
            if match in current_images and current_images[match][2] == row["source_id"]:
                # Preserve the two approved full-resolution images and translations.
                report["accepted_count"] += 1
                continue
            image = _image(originals[row["source_id"]]) if row["source_id"] in originals else public_image
            content, width, height, extension = image
            digest = _sha(content)
            relative = "images/honors/" + digest + extension
            target = website_root / relative
            if destination_images.is_symlink() or destination_images.parent.is_symlink() or target.is_symlink():
                raise ValueError("symlink_destination")
            target.resolve().relative_to(website_root.resolve())
            needs_copy = not target.exists() or _sha(target.read_bytes()) != digest
            if target.exists() and needs_copy:
                raise ValueError("content_addressed_file_conflict")
            operation = {"action": "copy" if needs_copy else "verify", "path": relative, "sha256": digest, "size": len(content)}
            if needs_copy and not dry_run:
                destination_images.mkdir(parents=True, exist_ok=True)
                descriptor, temporary = tempfile.mkstemp(prefix=".poster-", dir=destination_images)
                try:
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write(content)
                    os.replace(temporary, target)
                finally:
                    if os.path.exists(temporary):
                        os.unlink(temporary)
            report["image_operations"].append(operation)
            honor = deepcopy(current[match]) if match is not None else _new_honor(row)
            honor["poster"] = {"src": relative, "width": width, "height": height}
            if match is None:
                result.append(honor)
                report["added"] += 1
            elif honor != result[match]:
                result[match] = honor
                report["updated"] += 1
            report["accepted_count"] += 1
        except (OSError, ValueError, TypeError, SyntaxError, Image.DecompressionBombError) as error:
            code = str(error) if isinstance(error, ValueError) and re.fullmatch(r"[a-z_]+", str(error)) else "image_unavailable_or_invalid"
            warn(code, row["row_index"])

    report["changed"] = result != current
    if report["warnings"]:
        report["status"] = "warning"
    return result, report
