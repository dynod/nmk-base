"""
Python module for **nmk-base** venv tasks.
"""

from pathlib import Path
from typing import List

from nmk.model.builder import NmkTaskBuilder
from nmk.utils import run_pip

from nmk_base.common import TemplateBuilder


class VenvRequirementsBuilder(TemplateBuilder):
    """
    Builder for **py.req** task
    """

    def build(self, file_deps: List[str], template: str):
        """
        Build logic for **py.req** task:
        generates venv requirements file from template.

        :param file_deps: List of requirement files dependencies; merged content will be provided to template as **fileDeps** keyword
        :param template: Template file used for generation
        """

        file_requirements = []

        # Merge all files content
        for req_file in map(Path, file_deps):
            with req_file.open() as f:
                # Append file content + one empty line
                file_requirements.extend(f.read().splitlines(keepends=False))
                file_requirements.append("")

        # Write merged requirements file
        self.build_from_template(Path(template), self.main_output, {"fileDeps": file_requirements})


class VenvUpdateBuilder(NmkTaskBuilder):
    """
    Builder for **py.venv** task
    """

    def build(self, pip_args: str):
        """
        Build logic for **py.venv** task:
        calls **pip install** with generated requirements file, then **pip freeze** to list all dependencies in secondary output file.

        :param pip_args: Extra arguments to be used when invoking **pip install**
        """

        # Prepare outputs
        venv_folder = self.main_output
        venv_status = self.outputs[1]

        # Call pip and touch output folder
        run_pip(
            ["install"]
            + (["-r"] if self.main_input.suffix == ".txt" else [])
            + [str(self.main_input)]
            + (pip_args.strip().split(" ") if len(pip_args) else []),
            logger=self.logger,
        )
        venv_folder.touch()

        # Dump installed packages
        pkg_list = run_pip(["freeze"], logger=self.logger)
        with venv_status.open("w") as f:
            f.write(pkg_list)
