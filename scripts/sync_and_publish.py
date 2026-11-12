"""Refresh only approved public overviews and AI admissions, then publish safely."""
from __future__ import annotations

import argparse
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
from zoneinfo import ZoneInfo

from PIL import Image
from sync_honors import build_honors
from sync_topics import sync_topics
from sync_admissions import build_admissions, validate_feed

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
STATE = BASE / '自动更新'
MIRROR = BASE / '网页设计'
LANGUAGES = {'zh-CN', 'zh-TW', 'ja', 'en'}
PREFIX = 'Auto-update AI research catalog '
CATALOG = 'data/catalog.json'
ADMISSIONS = 'data/admissions.json'
PRIVATE_TEXT = re.compile(r'/home/|/work/|file://|志望理由|志望動機|statement\s+of\s+purpose|\.private\b', re.I)


def now():
    return datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def safe_path(root, relative):
    part = PurePosixPath(relative)
    if part.is_absolute() or not part.parts or '..' in part.parts or '\\' in relative:
        raise ValueError('Unsafe relative destination')
    path = root / relative
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('Refusing symbolic-link destination')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Destination outside root')
    return path


def atomic_write(path, content):
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('Refusing symbolic-link write')
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save(path, value):
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def text(value, max_length=800):
    if not isinstance(value, str) or len(value) > max_length or PRIVATE_TEXT.search(value):
        raise ValueError('Invalid or private public text')
    if any(ord(character) < 32 for character in value):
        raise ValueError('Control characters in public text')


def localized(value, tags=False):
    if not isinstance(value, dict) or set(value) != LANGUAGES:
        raise ValueError('Expected four-language public text')
    for content in value.values():
        if tags:
            if not isinstance(content, list) or len(content) > 8:
                raise ValueError('Invalid public tags')
            for tag in content:
                text(tag, 80)
        else:
            text(content)


