import subprocess

from _pytest.monkeypatch import MonkeyPatch
from buildenv.extension import BuildEnvInfo  # TODO: Reactivate this test when buildenv 2 is rolled out
from pytest_multilog import TestHelper

from nmk_base._buildenv.extension import NmkBaseBuildEnvExtension


class TestNmkBuildenvExtension(TestHelper):
    def test_no_project(self, monkeypatch: MonkeyPatch):
        # Fake extension loading
        venv_bin = self.test_folder / "venv" / "bin"
        ext = NmkBaseBuildEnvExtension(BuildEnvInfo(venv_bin=venv_bin, project_root=None))

        # Fake subprocess call
        called_args = None

        def fake_run(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:  # type: ignore
            nonlocal called_args
            called_args = args
            return subprocess.CompletedProcess(args, 0)

        monkeypatch.setattr(subprocess, "run", fake_run)  # type: ignore

        # Trigger init -> should do nothing
        ext.init(force=False)
        assert called_args is None

    def test_fake_ext_load(self, monkeypatch: MonkeyPatch):
        # Fake extension loading
        venv_bin = self.test_folder / "venv" / "bin"
        ext = NmkBaseBuildEnvExtension(BuildEnvInfo(venv_bin=venv_bin, project_root=self.test_folder))

        # Check expected completions
        comps = ext.get_completion_commands()
        assert len(comps) == 1
        comp = comps[0]
        assert comp.get_command() == 'eval "$(register-python-argcomplete nmk)"'

        # Fake subprocess call
        called_args = None

        def fake_run(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:  # type: ignore
            nonlocal called_args
            called_args = args
            return subprocess.CompletedProcess(args, 0)

        monkeypatch.setattr(subprocess, "run", fake_run)  # type: ignore

        # Trigger init in non nmk project (no nmk.yml) -> should do nothing
        ext.init(force=False)
        assert called_args is None

        # Trigger init in nmk project (with nmk.yml) -> should call subprocess
        (self.test_folder / "nmk.yml").touch()
        ext.init(force=False)
        assert called_args == [venv_bin / "nmk", "setup", "--force"]
        called_args = None

        # Trigger init with existing .nmk folder -> should do nothing
        (self.test_folder / ".nmk").mkdir()
        ext.init(force=False)
        assert called_args is None

        # Trigger init with force -> should call subprocess
        ext.init(force=True)
        assert called_args == [venv_bin / "nmk", "setup", "--force"]
