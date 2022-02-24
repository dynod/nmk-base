import re
import subprocess
import sys
from pathlib import Path
from typing import List

from nmk_base.common import TemplateBuilder

from nmk.model.builder import NmkTaskBuilder

# Pattern for pip list lines
PIP_LIST_PATTERN = re.compile("^([^ ]+) +([0-9][^ ]*)$")


class VenvRequirementsBuilder(TemplateBuilder):
    def build(self, package_deps: List[str], archive_deps: List[str], file_deps: List[str], template: str):
        file_requirements = []

        # Merge all files content
        for req_file in map(Path, file_deps):
            with req_file.open() as f:
                # Append file content + one empty line
                file_requirements.extend(f.read().splitlines(keepends=False))
                file_requirements.append("")

        # Write merged requirements file
        self.build_from_template(Path(template), self.main_output, {"fileDeps": file_requirements, "packageDeps": package_deps, "archiveDeps": archive_deps})


class VenvUpdateBuilder(NmkTaskBuilder):
    def pip(self, args: List[str]) -> str:
        all_args = [sys.executable, "-m", "pip"] + args
        self.logger.debug(f"Call pip: {all_args}")
        cp = subprocess.run(all_args, check=False, capture_output=True, text=True, encoding="utf-8")
        self.logger.debug(f">> rc: {cp.returncode}")
        self.logger.debug(">> stderr:")
        list(map(self.logger.debug, cp.stderr.splitlines(keepends=False)))
        self.logger.debug(">> stdout:")
        list(map(self.logger.debug, cp.stdout.splitlines(keepends=False)))
        assert cp.returncode == 0, f"pip returned {cp.returncode}"
        return cp.stdout

    def build(self, pip_args: str):
        # Prepare outputs
        venv_folder = self.main_output
        venv_status = self.outputs[1]

        # Call pip and touch output folder
        self.pip(["install", "-r", str(self.main_input)] + (pip_args.split(" ") if len(pip_args) else []))
        venv_folder.touch()

        # Dump installed packages
        raw_pkg_list = self.pip(["list"])
        pkg_list = ["# Packages installed for project build"] + list(
            map(lambda m: f"{m.group(1)}=={m.group(2)}", filter(lambda m: m is not None, map(PIP_LIST_PATTERN.match, raw_pkg_list.splitlines(keepends=False))))
        )
        with venv_status.open("w") as f:
            f.write("\n".join(pkg_list))