def validate_catalog(data, root):
    """Strict whitelist: never publish private source records or arbitrary links."""
    if set(data) != {'updatedAt', 'categories', 'topics', 'honors'}:
        raise ValueError('Unexpected catalog fields')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['updatedAt']):
        raise ValueError('Invalid update date')
    if not data['categories'] or not data['topics']:
        raise ValueError('Refusing empty research catalog')
    for collection in ('categories', 'topics', 'honors'):
        if not isinstance(data[collection], list) or len(data[collection]) > 1000:
            raise ValueError('Invalid catalog collection')
        ids = [entry.get('id') for entry in data[collection]]
        if any(not isinstance(key, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,127}', key) for key in ids) or len(set(ids)) != len(ids):
            raise ValueError('Invalid or duplicate public identifiers')
    categories = {entry['id'] for entry in data['categories']}
    for entry in data['categories']:
        if set(entry) != {'id', 'label'}:
            raise ValueError('Unexpected category fields')
        localized(entry['label'])
    for topic in data['topics']:
        if set(topic) - {'id', 'category', 'stage', 'title', 'summary', 'tags', 'updatedAt'}:
            raise ValueError('Unexpected topic fields')
        if topic['category'] not in categories or topic['stage'] not in {'practice', 'pilot', 'proposal'}:
            raise ValueError('Invalid topic category or stage')
        for field in ('title', 'summary'):
            localized(topic[field])
        localized(topic['tags'], tags=True)
        if 'updatedAt' in topic and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', topic['updatedAt']):
            raise ValueError('Invalid topic update date')
    for honor in data['honors']:
        if set(honor) != {'id', 'year', 'student', 'university', 'school', 'department', 'program', 'poster'}:
            raise ValueError('Unexpected admission fields')
        if not isinstance(honor['year'], int) or not 2000 <= honor['year'] <= 2100:
            raise ValueError('Invalid admission year')
        for field in ('student', 'university', 'school', 'department', 'program'):
            localized(honor[field])
        if not re.fullmatch(r'[\u3400-\u9fff]{1,2}同学', honor['student']['zh-CN']):
            raise ValueError('Student must use an anonymous display name')
        poster = honor['poster']
        if set(poster) != {'src', 'width', 'height'}:
            raise ValueError('Unexpected poster fields')
        if not re.fullmatch(r'images/(?:honors/[a-zA-Z0-9_-]+|he-(?:doshisha|ritsumeikan)-2027)\.(?:png|jpe?g|webp)', poster['src']):
            raise ValueError('Poster path outside public asset whitelist')
        image = safe_path(root, poster['src'])
        if not image.is_file() or image.stat().st_size > 25 * 1024 * 1024:
            raise ValueError('Missing or oversized poster')
        with Image.open(image) as opened:
            if opened.format not in {'PNG', 'JPEG', 'WEBP'} or opened.size != (poster['width'], poster['height']):
                raise ValueError('Invalid poster content or dimensions')
            opened.verify()


def generated(path):
    return path in {CATALOG, ADMISSIONS} or bool(re.fullmatch(r'images/honors/[a-zA-Z0-9_-]+\.(?:png|jpe?g|webp)', path))


def git(*args, check=True):
    result = subprocess.run(['git', *args], cwd=ROOT, check=check, capture_output=True, text=True, timeout=180)
    return result.stdout.strip() if check else result


def assert_clean():
    if git('status', '--porcelain'):
        raise RuntimeError('Local changes exist; preserving them and skipping automatic publication')


def pending_commits():
    commits = git('rev-list', 'origin/main..HEAD').splitlines()
    receipts_path = STATE / 'publisher_commits.private.json'
    receipts = load(receipts_path) if receipts_path.exists() else {}
    for commit in commits:
        if commit not in receipts or receipts[commit].get('tree') != git('rev-parse', commit + '^{tree}'):
            raise RuntimeError('Pending commit lacks a local publisher receipt; automatic publication paused')
        if not git('show', '-s', '--format=%s', commit).startswith(PREFIX):
            raise RuntimeError('Unpublished manual commit; automatic publication paused')
        paths = git('diff-tree', '--no-commit-id', '--name-only', '-r', commit).splitlines()
        if not paths or any(not generated(path) for path in paths):
            raise RuntimeError('Pending commit contains changes outside generated data')
    return commits


def integrate_remote():
    assert_clean()
    if git('branch', '--show-current') != 'main':
        raise RuntimeError('Automatic publication requires main branch')
    git('fetch', 'origin', 'main')
    ahead = pending_commits()
    behind = git('rev-list', 'HEAD..origin/main').splitlines()
    if ahead and behind:
        # No automatic reset, rebase or forced push over a changed remote.
        raise RuntimeError('Remote changed while a feed commit is pending; manual reconciliation required')
    if behind:
        git('merge', '--ff-only', 'origin/main')


def mirror(commit):
    allowed_files = {'index.html', 'ai-research.html', 'campus.html', 'README.md', CATALOG, ADMISSIONS, 'assets/site.css', 'assets/site.js'}
    for name in git('ls-tree', '-r', '--name-only', commit).splitlines():
        if name not in allowed_files and not name.startswith('images/'):
            continue
        destination = safe_path(MIRROR, name)
        content = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT, timeout=30)
        if not destination.exists() or destination.read_bytes() != content:
            atomic_write(destination, content)


