import subprocess
from pathlib import Path
from typing import Any

import pytest
from buildenv.__main__ import buildenv
from pytest_multilog import TestHelper

from nmk_base._buildenv.template import camel_to_kebab


class TestTemplate(TestHelper):
    @pytest.fixture(autouse=True)
    def fake_env(self, monkeypatch: pytest.MonkeyPatch):
        # Fake a "no CI" environment
        monkeypatch.delenv("CI", raising=False)

        # Fake subprocess to catch git execution
        old_sub_process_run = subprocess.run

        def filter_git_command(args: list[str], *pargs: list[Any], **kwargs: dict[str, Any]) -> subprocess.CompletedProcess[str]:
            if args[0] == "git":
                return subprocess.CompletedProcess(args, 0, str(self.test_folder), "")
            return old_sub_process_run(args, *pargs, **kwargs)  # type: ignore

        monkeypatch.setattr(subprocess, "run", filter_git_command)

    def test_camel_to_kebab(self):
        assert camel_to_kebab("CamelCase") == "camel-case"
        assert camel_to_kebab("CamelCaseTest") == "camel-case-test"
        assert camel_to_kebab("CamelCaseTestX") == "camel-case-test-x"
        assert camel_to_kebab("CamelCaseTestXyz") == "camel-case-test-xyz"
        assert camel_to_kebab("CamelCaseTestXyzAbc") == "camel-case-test-xyz-abc"
        assert camel_to_kebab("") == ""

    def test_raw_template(self):
        # Prepare a project with uvx backend and base template
        install_args = [
            "install",
            "--template",
            "nmk",
            "--ignore-template",
            "nmk.doc",
            "--ignore-template",
            "nmk.vscode",
            "--ignore-template",
            "nmk.github",
            "-p",
            str(self.test_folder),
        ]
        assert buildenv(install_args) == 0

        # Check nmk.yml
        assert "nmk-base" in (self.test_folder / "nmk.yml").read_text()

        # Try install again (skipped)
        assert buildenv(install_args) == 0
        self.check_logs("Skip nmk.yml generation (already exist in this project)")

    def test_delete_ref(self):
        # Prepare a project with uvx backend and vscode template
        install_args = [
            "install",
            "--template",
            "nmk",
            "--ignore-template",
            "nmk.doc",
            "--extra-template",
            "nmk.vscode",
            "--ignore-template",
            "nmk.github",
            "-p",
            str(self.test_folder),
        ]
        assert buildenv(install_args) == 0

        # Check nmk.yml
        project_file_content = (self.test_folder / "nmk.yml").read_text()
        assert "nmk-base" not in project_file_content
        assert "nmk-vscode" in project_file_content

    def test_ignored_task(self):
        # Prepare a project with python plugin (ignoring py.req task)
        install_args = [
            "install",
            "--template",
            "nmk.python",
            "-p",
            str(self.test_folder),
        ]
        assert buildenv(install_args) == 0

    def test_extra_packages(self):
        # Prepare fake wheels
        fake_wheel = self.test_folder / "dummy-0.1.0-py3-none-any.whl"
        fake_wheel.write_text("dummy wheel content")

        # Prepare a project with uvx backend and base template
        install_args = [
            "install",
            "--template",
            "nmk",
            "--ignore-template",
            "nmk.doc",
            "--ignore-template",
            "nmk.vscode",
            "--ignore-template",
            "nmk.github",
            "-p",
            str(self.test_folder),
            "--add",
            "dummy.dotted.ref",  # Package name with dots...
            "--add",
            str(fake_wheel),  # Absolute file ref
            "--add",
            fake_wheel.name,  # Relative file ref
        ]
        assert buildenv(install_args) == 0

        # Check nmk.yml
        project_file_content = (self.test_folder / "nmk.yml").read_text()
        assert "- dummy.dotted.ref" in project_file_content
        assert "- ${PROJECTDIR}/dummy-0.1.0-py3-none-any.whl" in project_file_content
        assert str(Path("extra_packages/dummy-0.1.0-py3-none-any.whl")) in project_file_content
