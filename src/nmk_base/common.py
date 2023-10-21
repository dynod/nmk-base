"""
Python module for **nmk-base** utility classes.
"""

from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, Template, meta
from nmk.model.builder import NmkTaskBuilder
from nmk.model.keys import NmkRootConfig


class TemplateBuilder(NmkTaskBuilder):
    """
    Common builder logic to generate files from templates
    """

    def get_windows_endings_files(self) -> List[str]:
        """
        Get file extensions typically known to use Windows line endings (CR+LF)

        :return: List of file extensions
        """
        return [".bat"]

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

        # Load template
        self.logger.debug(f"Generating {output} from template {template}")
        with output.open("w", newline="\r\n" if (output.suffix is not None and output.suffix.lower() in self.get_windows_endings_files()) else "\n") as o:
            # Render it
            out = self.render_template(template, kwargs)
            o.write(out)
            return out
