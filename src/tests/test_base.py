# Tests for base plugin
import json
import logging
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from nmk import __version__ as nmk_version
from nmk.envbackend import EnvBackendFactory
from nmk.tests.tester import NmkBaseTester
from nmk.utils import is_windows


class TestBasePlugin(NmkBaseTester):
    @property
    def templates_root(self) -> Path:
        return Path(__file__).parent / "templates"

    def test_output(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "outputDir"])
        self.check_logs(re.compile('Config dump: { "outputDir": "[^"]+/out" }'))

    def test_clean_missing(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["clean"])
        self.check_logs(f"Nothing to clean (folder not found: {self.test_folder / 'out'})")

    def test_clean_folder(self):
        fake_out = self.test_folder / "out"
        fake_out.mkdir()
        assert fake_out.is_dir()
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["clean"])
        self.check_logs(f"Cleaning folder: {self.test_folder}")
        assert not fake_out.exists()

    def test_build(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--dry-run"])
        self.check_logs(["setup]] INFO 🛫 - Setup project configuration", "build]] INFO 🛠  - Build project artifacts", "17 built tasks"], check_order=True)

    def test_test(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--dry-run", "tests"])
        self.check_logs(["tests]] INFO 🤞 - Run automated tests", "18 built tasks"], check_order=True)

    def test_package(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--dry-run", "package"])
        self.check_logs(["package]] INFO 📦 - Package project artifacts", "18 built tasks"], check_order=True)

    def test_install(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--dry-run", "install"])
        self.check_logs(["install]] INFO 📥 - Install built software", "18 built tasks"], check_order=True)

    def test_publish(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--dry-run", "publish"])
        self.check_logs(["publish]] INFO 🚚 - Publish artifacts", "19 built tasks"], check_order=True)

    def test_version(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["version"])
        self.check_logs(f" 👉 nmk     : {nmk_version}")

    def test_help(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["help"])
        self.check_logs(" 👉 nmk     : https://nmk.readthedocs.io/")

    def test_tasks(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["tasks"])
        self.check_logs(" 👉 tasks           : 🗃  - List all available tasks")

    def test_git_version_config(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "gitVersion"])
        self.check_logs('Config dump: { "gitVersion": "')

    def test_git_version_config_no_tag(self, monkeypatch: pytest.MonkeyPatch):
        # Fake git subprocess behavior, to make "git describe --tags" failing
        real_run = subprocess.run
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check, capture_output, text, encoding, cwd, errors: (  # type: ignore
                subprocess.CompletedProcess(all_args, 1, "", "")  # type: ignore
                if all_args[:3] == ["git", "describe", "--tags"]
                else real_run(all_args, check=check, capture_output=capture_output, text=text, encoding=encoding, cwd=cwd)  # type: ignore
            ),  # type: ignore
        )
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "gitVersion"])
        self.check_logs('Config dump: { "gitVersion": "0.0.0-')

    def test_git_version_config_no_git(self, monkeypatch: pytest.MonkeyPatch):
        # Fake git subprocess behavior, to make all "git" commands failing
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check, capture_output, text, encoding, cwd, errors: subprocess.CompletedProcess(all_args, 1, "", ""),  # type: ignore
        )
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "gitVersion"])
        self.check_logs('Config dump: { "gitVersion": "0.0.0" }')

    def test_git_version_stamp(self):
        # Try 1: git version is persisted
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.version"])
        self.check_logs("Refresh git version")
        assert (self.test_folder / "out" / ".gitversion").is_file()

        # Try 2: shouldn't be persisted
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.version"])
        self.check_logs("Persisted git version already up to date")

    def test_git_clean(self, monkeypatch: pytest.MonkeyPatch):
        # Stub to avoid real git clean command executed
        monkeypatch.setattr(subprocess, "run", lambda args, cwd, check: None)  # type: ignore
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.clean"])
        self.check_logs("Clean all git ignored files")

    def test_git_dirty(self, monkeypatch: pytest.MonkeyPatch):
        # Stub to have "git status" command with empty return
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check, capture_output, text, encoding, cwd, errors: subprocess.CompletedProcess(all_args, 0, "", ""),  # type: ignore
        )
        prj = self.prepare_project("ref_base.yml")
        self.nmk(prj, extra_args=["git.dirty", "--config", '{"gitEnableDirtyCheck":true}'], with_epilogue=True)
        self.check_logs("Check for modified files")

        # Stub to have "git status" command with some dirty files
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check=True, capture_output=True, text=True, encoding="utf-8", cwd=None, errors="ignore": subprocess.CompletedProcess(  # type: ignore
                all_args,  # type: ignore
                0,
                " M src/nmk_base/git.py\n M src/nmk_base/git.yml",
                "",  # type: ignore
            ),
        )
        self.nmk(
            prj,
            extra_args=["git.dirty", "--config", '{"gitEnableDirtyCheck":true}'],
            expected_error="An error occurred during task git.dirty build: Current folder is dirty:",
            with_epilogue=True,
        )

    def test_venv_merged_requirements(self):
        # Prepare some fake files
        fake_req = self.test_folder / "somereq.txt"
        fake_arc = self.test_folder / "somearchive.tar.gz"
        with fake_req.open("w") as f:
            f.write("SomeFakePackage")
        fake_arc.touch()

        # Build a merged requirements file
        self.nmk(
            self.prepare_project("ref_base.yml"),
            extra_args=[
                "py.req",
                "--config",
                json.dumps(
                    {
                        "venvFileDeps": ["${PROJECTDIR}/somereq.txt"],
                        "venvArchiveDeps": ["${PROJECTDIR}/somearchive.tar.gz"],
                        "backendUseRequirements": True,
                    }
                ),
            ],
        )

        # Verify generated file
        with (self.test_folder / "requirements.txt").open() as f:
            content = f.read()
            assert "nmk" in content
            assert "SomeFakePackage" in content
            assert "somearchive.tar.gz" in content

    def test_venv_simple_update(self, monkeypatch: pytest.MonkeyPatch):
        # Fake requirements
        (self.test_folder / "requirements.txt").write_text("rich==4.5.6\n")

        # Fake pip subprocess behavior
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda args, **kwargs: subprocess.CompletedProcess(args, 0, "# Fake packages list\nsomePackage==1.2.3\nrich==4.5.6", ""),  # type: ignore
        )

        # Test a simple venv update
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["py.venv"])

        # Verify output files
        output_req = self.test_folder / "out" / "requirements.txt"
        assert output_req.exists()
        assert "rich==" in output_req.read_text()

    def test_venv_not_mutable(self, monkeypatch: pytest.MonkeyPatch):
        # Fake non-mutable backend
        class FakeBackend:
            def __init__(self, root: Path) -> None:
                self._root = root

            def is_mutable(self) -> bool:
                return False

            @property
            def use_requirements(self) -> bool:
                return True

            @property
            def venv_name(self) -> str:
                return "venv"

            @property
            def venv_root(self) -> Path:
                return self._root / "venv"

            def lock(self, venv_status: Path) -> None:
                pass

            def dump(self, output_file: Path, log_level: int = logging.INFO):
                output_file.write_text("Fake backend dump")

        monkeypatch.setattr(EnvBackendFactory, "detect", lambda *args, **kwargs: FakeBackend(self.test_folder))  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

        # Test a simple venv update
        project = self.prepare_project("ref_base.yml")
        self.nmk(
            project,
            extra_args=["py.venv", "--config", '{"gitEnableDirtyCheck":true}'],
            expected_error="An error occurred during task py.venv build: Build stopped",
        )
        self.check_logs(["Requirements have been updated", "Updated config item: venvRequirementsUpdated=True"])

        # Force requirements update
        self.nmk(
            project,
            extra_args=["py.req", "--force"],
        )
        self.check_logs(["Updated config item: venvRequirementsUpdated=False"])

        # Try again
        self.nmk(
            project,
            extra_args=["py.venv", "--config", '{"gitEnableDirtyCheck":true}'],
        )
        self.check_logs("Requirements are up to date, nothing to do")

    def test_git_ignore(self):
        # Try 1: generate a new .gitignore
        gitignore = self.test_folder / ".gitignore"
        assert not gitignore.exists()
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.ignore"])
        assert gitignore.is_file()
        assert (self.test_folder / "out" / ".gitignore").is_file()
        self.check_logs("Create new .gitignore file")

        # Read content for compare
        with gitignore.open() as f:
            content = f.read()

        # Try 2: regenerate after fake manual edit
        time.sleep(1)
        with gitignore.open("w") as f:
            f.write("foo\n")
            f.write(content)
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.ignore"])
        assert gitignore.is_file()
        self.check_logs("Merge .gitignore content by replacing fragment at lines 2-")

        # Read content for compare
        with gitignore.open() as f:
            assert "foo\n" + content == f.read()

        # Try 3: update an existing file without fragment
        time.sleep(1)
        with gitignore.open("w") as f:
            f.write("foo\n")
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.ignore"])
        assert gitignore.is_file()
        self.check_logs("Insert generated fragment at and of existing .gitignore file")

        # Read content for compare
        with gitignore.open() as f:
            assert "foo\n" + content == f.read()

    def test_git_ignore_absolute_path(self):
        gitignore = self.test_folder / ".gitignore"
        assert not gitignore.exists()
        self.nmk(self.prepare_project("ref_base_absolute_git_ignore.yml"), extra_args=["git.ignore"])
        assert gitignore.is_file()
        assert (self.test_folder / "out" / ".gitignore").is_file()
        self.check_logs(["Create new .gitignore file", "Can't ignore non project-relative absolute path:"])

    def test_git_attributes(self):
        gitattributes = self.test_folder / ".gitattributes"
        assert not gitattributes.exists()
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.attributes"])
        assert gitattributes.is_file()
        assert (self.test_folder / "out" / ".gitattributes").is_file()
        self.check_logs("Create new .gitattributes file")

    def test_dirty_check(self):
        # Get current value
        already_in_ci = "CI" in os.environ
        old_value = None
        if already_in_ci:
            old_value = os.environ["CI"]
            del os.environ["CI"]

        # Without CI env var
        p = self.prepare_project("ref_base.yml")
        self.nmk(p, extra_args=["--print", "gitEnableDirtyCheck", "--print", "isLocalBuild", "--print", "isCIBuild"])
        self.check_logs('Config dump: { "isLocalBuild": true, "isCIBuild": false, "gitEnableDirtyCheck": false }')

        # With CI env var
        os.environ["CI"] = "true"
        self.nmk(p, extra_args=["--print", "gitEnableDirtyCheck", "--print", "isLocalBuild", "--print", "isCIBuild"])
        self.check_logs('Config dump: { "isLocalBuild": false, "isCIBuild": true, "gitEnableDirtyCheck": true }')

        # Restore environment
        if old_value is not None:
            os.environ["CI"] = old_value
        else:
            del os.environ["CI"]

    def test_sysdeps(self):
        # Run with missing fancy system dep
        self.nmk(
            self.prepare_project("ref_sysdeps.yml"),
            extra_args=["sys.deps"],
            with_prologue=True,
            expected_error="An error occurred during task sys.deps build: Please install missing system dependencies (see above)",
        )
        self.check_logs(
            [
                "Missing system dependencies: unknown-cmd",
                '* for "unknown-cmd" manual user install: see https://unknown-cmd.com/downloads',
            ]
        )

        # Apt install instructions depend if apt is present on the system
        apt_pattern = '* for global system install, use this command: "sudo apt install unknown-cmd"'
        if not is_windows():
            self.check_logs(apt_pattern)
        else:
            with pytest.raises(AssertionError, match="Missing patterns: .*"):
                self.check_logs(apt_pattern)

    @pytest.fixture
    def fake_new_backend(self, monkeypatch: pytest.MonkeyPatch):
        # Fake level env var to simulate new backend (buildenv >=2.X)
        monkeypatch.setenv("BUILDENV_VERSION", "2")

        # Back to test
        yield

    def test_java_runtime(self, monkeypatch: pytest.MonkeyPatch):
        p = self.prepare_project("ref_base.yml")

        # Case 1: unknown custom path
        java_path = self.test_folder / "java"
        self.nmk(p, extra_args=["--print", "javaRuntime", "--config", f"javaRuntimeCustomPath={java_path}"])
        self.check_logs("Provided path for 'java' command was not found: ")

        # Case 2: valid custom path
        java_path.touch()
        self.nmk(p, extra_args=["--print", "javaRuntime", "--config", f"javaRuntimeCustomPath={java_path}"])
        self.check_logs("Using provided path for 'java' command:")

        # Case 3: detect from system path with missing command
        old_which = shutil.which
        monkeypatch.setattr(shutil, "which", lambda cmd: None if cmd == "java" else old_which(cmd))  # type: ignore
        self.nmk(p, extra_args=["--print", "javaRuntime"])
        self.check_logs("'java' command was not found in system path")

        # Case 4: detect from system path with valid command
        monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/java" if cmd == "java" else old_which(cmd))  # type: ignore
        self.nmk(p, extra_args=["--print", "javaRuntime"])
        self.check_logs("'java' command found in system path:")
