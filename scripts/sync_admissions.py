#!/usr/bin/env python3
"""Monitor reviewed university sources without publishing scraped page content.

Install-free runtime: the site's existing Python environment supplies urllib3
and BeautifulSoup; PDF extraction uses the system pdftotext executable.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import ssl
import subprocess
import tempfile
import unicodedata
from urllib.parse import urljoin, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, Comment
import urllib3

LANGUAGES = {"zh-CN", "zh-TW", "ja", "en"}
LEVELS = {"undergraduate", "graduate"}
STATUSES = {"verified", "changed", "unavailable"}
TRANSLATED_FIELDS = {"university", "program", "route", "scope", "summary"}
ITEM_FIELDS = {"id", "level", "academicYear", "sourceUrl", "verifiedAt", "checkedAt", "status", "tags"} | TRANSLATED_FIELDS
MAX_BYTES = 8 * 1024 * 1024
MAX_TEXT_BYTES = 16 * 1024 * 1024
REPOSITORY = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,100}$")
DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+ac\.jp$")
REVIEWED_OFFICIAL_HOSTS = {"www.waseda.jp"}
PRIVATE_TEXT = re.compile(r"(?:/(?:home|work|tmp|etc|var)/|https?://|file://|```|[<>]|\b\d{8,}\b)", re.I)


class AdmissionsSyncError(ValueError):
    pass


class FetchError(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise AdmissionsSyncError("Dates must use YYYY-MM-DD")
    datetime.strptime(value, "%Y-%m-%d")
    return value


def _timestamp(value):
    if not isinstance(value, str):
        raise AdmissionsSyncError("A timezone-aware check timestamp is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise AdmissionsSyncError("A timezone-aware check timestamp is required")
    return parsed


def _text(value, limit=1600):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise AdmissionsSyncError("Invalid or oversized public text")
    if any(ord(c) < 32 for c in value) or PRIVATE_TEXT.search(value):
        raise AdmissionsSyncError("Private paths, markup, and identifiers are not public content")
    return value


def _translations(value, limit=1600):
    if not isinstance(value, dict) or set(value) != LANGUAGES:
        raise AdmissionsSyncError("All four reviewed translations are required")
    return {lang: _text(value[lang], limit) for lang in sorted(LANGUAGES)}


def validate_official_url(url):
    """Syntax-only validation; DNS validation is repeated for every actual hop."""
    if not isinstance(url, str) or len(url) > 2048 or any(c.isspace() or ord(c) < 32 for c in url):
        raise AdmissionsSyncError("Invalid official URL")
    parts = urlsplit(url)
    try:
        valid = (parts.scheme == "https" and parts.username is None and parts.password is None
                 and parts.port in (None, 443) and parts.hostname
                 and (DOMAIN_RE.fullmatch(parts.hostname.lower())
                      or parts.hostname.lower() in REVIEWED_OFFICIAL_HOSTS))
    except ValueError as exc:
        raise AdmissionsSyncError("Invalid official URL") from exc
    if not valid:
        raise AdmissionsSyncError("Only reviewed HTTPS university domains on port 443 are allowed")
    return url


def _fetch_url(url):
    validate_official_url(url)
    parts = urlsplit(url)
    return urlunsplit(("https", parts.hostname.lower(), parts.path or "/", parts.query, ""))


def _validate_item(item):
    if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
        raise AdmissionsSyncError("Admission fields must match the public allowlist exactly")
    if not isinstance(item["id"], str) or not ID_RE.fullmatch(item["id"]):
        raise AdmissionsSyncError("Invalid admission identifier")
    if item["level"] not in LEVELS or item["status"] not in STATUSES:
        raise AdmissionsSyncError("Invalid admission level or status")
    result = {field: item[field] for field in ("id", "level", "status")}
    for field in TRANSLATED_FIELDS:
        result[field] = _translations(item[field], 1600 if field in {"scope", "summary"} else 300)
    result["academicYear"] = _text(item["academicYear"], 100)
    result["sourceUrl"] = validate_official_url(item["sourceUrl"])
    result["verifiedAt"] = _date(item["verifiedAt"])
    _timestamp(item["checkedAt"])
    result["checkedAt"] = item["checkedAt"]
    if not isinstance(item["tags"], dict) or set(item["tags"]) != LANGUAGES:
        raise AdmissionsSyncError("All four reviewed tag translations are required")
    result["tags"] = {}
    for lang in sorted(LANGUAGES):
        tags = item["tags"][lang]
        if not isinstance(tags, list) or len(tags) > 8:
            raise AdmissionsSyncError("Invalid public tags")
        result["tags"][lang] = [_text(tag, 80) for tag in tags]
    return result


def validate_feed(feed):
    """Validate and return a fresh public-only feed, or fail closed."""
    if not isinstance(feed, dict) or set(feed) != {"updatedAt", "checkedAt", "items"}:
        raise AdmissionsSyncError("Feed fields must match the public allowlist exactly")
    _date(feed["updatedAt"])
    _timestamp(feed["checkedAt"])
    if not isinstance(feed["items"], list) or not 1 <= len(feed["items"]) <= 100:
        raise AdmissionsSyncError("An admissions feed must contain one to 100 reviewed items")
    items = [_validate_item(item) for item in feed["items"]]
    if len({item["id"] for item in items}) != len(items):
        raise AdmissionsSyncError("Duplicate admission identifier")
    return {"updatedAt": feed["updatedAt"], "checkedAt": feed["checkedAt"], "items": items}


def _public_addresses(hostname):
    try:
        records = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise FetchError("dns_failed") from exc
    addresses = sorted({record[4][0] for record in records})
    if not addresses:
        raise FetchError("dns_failed")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise FetchError("nonpublic_address_blocked")
    # Prefer IPv4 for hosts without working IPv6 connectivity. All answers were checked.
    return sorted(addresses, key=lambda address: (":" in address, address))


def _open_https(address, hostname, target):
    """Connect to the validated IP, while verifying TLS for the university name."""
    pool = urllib3.HTTPSConnectionPool(
        address, port=443, server_hostname=hostname, assert_hostname=hostname,
        ssl_context=ssl.create_default_context(), cert_reqs="CERT_REQUIRED",
        timeout=urllib3.Timeout(connect=10, read=30, total=30), retries=False,
    )
    try:
        response = pool.urlopen("GET", target, headers={
            "Host": hostname, "User-Agent": "CoachAcademy-PublicAdmissionsMonitor/1.0",
            "Accept": "text/html,application/pdf", "Accept-Encoding": "identity",
        }, preload_content=False, redirect=False, retries=False)
        return response, pool
    except Exception:
        pool.close()
        raise


def _normalize_text(text):
    return " ".join(unicodedata.normalize("NFKC", text).split())


def _html_text(body):
    soup = BeautifulSoup(body, "html.parser")
    for element in soup.select("script, style, nav, header, footer, noscript, svg"):
        element.decompose()
    for comment in soup.find_all(string=lambda node: isinstance(node, Comment)):
        comment.extract()
    return _normalize_text(soup.get_text(" ", strip=True))


def _pdf_text(body):
    executable = shutil.which("pdftotext")
    if not executable:
        raise FetchError("pdf_extractor_unavailable")
    with tempfile.TemporaryDirectory(prefix="admissions-pdf-") as temporary:
        source, output = Path(temporary) / "source.pdf", Path(temporary) / "text.txt"
        source.write_bytes(body)
        try:
            result = subprocess.run([executable, "-enc", "UTF-8", str(source), str(output)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    timeout=30, check=False)
        except subprocess.TimeoutExpired as exc:
            raise FetchError("pdf_extraction_timeout") from exc
        if result.returncode or not output.exists() or output.stat().st_size > MAX_TEXT_BYTES:
            raise FetchError("pdf_extraction_failed")
        return _normalize_text(output.read_text(encoding="utf-8", errors="replace"))


def fetch_document(url):
    """Fetch bounded official content; text stays in memory for keyword checks."""
    current = _fetch_url(url)
    for redirect in range(6):
        try:
            parts = urlsplit(current)
            addresses = _public_addresses(parts.hostname)
            target = urlunsplit(("", "", parts.path or "/", parts.query, ""))
            response, pool = _open_https(addresses[0], parts.hostname, target)
        except FetchError:
            raise
        except Exception as exc:
            raise FetchError("connection_failed") from exc
        try:
            if response.status in {301, 302, 303, 307, 308}:
                location = response.headers.get("Location")
                if not location or redirect == 5:
                    raise FetchError("redirect_failed")
                try:
                    current = _fetch_url(urljoin(current, location))
                except AdmissionsSyncError as exc:
                    raise FetchError("redirect_domain_blocked") from exc
                continue
            if response.status != 200:
                raise FetchError("http_unavailable")
            try:
                length = int(response.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length > MAX_BYTES:
                raise FetchError("document_too_large")
            chunks, size = [], 0
            while True:
                chunk = response.read(65536, decode_content=True)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_BYTES:
                    raise FetchError("document_too_large")
                chunks.append(chunk)
            body = b"".join(chunks)
            content_type = response.headers.get("Content-Type", "").lower()
        except FetchError:
            raise
        except Exception as exc:
            raise FetchError("read_failed") from exc
        finally:
            response.close()
            pool.close()
        if body.startswith(b"%PDF-") or "application/pdf" in content_type:
            text, kind = _pdf_text(body), "pdf"
        elif "text/html" in content_type or body.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            text, kind = _html_text(body), "html"
        else:
            raise FetchError("unsupported_document")
        if len(text) < 50:
            raise FetchError("insufficient_public_text")
        if re.search(r"access denied|just a moment|verify you are human", text, re.I) or (
            len(text) < 1000 and re.search(r"captcha", text, re.I)
        ):
            raise FetchError("verification_page")
        return {"sha256": _sha(text), "finalUrl": current, "kind": kind, "bytes": size, "text": text}
    raise FetchError("redirect_failed")


def _private_path(value):
    path = Path(value).absolute()
    if REPOSITORY == path.resolve() or REPOSITORY in path.resolve().parents or path.is_symlink():
        raise AdmissionsSyncError("Private configuration and hashes must stay outside the repository")
    return path


def _write_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".admissions-", delete=False) as handle:
        temporary = Path(handle.name)
        os.chmod(temporary, 0o600)
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)


def build_admissions(config_path, state_path, current_feed=None, checked_at=None):
    """Check reviewed sources, returning a public feed and operational report.

    A changed document stays changed until the reviewed configuration revision
    changes. A failed check never establishes a baseline or accepts a revision.
    """
    if checked_at is None:
        checked_at = datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds")
    today = _timestamp(checked_at).astimezone(ZoneInfo("Asia/Tokyo")).date().isoformat()
    config_path, state_path = _private_path(config_path), _private_path(state_path)
    if config_path.resolve() == state_path.resolve():
        raise AdmissionsSyncError("Configuration and state destinations must be separate")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not isinstance(config.get("items"), list) or not 1 <= len(config["items"]) <= 100:
        raise AdmissionsSyncError("One to 100 reviewed admissions entries are required")
    previous_feed = validate_feed(current_feed) if current_feed is not None else None
    previous_items = {item["id"]: item for item in previous_feed["items"]} if previous_feed else {}
    old = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"items": {}}
    entries, all_urls, seen = [], set(), set()
    for record in config["items"]:
        if not isinstance(record, dict) or set(record) - {"public", "revision", "monitorUrls", "requiredTerms"}:
            raise AdmissionsSyncError("Invalid reviewed configuration fields")
        public = dict(record["public"])
        public.setdefault("status", "verified")
        public.setdefault("checkedAt", checked_at)
        public = _validate_item(public)
        identifier = public["id"]
        if identifier in seen:
            raise AdmissionsSyncError("Duplicate admission identifier")
        seen.add(identifier)
        revision = _text(record["revision"], 100)
        urls = record.get("monitorUrls", [public["sourceUrl"]])
        if not isinstance(urls, list) or not 1 <= len(urls) <= 3:
            raise AdmissionsSyncError("Each entry may monitor one to three official URLs")
        urls = sorted({_fetch_url(url) for url in urls})
        all_urls.update(urls)
        required_terms = record.get("requiredTerms", [])
        if not isinstance(required_terms, list) or len(required_terms) > 20:
            raise AdmissionsSyncError("Required source terms must be a short private list")
        required_terms = [_normalize_text(_text(term, 100)).casefold() for term in required_terms]
        public_fingerprint = _sha(_canonical({key: value for key, value in public.items() if key not in {"checkedAt", "status"}}))
        prior = old.get("items", {}).get(identifier, {})
        if prior.get("revision") == revision and prior.get("publicFingerprint") not in {None, public_fingerprint}:
            raise AdmissionsSyncError("Reviewed summary changes require a new configuration revision")
        entries.append((public, revision, urls, public_fingerprint, prior, required_terms))
    fetched, failures = {}, {}
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="admissions") as executor:
        tasks = {executor.submit(fetch_document, url): url for url in sorted(all_urls)}
        for future in as_completed(tasks):
            url = tasks[future]
            try:
                fetched[url] = future.result()
            except FetchError as exc:
                failures[url] = exc.code
            except Exception:
                failures[url] = "source_check_failed"
    items, state_items, errors = [], {}, []
    for public, revision, urls, fingerprint, prior, required_terms in entries:
        identifier = public["id"]
        item = dict(public)
        item["checkedAt"] = checked_at
        state = dict(prior)
        state["checkedAt"] = checked_at
        entry_failures = [{"url": url, "code": failures[url]} for url in urls if url in failures]
        if not entry_failures and required_terms:
            combined = " ".join(fetched[url].get("text", "") for url in urls).casefold()
            if any(term not in combined for term in required_terms):
                entry_failures.append({"url": public["sourceUrl"], "code": "required_text_missing"})
        if entry_failures:
            if identifier in previous_items:
                item = dict(previous_items[identifier])
                item["checkedAt"] = checked_at
            item["status"] = "unavailable"
            state["status"] = "unavailable"
            state["errors"] = entry_failures
            errors.extend({"id": identifier, "code": failure["code"]} for failure in entry_failures)
        else:
            observations = [{"url": url, "sha256": fetched[url]["sha256"],
                             "finalUrl": fetched[url]["finalUrl"]} for url in urls]
            observed = _sha(_canonical(observations))
            if prior.get("revision") != revision or not prior.get("baselineSha256"):
                state = {"revision": revision, "publicFingerprint": fingerprint,
                         "baselineSha256": observed, "baselineVerifiedAt": public["verifiedAt"]}
            unchanged = state["baselineSha256"] == observed
            item["status"] = "verified" if unchanged else "changed"
            state.update({"checkedAt": checked_at, "status": item["status"],
                          "lastObservedSha256": observed, "observations": observations})
            state.pop("errors", None)
        items.append(item)
        state_items[identifier] = state
    feed = validate_feed({"updatedAt": today, "checkedAt": checked_at, "items": items})
    _write_state(state_path, {"schemaVersion": 1, "checkedAt": checked_at, "items": state_items})
    report = {"checkedAt": checked_at, "items": len(items), "urls": len(all_urls),
              "counts": {status: sum(item["status"] == status for item in items) for status in sorted(STATUSES)},
              "errors": errors}
    return feed, report
