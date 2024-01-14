# Tests for base plugin
import re
import shutil
import subprocess
import time
from pathlib import Path

from nmk import __version__ as nmk_version
from nmk.tests.tester import NmkBaseTester
from nmk.utils import is_windows

from nmk_base import __version__
from nmk_base.buildenv import BuildenvInitBuilder


class TestBasePlugin(NmkBaseTester):
    @property
    def templates_root(self) -> Path:
        return Path(__file__).parent / "templates"

    def test_output(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "outputDir"])
        self.check_logs(re.compile('Config dump: { "outputDir": "[^"]+/out" }'))

    def test_clean_missing(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["clean"])
        self.check_logs(f"Nothing to clean (folder not found: {self.test_folder/'out'})")

    def test_clean_folder(self):
        fake_out = self.test_folder / "out"
        fake_out.mkdir()
        assert fake_out.is_dir()
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["clean"])
        self.check_logs(f"Cleaning folder: {self.test_folder}")
        assert not fake_out.exists()

    def test_build(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--dry-run"])
        self.check_logs(["setup]] INFO 🛫 - Setup project configuration", "build]] INFO 🛠  - Build project artifacts", "9 built tasks"], check_order=True)

    def test_test(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--dry-run", "tests"])
        self.check_logs(["tests]] INFO 🤞 - Run automated tests", "11 built tasks"], check_order=True)

    def test_version(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["version"])
        self.check_logs(f" 👉 nmk     : {nmk_version}")

    def test_help(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["help"])
        self.check_logs(" 👉 nmk     : https://github.com/dynod/nmk/wiki")

    def test_tasks(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["tasks"])
        self.check_logs(" 👉 tasks         : 🗃  - List all available tasks")

    def test_git_version_config(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "gitVersion"])
        self.check_logs(f'Config dump: {{ "gitVersion": "{__version__[:5]}')

    def test_git_version_config_no_tag(self, monkeypatch):
        # Fake git subprocess behavior, to make "git describe --tags" failing
        real_run = subprocess.run
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check, capture_output, text, encoding, cwd, errors: subprocess.CompletedProcess(all_args, 1, "", "")
            if all_args[:3] == ["git", "describe", "--tags"]
            else real_run(all_args, check=check, capture_output=capture_output, text=text, encoding=encoding, cwd=cwd),
        )
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "gitVersion"])
        self.check_logs('Config dump: { "gitVersion": "0.0.0-')

    def test_git_version_config_no_git(self, monkeypatch):
        # Fake git subprocess behavior, to make all "git" commands failing
        monkeypatch.setattr(
            subprocess, "run", lambda all_args, check, capture_output, text, encoding, cwd, errors: subprocess.CompletedProcess(all_args, 1, "", "")
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

    def test_git_clean(self, monkeypatch):
        # Stub to avoid real git clean command executed
        monkeypatch.setattr(subprocess, "run", lambda args, cwd, check: None)
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["git.clean"])
        self.check_logs("Clean all git ignored files")

    def test_git_dirty(self, monkeypatch):
        # Stub to have "git status" command with empty return
        monkeypatch.setattr(
            subprocess, "run", lambda all_args, check, capture_output, text, encoding, cwd, errors: subprocess.CompletedProcess(all_args, 0, "", "")
        )
        prj = self.prepare_project("ref_base.yml")
        self.nmk(prj, extra_args=["git.dirty", "--config", '{"gitEnableDirtyCheck":true}'])
        self.check_logs("Check for modified files")

        # Stub to have "git status" command with some dirty files
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check, capture_output, text, encoding, cwd, errors: subprocess.CompletedProcess(
                all_args, 0, " M src/nmk_base/git.py\n M src/nmk_base/git.yml", ""
            ),
        )
        self.nmk(
            prj,
            extra_args=["git.dirty", "--config", '{"gitEnableDirtyCheck":true}'],
            expected_error="An error occurred during task git.dirty build: Current folder is dirty:",
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
            extra_args=["py.req", "--config", '{"venvFileDeps":["${PROJECTDIR}/somereq.txt"],"venvArchiveDeps":["${PROJECTDIR}/somearchive.tar.gz"]}'],
        )

        # Verify generated file
        with (self.test_folder / "requirements.txt").open() as f:
            content = f.read()
            assert "nmk" in content
            assert "SomeFakePackage" in content
            assert "somearchive.tar.gz" in content

    def test_venv_simple_update(self, monkeypatch):
        # Fake pip subprocess behavior
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check, capture_output, text, encoding, cwd, errors: subprocess.CompletedProcess(
                all_args, 0, "# Fake packages list\nsomePackage==1.2.3", ""
            ),
        )

        # Test a simple venv update
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["py.venv"])

        # Verify output files
        assert (self.test_folder / "venv").exists()
        output_req = self.test_folder / "out" / "requirements.txt"
        assert output_req.exists()
        with output_req.open() as f:
            assert "somePackage==1.2.3" in f.read()

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

    def test_buildenv_init(self, monkeypatch):
        # Fake pip subprocess behavior
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda all_args, check, capture_output, text=False, encoding="utf-8", cwd=None, errors=None: subprocess.CompletedProcess(
                all_args, 0, "# Fake packages list\nsomePackage==1.2.3", ""
            ),
        )

        # Fake venv path
        fake_venv = self.test_folder / "fakeVenv"
        if fake_venv.is_dir():
            shutil.rmtree(fake_venv)
        fake_venv_bin = fake_venv / ("Scripts" if is_windows() else "bin")
        fake_venv_activate = fake_venv_bin / "activate.d"
        fake_venv_activate.mkdir(parents=True, exist_ok=True)
        (fake_venv_activate / "00_init.sh").touch()
        (fake_venv_activate / "00_init.bat").touch()
        monkeypatch.setattr(BuildenvInitBuilder, "_venv_bin_path", lambda _: fake_venv_bin)

        # Force buildend loading scripts
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["buildenv", "--config", '{"buildenvInitForce": true}'])
        assert (self.test_folder / "buildenv.sh").is_file()
        assert (self.test_folder / "buildenv.cmd").is_file()
        assert (self.test_folder / "buildenv-loader.py").is_file()
        assert (fake_venv_activate / "01_nmk.sh").is_file()
