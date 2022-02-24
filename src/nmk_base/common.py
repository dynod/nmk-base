from pathlib import Path
from typing import Dict

from jinja2 import Template

from nmk.model.builder import NmkTaskBuilder


class TemplateBuilder(NmkTaskBuilder):
    """
    Common builder logic to generate files from templates
    """

    def build_from_template(self, template: Path, output: Path, kwargs: Dict[str, str]):
        # Prepare keywords
        all_kw = {"nmkBaseVersion": self.model.config["nmkPluginsVersions"].value["base"]}
        all_kw.update(kwargs)

        # Load template
        self.logger.debug(f"Generating {output} from template {template}")
        with template.open() as f, output.open("w") as o:
            # Render it
            t = Template(f.read())
            o.write(t.render(all_kw))
