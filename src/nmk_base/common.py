from pathlib import Path
from typing import Dict, List

from jinja2 import Template
from nmk.model.builder import NmkTaskBuilder


class TemplateBuilder(NmkTaskBuilder):
    """
    Common builder logic to generate files from templates
    """

    def get_windows_endings_files(self) -> List[str]:
        return [".bat"]

    def build_from_template(self, template: Path, output: Path, kwargs: Dict[str, str]) -> str:
        # Prepare keywords
        all_kw = dict(kwargs)

        # Load template
        self.logger.debug(f"Generating {output} from template {template}")
        with template.open() as f, output.open(
            "w", newline="\r\n" if (output.suffix is not None and output.suffix.lower() in self.get_windows_endings_files()) else "\n"
        ) as o:
            # Render it
            t = Template(f.read())
            out = t.render(all_kw)
            o.write(out)
            return out
