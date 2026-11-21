"""Offline regressions for discovery, evidence coverage and public-field privacy."""

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import discover_topics as discovery


def translated(text):
    return {lang: text for lang in discovery.LANGUAGES}


def public_topic(identifier='cell-regulation'):
    return {'id': identifier, 'category': 'life',
            'title': translated('Cell regulation'),
            'summary': translated('Explore how cells regulate their responses to environmental signals.'),
            'tags': {lang: ['Cell biology'] for lang in discovery.LANGUAGES}}


class TopicDiscoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.sources = self.base / 'research'
        self.source = self.sources / 'cell-regulation'
        self.source.mkdir(parents=True)
        self.readme = self.source / 'README.md'
        self.readme.write_text('Cell responses to environmental signals.\n')
        self.state = self.base / 'private-state'
        self.state.mkdir()
        self.config_path = self.state / 'sources.private.json'
        self.scan_path = self.state / 'discovery.private.json'
        self.config = {
            'schemaVersion': 1, 'discoveryRoots': [str(self.sources)],
            'categories': [{'id': 'life', 'label': translated('Life science')}],
            'topics': [{'approved': True, 'reviewedAt': '2026-11-21',
                        'public': {**public_topic(), 'stage': 'proposal'},
                        'sources': [str(self.source)], 'practiceRunRoots': []}],
        }
        self.save_config()
        for key, value in [('STATE', self.state), ('CONFIG', self.config_path),
                           ('SCAN_STATE', self.scan_path)]:
            patcher = patch.object(discovery, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(discovery, 'today', return_value='2026-11-21')
        patcher.start()
        self.addCleanup(patcher.stop)

    def save_config(self):
        self.config_path.write_text(json.dumps(self.config))

    def units(self):
        return discovery.inventory(self.config)

    def response(self, units, identifier='cell-regulation'):
        return {'topics': [{'public': public_topic(identifier), 'sourceIds': list(units)}],
                'ignored': []}

    def per_source_response(self, config, units, audit):
        return {'topics': [{'public': public_topic(Path(unit['path']).stem), 'sourceIds': [key]}
                           for key, unit in units.items()], 'ignored': []}

    def merge(self, response, units=None):
        return discovery.merge(self.config, self.units() if units is None else units,
                               response, '2026-11-21')

    def test_new_and_changed_sources_are_automatically_processed_once(self):
        with patch.object(discovery, 'generate', side_effect=self.per_source_response) as generate:
            initial = discovery.run(apply=True)
            self.assertEqual(initial['changedSources'], 1)
            self.assertEqual(generate.call_count, 1)
            generate.reset_mock()
            unchanged = discovery.run(apply=True)
            self.assertEqual(unchanged['changedSources'], 0)
            generate.assert_not_called()

            self.readme.write_text('Updated source scope: cell responses and their regulation.\n')
            added = self.sources / 'cell-tracking'
            added.mkdir()
            (added / 'README.md').write_text('Tracking changes in cellular behavior.\n')
            changed = discovery.run(apply=True)
            self.assertEqual(changed['changedSources'], 2)
            self.assertEqual(changed['newTopics'], 1)
            self.assertEqual(generate.call_count, 1)
            saved = json.loads(self.config_path.read_text())
            self.assertEqual({row['public']['id'] for row in saved['topics']},
                             {'cell-regulation', 'cell-tracking'})
            generate.reset_mock()
            self.assertEqual(discovery.run(apply=True)['changedSources'], 0)
            generate.assert_not_called()

    def test_equivalent_html_and_pdf_are_not_repeated_in_model_evidence(self):
        html = self.source / 'research.html'
        pdf = self.source / 'research.pdf'
        html.write_text('<html><style>hidden</style><p>Shared research overview.</p></html>')
        pdf.write_bytes(b'%PDF-fake-test-fixture')
        units = self.units()
        self.assertEqual(len(units), 1)
        with patch.object(discovery.subprocess, 'run', return_value=Mock(returncode=0, stdout='Shared research overview.\n')):
            text = discovery.source_text(next(iter(units.values())))
        self.assertEqual(text.count('Shared research overview.'), 1)
        self.assertNotIn('hidden', text)
        merged = self.merge(self.response(units), units)
        self.assertEqual(len(merged['topics']), 1)

    def test_same_topic_from_separate_exports_has_one_mapping(self):
        html = self.sources / 'new-topic.html'
        pdf = self.sources / 'new-topic.pdf'
        html.write_text('<p>Another research topic.</p>')
        pdf.write_bytes(b'%PDF-fake-test-fixture')
        units = {key: unit for key, unit in self.units().items() if unit['path'] != str(self.source)}
        merged = self.merge(self.response(units, 'new-topic'), units)
        additions = [row for row in merged['topics'] if row['public']['id'] == 'new-topic']
        self.assertEqual(len(additions), 1)
        self.assertEqual(set(additions[0]['sources']), {str(html), str(pdf)})
        repeated = discovery.merge(merged, units, self.response(units, 'new-topic'), '2026-11-22')
        self.assertEqual(len(repeated['topics']), 2)
        self.assertEqual(len(repeated['topics'][-1]['sources']), 2)

    def test_all_four_languages_are_required_for_every_text_field(self):
        units = self.units()
        for field in ('title', 'summary', 'tags'):
            for lang in sorted(discovery.LANGUAGES):
                with self.subTest(field=field, language=lang):
                    response = self.response(units)
                    del response['topics'][0]['public'][field][lang]
                    with self.assertRaises(discovery.TopicSyncError):
                        self.merge(response, units)
        response = self.response(units)
        response['topics'][0]['public']['title']['fr'] = 'Unexpected language'
        with self.assertRaises(discovery.TopicSyncError):
            self.merge(response, units)

    def test_evidence_ids_and_topic_ids_are_validated(self):
        units = self.units()
        source_id = next(iter(units))
        for invalid_ids in ([], ['source-not-in-current-scan'], [source_id, source_id], source_id, [None]):
            with self.subTest(ids=invalid_ids):
                response = self.response(units)
                response['topics'][0]['sourceIds'] = invalid_ids
                with self.assertRaises(discovery.TopicSyncError):
                    self.merge(response, units)
        response = self.response(units)
        response['topics'].append(copy.deepcopy(response['topics'][0]))
        with self.assertRaises(discovery.TopicSyncError):
            self.merge(response, units)

    def test_unknown_or_repeated_ignored_source_ids_are_rejected(self):
        units = self.units()
        source_id = next(iter(units))
        for ignored in ([{'sourceId': 'outside-scanned-roots', 'reason': 'Not research.'}],
                        [{'sourceId': source_id, 'reason': 'Not research.'}] * 2):
            with self.subTest(ignored=ignored):
                with self.assertRaises(discovery.TopicSyncError):
                    self.merge({'topics': [], 'ignored': ignored}, units)

    def test_same_length_edit_with_preserved_timestamp_changes_fingerprint(self):
        before = self.units()
        old_stat = self.readme.stat()
        original = self.readme.read_text()
        self.readme.write_text(original.replace('Cell', 'Gene'))
        os.utime(self.readme, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
        after = self.units()
        self.assertEqual(set(before), set(after))
        source_id = next(iter(before))
        self.assertNotEqual(before[source_id]['fingerprint'], after[source_id]['fingerprint'])

    def test_unknown_source_cannot_be_silently_dropped(self):
        added = self.sources / 'unfamiliar-research'
        added.mkdir()
        (added / 'README.md').write_text('Another research question.')
        units = self.units()
        known = next(key for key, unit in units.items() if unit['path'] == str(self.source))
        unknown = next(key for key in units if key != known)
        response = self.response({known: units[known]})
        with self.assertRaises(discovery.TopicSyncError):
            self.merge(response, units)
        response['ignored'] = [{'sourceId': unknown, 'reason': 'This source contains a generic course schedule.'}]
        self.assertEqual(len(self.merge(response, units)['topics']), 1)
        response['ignored'].append({'sourceId': known, 'reason': 'Already assigned to a topic.'})
        with self.assertRaises(discovery.TopicSyncError):
            self.merge(response, units)

    def test_unrelated_existing_topics_are_retained(self):
        units = self.units()
        merged = self.merge(self.response(units, 'additional-topic'), units)
        self.assertEqual({item['public']['id'] for item in merged['topics']},
                         {'cell-regulation', 'additional-topic'})

    def test_status_labels_in_any_language_are_rejected(self):
        units = self.units()
        cases = {'zh-CN': ['科研提案', '方向储备', '试点探索', '已完成'],
                 'zh-TW': ['方向儲備', '試點探索', '已發表'],
                 'ja': ['構想段階', '試行段階', '実施済'],
                 'en': ['Research proposal', 'Pilot exploration', 'Planned research',
                        'Completed study', 'Published research']}
        for lang, phrases in cases.items():
            for phrase in phrases:
                with self.subTest(language=lang, phrase=phrase):
                    response = self.response(units)
                    response['topics'][0]['public']['summary'][lang] = phrase
                    with self.assertRaises(discovery.TopicSyncError):
                        self.merge(response, units)

    def test_personal_names_and_private_paths_are_rejected_in_public_text(self):
        (self.source / '研究方案_李明辉.html').write_text('<p>A research overview.</p>')
        units = self.units()
        for content in ['李明辉研究细胞', '李同学研究细胞', '田中さんの研究',
                        '李明辉教授', '/work/private/research/results',
                        '/home/admin/private.txt', 'person@example.org']:
            for field in ('title', 'summary', 'tags'):
                with self.subTest(content=content, field=field):
                    response = self.response(units)
                    response['topics'][0]['public'][field]['zh-CN'] = [content] if field == 'tags' else content
                    with self.assertRaises(discovery.TopicSyncError):
                        self.merge(response, units)

    def test_model_cannot_add_private_fields_or_a_stage_field(self):
        units = self.units()
        for name, value in [('stage', 'proposal'), ('sourcePath', str(self.source)),
                            ('sourceIds', list(units)), ('studentName', '李明辉')]:
            with self.subTest(field=name):
                response = self.response(units)
                response['topics'][0]['public'][name] = value
                with self.assertRaises(discovery.TopicSyncError):
                    self.merge(response, units)

    def test_nested_and_root_data_models_archives_and_symlinks_are_skipped(self):
        external = self.base / 'external'
        external.mkdir()
        (external / 'private.md').write_text('Must not be scanned.')
        for parent in (self.sources, self.source):
            for name in ('data', 'models', 'runs', '归档', 'backup-v1', '.hidden'):
                directory = parent / name
                directory.mkdir()
                (directory / 'sensitive.md').write_text('Must not be scanned.')
            (parent / 'external-link').symlink_to(external, target_is_directory=True)
            (parent / 'linked.md').symlink_to(external / 'private.md')
        units = self.units()
        self.assertEqual([unit['path'] for unit in units.values()], [str(self.source)])
        self.assertEqual(next(iter(units.values()))['documents'][0]['path'], str(self.readme))
        self.assertEqual(len(next(iter(units.values()))['documents']), 1)

    def test_source_tree_is_unchanged_by_inventory_extraction_and_apply(self):
        paths = [self.source, self.readme]
        def snapshot():
            return {str(p): (p.stat().st_mtime_ns, p.stat().st_size,
                             hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
                    for p in paths}
        before = snapshot()
        units = self.units()
        discovery.source_text(next(iter(units.values())))
        with patch.object(discovery, 'generate', side_effect=self.per_source_response):
            discovery.run(apply=True)
        self.assertEqual(snapshot(), before)
        self.assertEqual(self.scan_path.stat().st_mode & 0o777, 0o600)

    def test_symlink_root_and_shared_stores_cannot_become_research_roots(self):
        linked_root = self.base / 'linked-research'
        linked_root.symlink_to(self.sources, target_is_directory=True)
        for root in (str(linked_root), '/work/shared/datasets', '/work/shared/models'):
            with self.subTest(root=root):
                config = copy.deepcopy(self.config)
                config['discoveryRoots'] = [root]
                with self.assertRaises(discovery.TopicSyncError):
                    discovery.inventory(config)

    def test_source_text_redacts_contacts_and_labeled_personal_information(self):
        self.readme.write_text('姓名：李明辉\n李同学分析细胞。\ncontact@example.org\n'
                               '/work/private/results.txt\nA neutral scientific question.\n')
        text = discovery.source_text(next(iter(self.units().values())))
        for private in ('李明辉', '李同学', 'contact@example.org', '/work/private'):
            self.assertNotIn(private, text)
        self.assertIn('A neutral scientific question.', text)

    def test_missing_source_root_preserves_configuration_and_inventory(self):
        self.scan_path.write_text('{"previous":true}')
        self.config['discoveryRoots'] = [str(self.base / 'unavailable')]
        self.save_config()
        before_config, before_scan = self.config_path.read_bytes(), self.scan_path.read_bytes()
        with patch.object(discovery, 'generate') as generate:
            with self.assertRaises(discovery.TopicSyncError):
                discovery.run(apply=True)
            generate.assert_not_called()
        self.assertEqual(self.config_path.read_bytes(), before_config)
        self.assertEqual(self.scan_path.read_bytes(), before_scan)

    def test_concurrent_configuration_change_is_never_overwritten(self):
        replacement = copy.deepcopy(self.config)
        replacement['operatorNote'] = 'A concurrent reviewed update.'
        replacement_bytes = json.dumps(replacement).encode()
        self.scan_path.write_text('{"previous":true}')
        before_scan = self.scan_path.read_bytes()
        def change_config(config, units, audit):
            self.config_path.write_bytes(replacement_bytes)
            return self.response(units)
        with patch.object(discovery, 'generate', side_effect=change_config):
            with self.assertRaisesRegex(discovery.TopicSyncError, 'configuration changed'):
                discovery.run(apply=True)
        self.assertEqual(self.config_path.read_bytes(), replacement_bytes)
        self.assertEqual(self.scan_path.read_bytes(), before_scan)

    def test_failed_model_output_does_not_advance_scan_or_configuration(self):
        self.scan_path.write_text('{"previous":true}')
        before_config, before_scan = self.config_path.read_bytes(), self.scan_path.read_bytes()
        with patch.object(discovery, 'generate', return_value={'topics': [], 'ignored': []}):
            with self.assertRaises(discovery.TopicSyncError):
                discovery.run(apply=True)
        self.assertEqual(self.config_path.read_bytes(), before_config)
        self.assertEqual(self.scan_path.read_bytes(), before_scan)


if __name__ == '__main__':
    unittest.main()
