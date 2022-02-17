import shutil
from pathlib import Path
from typing import Dict

from jinja2 import Template

from nmk.model.builder import NmkTaskBuilder


class CleanBuilder(NmkTaskBuilder):
    def build(self, path: str):
        # Check path
        to_delete = Path(path)
        if to_delete.is_dir():
            # Clean it
            self.logger.debug(f"Cleaning folder: {to_delete}")
            shutil.rmtree(to_delete)
        else:
            # Nothing to clean
            self.logger.debug(f"Nothing to clean (folder not found: {to_delete})")


class BuildLoadMe(NmkTaskBuilder):
    def build(self, deps: Dict[str, str], venv_python: str):
        # Iterate on outputs
        for template, output in zip(self.task.inputs, self.task.outputs):
            # Load template
            self.logger.debug(f"Generating {output} from template {template}")
            with template.open() as f, output.open("w") as o:
                # Render it
                t = Template(f.read())
                o.write(t.render({"linuxVenvPython": venv_python}))
