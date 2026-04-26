import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from buildenv.extension import BuildEnvProjectTemplate, BuildEnvRenderer
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

_LOGGER = logging.getLogger("nmk-base.template")


def _to_commented(obj: dict[str, Any] | list[Any] | Any, comments: dict[str, str], path: str = "") -> CommentedMap | list[CommentedMap] | Any:
    comments = comments or {}
    if isinstance(obj, dict):
        cm = CommentedMap()
        for k, v in obj.items():  # type: ignore
            subpath = f"{path}.{k}" if path else str(k)  # type: ignore
            cm[k] = _to_commented(v, comments, subpath)  # type: ignore
            if subpath in comments:
                cm.yaml_set_comment_before_after_key(k, before=comments[subpath], indent=(len(subpath.split(".")) - 1) * 2)  # type: ignore
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


class NmkBaseProjectTemplate(BuildEnvProjectTemplate):
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

    def generate_project_files(self, renderer: BuildEnvRenderer, packages: list[str]):
        # Prepare nmk.yml definition
        _LOGGER.info("Generate nmk.yml")
        project_def: dict[str, list[str] | dict[str, list[str]]] = {"refs": ["pip://nmk-base!plugin.yml"]}
        config_items: dict[str, list[str]] = {}
        if packages:
            # Prepare packages
            simple_refs: list[str] = []
            file_refs: list[str] = []
            for package in packages:
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

        # Amend config, if any
        if config_items:
            project_def["config"] = config_items

        project_comments = {
            "refs": "Plugin references",
            "config": "\nProject configuration",
            "config.venvPkgDeps": "\nProject package dependencies",
            "config.venvArchiveDeps": "\nProject package dependencies (from local files)",
        }
        assert self.info.project_root
        assert self.info.project_root.is_dir()
        dict_to_yaml_with_comments(project_def, project_comments, self.info.project_root / "nmk.yml")

        # Call nmk to generate other files
        subprocess.run(["nmk", "git.attributes", "git.ignore", "py.req"], cwd=self.info.project_root, check=True)

        # Clean output folders created by nmk
        for folder in [".nmk", "out"]:
            path = self.info.project_root / folder
            if path.is_dir():
                shutil.rmtree(path)
