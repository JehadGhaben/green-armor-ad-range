"""Standard-library tests for local CLI behavior (Docker not required)."""
import contextlib
import io
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import armorlab


class RangeCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.patches = [
            patch.object(armorlab, "RUNTIME", self.root / "runtime"),
            patch.object(armorlab, "STATE_FILE", self.root / "runtime" / "state.json"),
            patch.object(armorlab, "SEED_FILE", self.root / "runtime" / "seed" / "scenario.json"),
            patch.object(armorlab, "PROGRESS_FILE", self.root / "runtime" / "progress.json"),
        ]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temp.cleanup()

    def test_dc_provisioning_dependencies_are_explicit(self):
        dockerfile = (Path(__file__).resolve().parents[1] / 'docker/dc/Dockerfile').read_text()
        self.assertIn('samba-ad-provision', dockerfile)
        self.assertIn('samba-ad-dc', dockerfile)
        self.assertIn('winbind', dockerfile)

    def test_global_ldap_setting_is_inserted_under_global(self):
        entrypoint = (Path(__file__).resolve().parents[1] / 'docker/dc/entrypoint.sh').read_text()
        self.assertIn("lines.insert(index + 1, '    ldap server require strong auth = no')", entrypoint)
        self.assertNotIn('    map to guest = Never', entrypoint)
        self.assertIn('Incomplete AD volume detected', entrypoint)

    def test_ci_has_a_real_docker_smoke_job(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/ci.yml').read_text()
        self.assertIn('real-docker-smoke:', workflow)
        self.assertIn('python3 scripts/smoke-test.py', workflow)

    def test_flags_are_unique_and_correctly_shaped(self):
        s1, s2 = armorlab.new_state(), armorlab.new_state()
        self.assertNotEqual(s1["admin_password"], s2["admin_password"])
        self.assertNotEqual(s1["service_password"], s2["service_password"])
        self.assertEqual(len(s1["flags"]), 4)
        self.assertEqual(len(set(s1["flags"].values())), 4)
        for key, value in s1["flags"].items():
            self.assertTrue(value.startswith("GA{" + key + "-"))
            self.assertTrue(value.endswith("}"))

    def test_first_init_is_stable_and_secret_seed_is_written(self):
        first = armorlab.ensure_state()
        second = armorlab.ensure_state()
        self.assertEqual(first, second)
        self.assertEqual(first, armorlab.read_json(armorlab.SEED_FILE))
        self.assertEqual([], armorlab.read_json(armorlab.PROGRESS_FILE)["solved"])
        self.assertEqual(0o600, armorlab.STATE_FILE.stat().st_mode & 0o777)

    def test_valid_submission_scores_once(self):
        value = armorlab.ensure_state()["flags"]["01"]
        args = types.SimpleNamespace(flag=value)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, armorlab.command_submit(args))
            self.assertEqual(0, armorlab.command_submit(args))
        self.assertEqual(["01"], armorlab.read_json(armorlab.PROGRESS_FILE)["solved"])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(0, armorlab.command_score(types.SimpleNamespace(json=True)))
        self.assertIn('"earned": 15', out.getvalue())

    def test_wrong_flag_does_not_change_progress(self):
        armorlab.ensure_state()
        with contextlib.redirect_stdout(io.StringIO()):
            code = armorlab.command_submit(types.SimpleNamespace(flag="GA{wrong}"))
        self.assertEqual(1, code)
        self.assertEqual([], armorlab.read_json(armorlab.PROGRESS_FILE)["solved"])

    def test_safe_reset_without_yes_does_nothing(self):
        armorlab.ensure_state()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(2, armorlab.command_reset(types.SimpleNamespace(yes=False)))
        self.assertTrue(armorlab.STATE_FILE.exists())

    def test_hint_works(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(0, armorlab.command_hint(types.SimpleNamespace(stage="04", level=2)))
        self.assertIn("SMB", out.getvalue())


if __name__ == "__main__":
    unittest.main()
