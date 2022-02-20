import shutil
from pathlib import Path
from typing import Dict, List

from jinja2 import Template
from rich.emoji import Emoji

from nmk import __version__
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
    def build(self, deps: Dict[str, str], venv_pythons: List[str]):
        # Iterate on outputs
        for template, output, venv_python in zip(self.task.inputs, self.task.outputs, venv_pythons):
            # Load template
            self.logger.debug(f"Generating {output} from template {template}")
            with template.open() as f, output.open("w") as o:
                # Render it
                t = Template(f.read())
                o.write(t.render({"pythonForVenv": venv_python}))


class VersionBuilder(NmkTaskBuilder):
    def build(self, plugins: Dict[str, str]):
        # Displays all versions
        all_versions = {"nmk": __version__}
        all_versions.update(plugins)
        for name, version in all_versions.items():
            self.logger.info(self.task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {version}")


class HelpBuilder(NmkTaskBuilder):
    def build(self, links: Dict[str, str]):
        # Displays all online help links
        all_links = {"nmk": "https://github.com/dynod/nmk/wiki"}
        all_links.update(links)
        for name, link in all_links.items():
            self.logger.info(self.task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {link}")


class TaskListBuilder(NmkTaskBuilder):
    def build(self):
        # Iterate on all model tasks
        for name, task in self.model.tasks.items():
            self.logger.info(task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {task.description}")
