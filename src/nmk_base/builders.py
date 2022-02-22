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
    def prepare_deps(self, deps: Dict[str, Dict[str, str]], source: str) -> Dict[str, str]:
        return {
            name: " ".join(sources[source]) if isinstance(sources[source], list) else sources[source]
            for name, sources in filter(lambda t: source in t[1], deps.items())
        }

    def build(self, deps: Dict[str, Dict[str, str]], venv_pythons: List[str]):
        # Prepare sysdeps list per keys
        apt_deps = self.prepare_deps(deps, "apt")
        url_deps = self.prepare_deps(deps, "url")

        # Iterate on combination of templates, outputs and venv command
        for template, output, venv_python in zip(self.inputs, self.outputs, venv_pythons):
            # Load template
            self.logger.debug(f"Generating {output} from template {template}")
            with template.open() as f, output.open("w") as o:
                # Render it
                t = Template(f.read())
                o.write(
                    t.render(
                        {
                            "nmkBaseVersion": self.model.config["nmkPluginsVersions"].value["base"],
                            "pythonForVenv": venv_python,
                            "aptDeps": apt_deps,
                            "urlDeps": url_deps,
                        }
                    )
                )


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


class GitVersionRefresh(NmkTaskBuilder):
    def build(self, version: str):
        # Check if update is needed
        self.logger.debug(f"New version: {version}")
        do_update = True
        stamp_file = self.main_output
        if stamp_file.is_file():
            with stamp_file.open() as f:
                persisted_version = f.read().splitlines(keepends=False)[0]
                self.logger.debug(f"Previously persisted version: {persisted_version}")
                do_update = version != persisted_version
        if do_update:
            # Yep, update persisted version
            self.logger.info(self.task.emoji, self.task.description)
            stamp_file.parent.mkdir(exist_ok=True, parents=True)
            with stamp_file.open("w") as f:
                f.write(version)
        else:
            self.logger.debug("Persisted git version already up to date")
