import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceResolution(unittest.TestCase):
    def test_stable_tags_exclude_prereleases_and_peel_annotated_tags(self):
        tag, revision = load('resolve').stable_tag(
            'a' * 40 + '\trefs/tags/v26.09.29\n' +
            'b' * 40 + '\trefs/tags/v26.10.01\n' +
            'c' * 40 + '\trefs/tags/v26.10.01^{}\n' +
            'd' * 40 + '\trefs/tags/v99.0.0-rc.1\n')
        self.assertEqual((tag, revision), ('v26.10.01', 'c' * 40))

    def test_no_stable_release_fails_instead_of_using_dev(self):
        with self.assertRaises(ValueError):
            load('resolve').stable_tag('a' * 40 + '\trefs/tags/v1.0.0-beta\n')


class UpstreamCompatibility(unittest.TestCase):
    def test_supersync_revision_ignores_unrelated_newer_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', '-C', tmp, '-c', 'user.name=Build Test',
                                                '-c', 'user.email=build-test@example.invalid', *args], text=True).strip()
            git('init', '-q')
            (source / 'package.json').write_text('{}')
            git('add', '.')
            git('commit', '-qm', 'Server input')
            expected = git('rev-parse', 'HEAD')
            (source / 'README.md').write_text('Unrelated docs')
            git('add', '.')
            git('commit', '-qm', 'Docs only')
            self.assertNotEqual(expected, git('rev-parse', 'HEAD'))
            self.assertEqual(load('prepare').image_revision('supersync', source), expected)

    def test_supersync_adapter_preserves_upstream_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            upstream = source / 'packages/super-sync-server'
            upstream.mkdir(parents=True)
            original = 'FROM node:24-alpine\nUSER supersync\nENV RUN_MIGRATIONS_ON_STARTUP=false\nCMD ["sh", "-c", "exec node server.js"]\n'
            (upstream / 'Dockerfile').write_text(original)
            path = load('prepare').prepare('supersync', source, ROOT)
            generated = path.read_text()
            self.assertTrue(generated.startswith(original))
            self.assertIn('ENTRYPOINT ["/usr/local/bin/community-notice"]', generated)
            self.assertIn('_build', (source / '.dockerignore').read_text())

    def test_new_upstream_entrypoint_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            upstream = source / 'packages/super-sync-server'
            upstream.mkdir(parents=True)
            (upstream / 'Dockerfile').write_text('FROM node:24\nENTRYPOINT ["upstream"]\n')
            with self.assertRaises(ValueError):
                load('prepare').prepare('supersync', source, ROOT)

    def test_notice_preserves_command_exit_status_and_opt_out(self):
        import os
        notice = ROOT / 'dockerfiles/supersync/notice.sh'
        result = subprocess.run(['sh', str(notice), 'sh', '-c', 'exit 17'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 17)
        self.assertIn('ghcr.io/super-productivity/supersync', result.stdout)
        result = subprocess.run(['sh', str(notice), 'printf', '%s', 'custom command'],
                                env=dict(os.environ, SUPERSYNC_HIDE_UPSTREAM_NOTICE='true'),
                                capture_output=True, text=True)
        self.assertEqual(result.stdout, 'custom command')
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
