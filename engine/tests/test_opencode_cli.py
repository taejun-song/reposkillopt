"""Feature 017 — keyless opencode-cli provider (TDD, written before implementation)."""
import unittest
from unittest import mock

from reposkillopt_engine.providers import ProviderError, make_provider


class TestDispatch(unittest.TestCase):
    def test_make_provider_opencode_cli(self):
        p = make_provider("opencode-cli")
        self.assertEqual(p.name, "opencode-cli")

    def test_model_parsed_from_spec(self):
        p = make_provider("opencode-cli:anthropic/claude-3-5-sonnet")
        self.assertEqual(p.model, "anthropic/claude-3-5-sonnet")


class TestOpenCodeCLIProvider(unittest.TestCase):
    def _p(self, **kw):
        from reposkillopt_engine.providers.opencode_cli import OpenCodeCLIProvider
        return OpenCodeCLIProvider(**kw)

    def test_complete_runs_opencode_run_and_returns_clean_stdout(self):
        p = self._p(model="openai/gpt-4o")
        fake = mock.Mock(returncode=0, stdout="\x1b[32m  # Spec\x1b[0m\n", stderr="")
        with mock.patch("subprocess.run", return_value=fake) as run:
            out = p.complete("PROMPT", system="SYS")
        cmd = run.call_args[0][0]
        self.assertEqual(cmd[0], "opencode")
        self.assertIn("run", cmd)                              # non-interactive run mode (like claude -p)
        self.assertIn("--model", cmd)
        self.assertIn("openai/gpt-4o", cmd)
        self.assertTrue(any("PROMPT" in a for a in cmd))      # prompt passed
        self.assertTrue(any("SYS" in a for a in cmd))         # system prepended
        self.assertEqual(out, "# Spec")                       # ANSI stripped + trimmed

    def test_no_model_omits_flag(self):
        p = self._p()
        fake = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch("subprocess.run", return_value=fake) as run:
            p.complete("hi")
        self.assertNotIn("--model", run.call_args[0][0])      # uses OpenCode's configured default

    def test_missing_binary_raises_providererror(self):
        p = self._p(binary="definitely-not-real-opencode-xyz")
        with self.assertRaises(ProviderError):
            p.complete("hi")

    def test_nonzero_exit_raises_providererror(self):
        p = self._p()
        fake = mock.Mock(returncode=1, stdout="", stderr="boom")
        with mock.patch("subprocess.run", return_value=fake):
            with self.assertRaises(ProviderError):
                p.complete("hi")

    def test_timeout_raises_providererror(self):
        import subprocess
        p = self._p(timeout=1.0)
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired("opencode", 1.0)):
            with self.assertRaises(ProviderError):
                p.complete("hi")


if __name__ == "__main__":
    unittest.main()
