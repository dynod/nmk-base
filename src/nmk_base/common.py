"""
Python module for **nmk-base** utility classes.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Union

from jinja2 import Environment, Template, meta
from nmk.model.builder import NmkTaskBuilder
from nmk.model.keys import NmkRootConfig
from nmk.utils import run_with_logs


class TemplateBuilder(NmkTaskBuilder):
    """
    Generic builder logic to generate files from templates
    """

    def relative_path(self, v: str) -> str:
        """
        Make an absolute path as project relative if possible

        :param v: Path string to be converted
        :return: Project relative path (if possible); unchanged input value otherwise
        """
        v_path = Path(str(v))
        if v_path.is_absolute():
            try:
                return v_path.relative_to(self.model.config[NmkRootConfig.PROJECT_DIR].value).as_posix()
            except ValueError:  # pragma: no cover
                # Simply ignore, non project -relative
                pass
        return v

    def config_value(self, config_name: str) -> Any:
        """
        Get config value by name & turn absolute paths to project relative ones (if possible)

        :param config_name: Config item name
        :return: Config item value
        """
        v = self.model.config[config_name].value

        # Value processing depends on type
        if isinstance(v, str):
            # Single string
            return self.relative_path(v)
        elif isinstance(v, list):
            # Potentially a list of string
            return [self.relative_path(p) for p in v]

        # Probably nothing to do with path, use raw value
        return v  # pragma: no cover

    def render_template(self, template: Path, kwargs: Dict[str, str]) -> str:
        """
        Render template into a string, with provided keywords and config items

        :param template: Path to template file to be rendered
        :param kwargs: Map of keywords for templates rendering, indexed by name
        :return: Rendered template string
        :throw: AssertionError if unknown keyword is referenced in template
        """

        # Load template
        with template.open() as f:
            # Render it
            template_source = f.read()

        # Look for required config items
        required_items = meta.find_undeclared_variables(Environment().parse(template_source))
        unknown_items = list(filter(lambda x: x not in kwargs and x not in self.model.config, required_items))
        assert len(unknown_items) == 0, f"Unknown config items referenced from template {template}: {', '.join(unknown_items)}"

        # Render
        all_kw = {c: self.config_value(c) for c in filter(lambda x: x not in kwargs, required_items)}
        all_kw.update(kwargs)
        return Template(template_source).render(all_kw)

    def build_from_template(self, template: Path, output: Path, kwargs: Dict[str, str]) -> str:
        """
        Generate file from template

        :param template: Path to template file to be rendered
        :param output: Path to output file to be generated
        :param kwargs: Map of keywords for templates rendering, indexed by name
        :return: Rendered template string
        :throw: AssertionError if unknown keyword is referenced in template
        """

        # By default, keep system-defined line endings
        line_endings = None
        if output.suffix is not None:  # pragma: no branch
            # Check for forced line endings
            suffix = output.suffix.lower()

            if suffix in self.model.config["linuxLineEndings"].value:
                # Always generate with Linux line endings
                line_endings = "\n"

            if suffix in self.model.config["windowsLineEndings"].value:
                # Always generate with Windows line endings
                line_endings = "\r\n"

        # Load template
        self.logger.debug(f"Generating {output} from template {template}")
        with output.open("w", newline=line_endings) as o:
            # Render it
            out = self.render_template(template, kwargs)
            o.write(out)
            return out

    def build(self, template: str):
        """
        Default build behavior: generate main output file from provided template

        :param template: Path to the Jinja template to use for generation
        """

        # Just build from template
        self.build_from_template(Path(template), self.main_output, {})


class MkdirBuilder(NmkTaskBuilder):
    """
    Generic builder logic to create directory
    """

    def build(self):
        """
        Build logic:
        create specified directory (main output of the task)
        """

        # Create directory
        self.main_output.mkdir(parents=True, exist_ok=True)


class ProcessBuilder(NmkTaskBuilder):
    """
    Generic builder logic to call a sub-process
    """

    def build(self, cmd: Union[str, List[str]], verbose: bool = False):
        """
        Build logic:

        * call subprocess specified through **cmd** parameter; process is invoked in project directory
        * depending on the **verbose** parameter, redirect output to stdout (if True) or to nmk logs (if False)
        * touch the specified output file

        :param cmd: process command line; may be a string or a list of parameters
        :param verbose: states if the process output shall be displayed in stdout or saved in logs
        """

        # Split args if cmd is a string
        args = cmd if isinstance(cmd, list) else cmd.split(" ")

        if verbose:
            # Verbose: process output will go to stdout/stderr
            self.logger.debug(f"Running command: {args}")
            subprocess.run(args, cwd=self.model.config[NmkRootConfig.PROJECT_DIR].value, check=True)
        else:
            # Redirect output to logs
            run_with_logs(args, cwd=self.model.config[NmkRootConfig.PROJECT_DIR].value, check=True)

        # Touch main output file
        self.main_output.touch()
