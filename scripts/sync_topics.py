#!/usr/bin/env python3
"""Build public topic records from a private, reviewed allowlist.

No source body, path or filename is copied to the public return value. Source
inventory and unreviewed discoveries stay in private files outside this repo.
This module only reads research sources; it never runs research programs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

LANGUAGES = {"zh-CN", "zh-TW", "ja", "en"}
STAGES = {"proposal": 0, "pilot": 1, "practice": 2}
PUBLIC_TOPIC_FIELDS = {"id", "category", "stage", "title", "summary", "tags"}
ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,79}$")
PRIVATE_TEXT = re.compile(
    r"(?:https?://|file://|/(?:home|work|tmp|etc|var)/|```|[<>]|"
    r"\b\d{7,}\b|志望理由[书書]|statement\s+of\s+purpose|"
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.I
)
SOURCE_SUFFIXES = {".md", ".pdf", ".json", ".csv", ".html", ".txt"}
SKIP_DIRS = {
    "data", "datasets", "models", "model", "weights", "checkpoints", "checkpoint",
    "cache", "__pycache__", "node_modules", "venv", "logs", "wandb", "tensorboard",
    "predictions", "submissions", "reviews", "monitor", "archive", "archives",
}
MAX_DEPTH = 6
MAX_FILES = 12000
MAX_READ = 2 * 1024 * 1024
REPOSITORY = Path(__file__).resolve().parents[1]


class TopicSyncError(ValueError):
    """The topic update could not be safely completed."""


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _under(path, parent):
    return path == parent or parent in path.parents


def _private_path(path):
    path = Path(path).absolute()
    if _under(path.resolve(), REPOSITORY):
        raise TopicSyncError("Private configuration and audit files must stay outside the repository")
    if path.is_symlink():
        raise TopicSyncError("Private output paths must not be symlinks")
    return path


def _write_private(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".topic-sync-", delete=False) as handle:
        temporary = Path(handle.name)
        os.chmod(temporary, 0o600)
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)


def _text(value, *, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise TopicSyncError("Public text is missing or exceeds its size limit")
    if any(ord(c) < 32 for c in value) or PRIVATE_TEXT.search(value):
        raise TopicSyncError("Public text contains a disallowed link, identifier or private-content marker")
    return value


def _translations(value, *, limit):
    if not isinstance(value, dict) or set(value) != LANGUAGES:
        raise TopicSyncError("All four reviewed translations are required")
    return {lang: _text(value[lang], limit=limit) for lang in sorted(LANGUAGES)}


def _public_topic(value, category_ids):
    if not isinstance(value, dict) or set(value) != PUBLIC_TOPIC_FIELDS:
        raise TopicSyncError("Topic fields must match the public allowlist exactly")
    if not ID_RE.fullmatch(value["id"]) or value["category"] not in category_ids:
        raise TopicSyncError("Invalid public topic or category identifier")
    if value["stage"] not in STAGES:
        raise TopicSyncError("Invalid topic stage")
    result = {key: value[key] for key in ("id", "category", "stage")}
    result["title"] = _translations(value["title"], limit=120)
    result["summary"] = _translations(value["summary"], limit=360)
    if not isinstance(value["tags"], dict) or set(value["tags"]) != LANGUAGES:
        raise TopicSyncError("All four reviewed tag translations are required")
    result["tags"] = {}
    for lang in sorted(LANGUAGES):
        tags = value["tags"][lang]
        if not isinstance(tags, list) or not 1 <= len(tags) <= 5:
            raise TopicSyncError("A topic requires one to five short tags per language")
        result["tags"][lang] = [_text(tag, limit=55) for tag in tags]
    return result


def _source_path(value, roots):
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise TopicSyncError("Source paths must be absolute")
    # Shared data/model stores are not part of publication inventory, even read-only.
    if _under(path, Path("/work/shared")):
        raise TopicSyncError("Shared stores are excluded from website scanning")
    if not any(_under(path, root) for root in roots):
        raise TopicSyncError("Source path is outside the configured discovery roots")
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise TopicSyncError("Source symlinks are not followed")
        if parent in roots:
            break
    return path


def _metadata(path, anchor):
    stat = path.stat()
    entry = {"path": str(path.relative_to(anchor)), "size": stat.st_size,
             "mtime_ns": stat.st_mtime_ns}
    # Only small review/report documents are hashed. Large files are never read.
    if stat.st_size <= MAX_READ and path.suffix.lower() in {".md", ".json", ".html", ".txt"}:
        entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return entry


def _inventory(source):
    if not source.exists():
        return [], ["source_missing"]
    if source.is_file():
        return [_metadata(source, source.parent)], []
    files, warnings = [], []
    for directory, children, names in os.walk(source, followlinks=False):
        base = Path(directory)
        depth = len(base.relative_to(source).parts)
        children[:] = sorted(name for name in children if not name.startswith(".")
                             and name.lower() not in SKIP_DIRS
                             and not (base / name).is_symlink()) if depth < MAX_DEPTH else []
        for name in sorted(names):
            path = base / name
            if name.startswith(".") or path.is_symlink():
                continue
            if path.suffix.lower() not in SOURCE_SUFFIXES and name != "SUCCESS":
                continue
            # Per-sample predictions may be huge and are not publication evidence.
            if any(word in name.lower() for word in ("prediction", "checkpoint", "weights")):
                continue
            if len(files) >= MAX_FILES:
                raise TopicSyncError("Source inventory exceeds the bounded scan limit")
            files.append(_metadata(path, source))
    return files, warnings


def _metric_evidence(path):
    """Require a real, finite metric value, not just a CSV header or an empty file."""
    if not path.is_file() or path.is_symlink() or not 0 < path.stat().st_size <= MAX_READ:
        return False
    try:
        rows = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig")))
        metric_names = {"r", "rho", "r2", "r²", "pearson", "spearman", "mse", "rmse",
                        "mae", "accuracy", "f1", "auroc", "auc", "loss", "score", "success_rate"}
        columns = [key for key in (rows.fieldnames or [])
                   if key.lower().strip().removeprefix("test_").removeprefix("val_") in metric_names]
        if not columns:
            return False
        for index, row in enumerate(rows):
            if index >= 10000:
                break
            for column in columns:
                try:
                    if math.isfinite(float(row.get(column, ""))):
                        return True
                except (ValueError, TypeError):
                    pass
    except (OSError, UnicodeError, csv.Error):
        return False
    return False


def _practice_evidence(runs_roots):
    """A configured formal run needs a completion marker, report, and metrics."""
    confirmed = []
    for runs_root in runs_roots:
        if not runs_root.is_dir():
            continue
        for run in sorted(runs_root.iterdir()):
            if not run.is_dir() or run.is_symlink() or re.search(
                r"smoke|pilot|preview|dry.?run|test|预演|預演", run.name, re.I
            ):
                continue
            success, summary = run / "SUCCESS", run / "summary.md"
            if not success.is_file() or success.is_symlink():
                continue
            if not summary.is_file() or summary.is_symlink() or not 80 <= summary.stat().st_size <= MAX_READ:
                continue
            if any((run / name).exists() for name in ("FAILED", "FAILURE", "ERROR")):
                continue
            valid_metrics = [run / name for name in ("metrics.csv", "aggregate_metrics.csv")
                             if _metric_evidence(run / name)]
            # A stale completion flag must not validate a run currently being rewritten.
            if valid_metrics and success.stat().st_mtime_ns >= max(
                summary.stat().st_mtime_ns, min(path.stat().st_mtime_ns for path in valid_metrics)
            ):
                confirmed.append(str(run))
    return confirmed


def _discover(roots, sources, excluded, previous, today):
    records = []
    for root in roots:
        for path in sorted(root.iterdir()):
            if path.name.startswith(".") or path.is_symlink() or path in excluded:
                continue
            if not path.is_dir() and path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            if any(_under(source, path) or _under(path, source) for source in sources):
                continue
            prior = previous.get(str(path), {})
            records.append({"path": str(path), "kind": "directory" if path.is_dir() else "file",
                            "firstSeen": prior.get("firstSeen", today), "lastSeen": today,
                            "reason": "No reviewed public mapping; not published"})
    return records


def sync_topics(config_path, state_path, pending_path, *, today=None):
    """Return public categories/topics plus safe operational counts.

    ``config_path`` is a private reviewed configuration. ``state_path`` and
    ``pending_path`` are private audit destinations, never public repo files.
    A missing source root fails the update, preserving the last published data.
    """
    config_path, state_path, pending_path = map(_private_path, (config_path, state_path, pending_path))
    if len({config_path.resolve(), state_path.resolve(), pending_path.resolve()}) != 3:
        raise TopicSyncError("Configuration and audit destinations must be separate")
    today = today or datetime.now(ZoneInfo("Asia/Tokyo")).date().isoformat()
    datetime.strptime(today, "%Y-%m-%d")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schemaVersion") != 1:
        raise TopicSyncError("Unsupported topic configuration schema")
    roots = [Path(path) for path in config["discoveryRoots"]]
    if not roots:
        raise TopicSyncError("At least one discovery root is required")
    for root in roots:
        _source_path(str(root), roots)
        if not root.is_dir():
            raise TopicSyncError("A configured source root is unavailable; publication was preserved")
    categories, category_ids = [], set()
    for category in config["categories"]:
        if set(category) != {"id", "label"} or not ID_RE.fullmatch(category["id"]):
            raise TopicSyncError("Invalid public category")
        if category["id"] in category_ids:
            raise TopicSyncError("Duplicate category identifier")
        category_ids.add(category["id"])
        categories.append({"id": category["id"], "label": _translations(category["label"], limit=70)})
    old_state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    old_topics = old_state.get("topics", {})
    old_pending = json.loads(pending_path.read_text(encoding="utf-8")) if pending_path.exists() else {}
    previous_pending = {item["path"]: item for item in old_pending.get("unmappedSources", [])}
    topics, inventory_state, all_sources, warnings = [], {}, [], []
    changed, ids = False, set()
    for record in config["topics"]:
        if record.get("approved") is not True:
            warnings.append({"reason": "unapproved_configuration_record", "id": record.get("public", {}).get("id")})
            continue
        topic = _public_topic(record["public"], category_ids)
        if topic["id"] in ids:
            raise TopicSyncError("Duplicate topic identifier")
        ids.add(topic["id"])
        reviewed = record["reviewedAt"]
        datetime.strptime(reviewed, "%Y-%m-%d")
        sources = [_source_path(path, roots) for path in record["sources"]]
        if not sources:
            raise TopicSyncError("Each approved topic needs at least one reviewed source")
        all_sources.extend(sources)
        inventory = []
        for source in sources:
            files, source_warnings = _inventory(source)
            inventory.append({"source": str(source), "files": files})
            warnings.extend({"topic": topic["id"], "source": str(source), "reason": warning}
                            for warning in source_warnings)
        source_fingerprint = _digest(inventory)
        public_fingerprint = _digest(topic)
        prior = old_topics.get(topic["id"], {})
        source_changed = bool(prior) and prior.get("sourceFingerprint") != source_fingerprint
        public_changed = bool(prior) and prior.get("publicFingerprint") != public_fingerprint
        floor = max((topic["stage"], prior.get("stage", topic["stage"])), key=STAGES.__getitem__)
        runs_roots = [_source_path(path, roots) for path in record.get("practiceRunRoots", [])]
        if any(not any(_under(path, source) for source in sources) for path in runs_roots):
            raise TopicSyncError("Practice evidence must be inside the topic's reviewed sources")
        practice = _practice_evidence(runs_roots)
        topic["stage"] = "practice" if practice else floor
        stage_changed = topic["stage"] != prior.get("stage", record["public"]["stage"])
        topic["updatedAt"] = today if source_changed or public_changed or stage_changed else prior.get("updatedAt", reviewed)
        changed = changed or source_changed or public_changed or stage_changed or not prior
        topics.append(topic)
        inventory_state[topic["id"]] = {
            "sourceFingerprint": source_fingerprint, "publicFingerprint": public_fingerprint,
            "stage": topic["stage"], "updatedAt": topic["updatedAt"],
            "sources": inventory, "confirmedPracticeRuns": practice,
        }
    if not topics:
        raise TopicSyncError("No approved topics are available; publication was preserved")
    if set(old_topics) - ids:
        raise TopicSyncError("Removing previously published topics requires an explicit reviewed migration")
    excluded = {_source_path(item["path"], roots) for item in config.get("excludedSources", [])}
    pending = _discover(roots, all_sources, excluded, previous_pending, today)
    counts = {stage: sum(topic["stage"] == stage for topic in topics) for stage in STAGES}
    _write_private(pending_path, {"schemaVersion": 1, "checkedAt": today,
                                 "unmappedSources": pending, "warnings": warnings})
    _write_private(state_path, {"schemaVersion": 1, "checkedAt": today, "topics": inventory_state})
    return {"categories": categories, "topics": topics, "sourceChanged": changed,
            "counts": counts, "pendingCount": len(pending), "warningCount": len(warnings),
            "warnings": sorted({item["reason"] for item in warnings})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--pending", required=True)
    parser.add_argument("--public-output", help="Optional public categories/topics JSON destination")
    args = parser.parse_args()
    result = sync_topics(args.config, args.state, args.pending)
    if args.public_output:
        destination = Path(args.public_output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps({key: result[key] for key in ("categories", "topics")},
                                          ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("sourceChanged", "counts", "pendingCount", "warningCount")}))


if __name__ == "__main__":
    main()