def prepare(stage):
    # Stage assets and private state before mutating the published tree.
    for source in (ROOT / 'images').rglob('*'):
        if source.is_symlink():
            raise ValueError('Unexpected symlink in public images')
    shutil.copytree(ROOT / 'images', stage / 'images')
    state_file = STATE / 'topic_state.private.json'
    if state_file.exists():
        shutil.copyfile(state_file, stage / 'topic_state.private.json')
    admissions_state = STATE / 'admissions_state.private.json'
    if admissions_state.exists():
        shutil.copyfile(admissions_state, stage / 'admissions_state.private.json')
    current = load(ROOT / CATALOG)
    topics = sync_topics(STATE / 'topic_sources.private.json', stage / 'topic_state.private.json', stage / 'pending_topics.private.json', today=now()[:10])
    sources = load(STATE / 'sources.private.json')
    honors, report = build_honors(
        source_json=Path(sources['honors_json']),
        source_images_root=Path(sources['honors_site_root']),
        current_honors=current['honors'],
        destination_images=stage / 'images',
        source_posters_root=Path(sources['honors_originals']),
        dry_run=False,
    )
    data = {'updatedAt': current['updatedAt'], 'categories': topics['categories'], 'topics': topics['topics'], 'honors': honors}
    if {key: value for key, value in data.items() if key != 'updatedAt'} != {key: value for key, value in current.items() if key != 'updatedAt'}:
        data['updatedAt'] = now()[:10]
    save(stage / CATALOG, data)
    validate_catalog(data, stage)
    feed, admissions_report = build_admissions(
        STATE / 'admissions_sources.private.json',
        stage / 'admissions_state.private.json',
        load(ROOT / ADMISSIONS) if (ROOT / ADMISSIONS).exists() else None,
        checked_at=now(),
    )
    validate_feed(feed)
    save(stage / ADMISSIONS, feed)
    changes = []
    for source in [stage / CATALOG, stage / ADMISSIONS, *(stage / 'images' / 'honors').glob('*')]:
        relative = source.relative_to(stage).as_posix()
        if not source.is_file() or not generated(relative):
            raise ValueError('Unexpected generated asset')
        target = safe_path(ROOT, relative)
        if not target.exists() or hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(target.read_bytes()).digest():
            changes.append(relative)
    return data, changes, {'topics': {key: value for key, value in topics.items() if key not in {'topics', 'categories'}}, 'honors': report, 'admissions': admissions_report}


def run(publish=False):
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / 'publisher.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {'status': 'skipped_busy', 'checkedAt': now()}
        if publish:
            integrate_remote()
        with tempfile.TemporaryDirectory(prefix='staging-', dir=STATE) as temporary:
            stage = Path(temporary)
            data, changes, sources = prepare(stage)
            result = {'status': 'preview', 'checkedAt': now(), 'changedFiles': changes, 'topics': len(data['topics']), 'honors': len(data['honors']), 'sources': sources}
            if publish:
                # Check again after reading sources, in case an editor changed the checkout.
                assert_clean()
                for relative in changes:
                    atomic_write(safe_path(ROOT, relative), safe_path(stage, relative).read_bytes())
                if changes:
                    git('add', '--', *changes)
                    staged = git('diff', '--cached', '--name-only').splitlines()
                    if set(staged) != set(changes) or any(not generated(path) for path in staged):
                        raise RuntimeError('Unexpected staged files; refusing automatic commit')
                    git('commit', '-m', PREFIX + now())
                    commit = git('rev-parse', 'HEAD')
                    receipts_path = STATE / 'publisher_commits.private.json'
                    receipts = load(receipts_path) if receipts_path.exists() else {}
                    receipts[commit] = {'tree': git('rev-parse', 'HEAD^{tree}'), 'createdAt': now(), 'paths': changes}
                    save(receipts_path, receipts)
                if pending_commits():
                    git('push', 'origin', 'main')
                commit = git('rev-parse', 'HEAD')
                mirror(commit)
                for name in ('topic_state.private.json', 'pending_topics.private.json', 'admissions_state.private.json'):
                    if (stage / name).exists():
                        atomic_write(STATE / name, (stage / name).read_bytes())
                result.update(status='published' if changes else 'unchanged', commit=commit)
                save(STATE / 'last_run.private.json', result)
            else:
                save(STATE / 'preview.private.json', result)
            return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', help='Commit and push validated public updates; default is a private preview')
    options = parser.parse_args()
    try:
        result = run(publish=options.publish)
        print(json.dumps({key: value for key, value in result.items() if key != 'sources'}, ensure_ascii=False), flush=True)
        return 0
    except Exception as error:
        STATE.mkdir(parents=True, exist_ok=True)
        save(STATE / 'last_error.private.json', {'checkedAt': now(), 'error': str(error), 'kind': type(error).__name__})
        print('Automatic update failed; inspect the private last_error record.', flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
