import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from buildenv.extension import BuildEnvProjectTemplate, BuildEnvRenderer
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from typing_extensions import Self

_LOGGER = logging.getLogger("nmk-base.template")

NmkConfigType = str | bool | list[str] | dict[str, Any]
"""Nmk config item types"""


def _to_commented(obj: dict[str, Any] | list[Any] | Any, comments: dict[str, str], path: str = "") -> CommentedMap | list[CommentedMap] | Any:
    comments = comments or {}
    if isinstance(obj, dict):
        cm = CommentedMap()
        for k, v in obj.items():  # type: ignore
            subpath = f"{path}.{k}" if path else str(k)  # type: ignore
            cm[k] = _to_commented(v, comments, subpath)  # type: ignore
            if subpath in comments:
                cm.yaml_set_comment_before_after_key(  # type: ignore
                    k,
                    before=comments[subpath],
                    indent=(len(subpath.split(".")) - 1) * 2,
                )
        return cm
    elif isinstance(obj, list):
        return [_to_commented(i, comments, path) for i in obj]  # type: ignore
    else:
        return obj


def dict_to_yaml_with_comments(data: dict[str, Any], comments: dict[str, str], dest_file: Path):
    """
    Dump `data` (a dict) to YAML with comments.
    """
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.allow_unicode = True
    commented = _to_commented(data, comments or {}, "")
    assert isinstance(commented, CommentedMap), "Top-level data must be a dict"
    with dest_file.open("w", encoding="utf-8") as f:
        yaml.dump(commented, f)  # type: ignore


@dataclass
class NmkReference:
    """
    Nmk reference definition
    """

    ref: str
    """
    Reference string, without the pip prefix, e.g. `nmk-base!plugin.yml`
    """

    included_refs: list[str] = field(default_factory=list[str])
    """List of included references, e.g. `nmk-python!plugin.yml` may include `nmk-base!plugin.yml`"""


