"""
Python module for base resolvers (to be used by other plugins).
"""

from pathlib import Path
from typing import cast

from nmk.model.resolver import NmkListConfigResolver


class FilesResolver(NmkListConfigResolver):
    """
    Base resolver class helping for files resolution.
    """

    @property
    def folder_config(self) -> str:  # pragma: no cover
        """
        Can be overridden by sub-classes. This property is used to identify the config item identifying the folder(s) where to search files.

        :return: Name of the config item holding the folder(s) to be searched for files; Default is "PROJECTDIR"
        """
        return "PROJECTDIR"

    @property
    def extension(self) -> str:  # pragma: no cover
        """
        Can be overridden by sub-classes. This property is used to identify the extension of files to be searched

        :return: Extension to be searched in folder(s); Default is "*.*"
        """
        return "*.*"

    def get_value(self, name: str, folder: str | list[str] | None = None, extension: str | None = None) -> list[Path]:
        """
        Files resolution logic:
        iterate on provided folders (from config item name), and filter on provided extension.

        :param name: Name of the config item to be resolved (not used in this resolver)
        :param folder: Specific folder(s) to search in (overrides folder_config property)
        :param extension: Specific extension to search for (overrides extension property)
        :return: List of found files
        """

        # Extension to be searched
        extension_to_search = extension if extension is not None else self.extension

        # Locate paths to be browsed
        if folder is not None:
            paths_to_browse: list[str] = folder if isinstance(folder, list) else [folder]
        else:
            path_config = self.model.config[self.folder_config].value
            paths_to_browse: list[str] = cast(list[str], path_config) if isinstance(path_config, list) else [cast(str, path_config)]

        # Iterate on paths, and find all files
        return [file for path in map(Path, paths_to_browse) for file in filter(lambda f: f.is_file(), path.rglob(extension_to_search))]