class NmkBaseProjectTemplate(BuildEnvProjectTemplate):
    """
    Base project template for nmk projects

    This template is extendable by plugins, to provide extra:
    - references
    - config items
    - tasks to be called after project files generation
    """

    @property
    def description(self) -> str:
        return "base nmk project, without any plugin"

    @property
    def generated_files(self) -> set[Path]:
        return super().generated_files | set(
            [
                Path("nmk.yml"),
                Path("requirements.txt"),
                Path(".gitattributes"),
                Path(".gitignore"),
            ]
        )

    @property
    def references(self) -> list[NmkReference]:
        """
        Get the list of references for this template, to be added to the generated nmk.yml file.
        """
        return [NmkReference(ref="nmk-base!plugin.yml")]

    @property
    def comments(self) -> dict[str, str]:
        """
        Get the comments for the generated nmk.yml file, as a dict where keys are the paths to the items in the nmk.yml file
        (using dot notation for nested items), and values are the comments to be added before those items.
        """
        return {
            "refs": "Plugin references",
            "config": "\nProject configuration",
            "config.venvPkgDeps": "\nProject package dependencies",
            "config.venvArchiveDeps": "\nProject package dependencies (from local files)",
        }

    @property
    def config_items(self) -> dict[str, NmkConfigType]:
        """
        Get the config items to be added to the generated nmk.yml file, as a dict.
        """

        # By default, no extra config
        return {}

    def handle_dependencies(self, packages: list[str]) -> dict[str, NmkConfigType]:
        """
        Handle the dependencies of the project, and return the config items to be added to the generated nmk.yml file, as a dict.
        """

        # Iterate on packages
        config_items: dict[str, NmkConfigType] = {}
        simple_refs: list[str] = []
        file_refs: list[str] = []
        for package in map(lambda x: x.split(":")[-1], packages):  # Ignore dependency groups, if any (e.g. `dev:package` -> `package`)
            if "." in package:
                package_path = Path(package)
                if package_path.is_absolute() and package_path.is_file():
                    file_refs.append(package)
                elif (Path.cwd() / package).is_file():
                    file_refs.append(f"${{PROJECTDIR}}/{package}")
                else:
                    simple_refs.append(package)
            else:
                simple_refs.append(package)

        # Build settings
        if simple_refs:
            config_items["venvPkgDeps"] = simple_refs
        if file_refs:
            config_items["venvArchiveDeps"] = file_refs

        return config_items

    @property
    def post_generation_tasks(self) -> list[str]:
        """
        Get the list of tasks to be called after project files generation, as a list of strings.
        """
        return ["git.attributes", "git.ignore", "py.req"]

    # Build references list
    def _setup_references(self, nmk_templates: list[Self]) -> list[str]:
        references: list[str] = []
        for nmk_template in nmk_templates:
            for declared_def in nmk_template.references:
                if declared_def.ref not in references:
                    # Add to references list if not done yet
                    references.append(declared_def.ref)
                for included_ref in declared_def.included_refs:
                    # Remove any included ref that is already in the list, to avoid duplicates
                    if included_ref in references:
                        references.remove(included_ref)
        return references

    # Build config tree
    def _setup_config(self, nmk_templates: list[Self], packages: list[str]) -> dict[str, NmkConfigType]:
        config_items: dict[str, NmkConfigType] = self.handle_dependencies(packages)
        for nmk_template in nmk_templates:
            config_items.update(nmk_template.config_items)
        return config_items

    # Build comments dict
    def _setup_comments(self, nmk_templates: list[Self]) -> dict[str, str]:
        comments: dict[str, str] = {}
        for nmk_template in nmk_templates:
            comments.update(nmk_template.comments)
        return comments

    # Build tasks list
    def _setup_tasks(self, nmk_templates: list[Self]) -> list[str]:
        tasks: list[str] = []
        for nmk_template in nmk_templates:
            for task in nmk_template.post_generation_tasks:
                if task not in tasks:
                    tasks.append(task)
        return tasks

    # Generate extra files before calling nmk, if needed
    def _generate_extra_files(self, nmk_templates: list[Self], renderer: BuildEnvRenderer):
        # Delegate to other templates first
        for nmk_template in nmk_templates[1:]:  # Skip self
            nmk_template.generate_extra_files(renderer)

        # Generate extra files for self
        self.generate_extra_files(renderer)

    def generate_extra_files(self, renderer: BuildEnvRenderer):
        """
        Generate extra template files, before calling nmk to finalize the project install.
        """
        pass

    def generate_project_files(self, renderer: BuildEnvRenderer, packages: list[str], extra_templates: list[BuildEnvProjectTemplate]):
        # Don't generate nmk.yml if it already exists, to avoid overwriting user changes
        assert self.info.project_root
        assert self.info.project_root.is_dir()
        if (self.info.project_root / "nmk.yml").is_file():
            _LOGGER.info("Skip nmk.yml generation (already exist in this project)")
            return

        # Check for extra nmk templates
        all_nmk_templates: list[Self] = [self] + [t for t in extra_templates if isinstance(t, NmkBaseProjectTemplate) and t is not self]  # type: ignore

        # Handle references and config items
        references = self._setup_references(all_nmk_templates)
        config_items = self._setup_config(all_nmk_templates, packages)

        # Amend config, if any
        project_def: dict[str, list[str] | dict[str, NmkConfigType]] = {"refs": list(map(lambda x: f"pip://{x}", references))}
        if config_items:
            project_def["config"] = config_items

        # Generate nmk.yml with comments
        _LOGGER.info("Generate nmk.yml")
        dict_to_yaml_with_comments(project_def, self._setup_comments(all_nmk_templates), self.info.project_root / "nmk.yml")

        # Delegate other templatefiles generation
        self._generate_extra_files(all_nmk_templates, renderer)

        # Call nmk to generate other files
        subprocess.run(["nmk"] + self._setup_tasks(all_nmk_templates), cwd=self.info.project_root, check=True)

        # Clean output folders created by nmk
        for folder in [".nmk", "out"]:
            path = self.info.project_root / folder
            if path.is_dir():
                shutil.rmtree(path)
