"""
Python module for base resolvers (to be used by other plugins).
"""

import shutil
from pathlib import Path
from typing import Any, cast

from nmk.logs import NmkLogger
from nmk.model.resolver import NmkConfigResolver, NmkDictConfigResolver, NmkListConfigResolver, NmkStrConfigResolver


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


_MultiChoiceValue = str | int | bool | list[Any] | dict[str, Any]


class MultiChoiceResolver(NmkConfigResolver):
    """
    Multi-choice config item resolver base class
    """

    def get_value(  # type: ignore
        self, name: str, key: int | str | bool, choices: dict[int | str | bool, _MultiChoiceValue], default: _MultiChoiceValue
    ) -> _MultiChoiceValue:
        """
        Resolve multi-choice config item value using provided key and available choices

        :param name: config item name
        :param key: key to select value
        :param choices: available choices
        :param default: default value
        :return: item value
        """
        return choices.get(key, default)


class MultiStrChoiceResolver(MultiChoiceResolver, NmkStrConfigResolver):  # type: ignore
    """
    Multi-choice string config item resolver class
    """

    pass


class MultiListChoiceResolver(MultiChoiceResolver, NmkListConfigResolver):  # type: ignore
    """
    Multi-choice list config item resolver class
    """

    pass


class MultiDictChoiceResolver(MultiChoiceResolver, NmkDictConfigResolver):  # type: ignore
    """
    Multi-choice dict config item resolver class
    """

    pass


class CommandResolver(NmkStrConfigResolver):
    """
    Command resolver class, allowing to resolve a command path.
    """

    def get_value(self, name: str, command: str, custom_path: str) -> str:  # type: ignore
        """
        Resolve command path (from custom path, if any, or from system path)

        :param name: config item name
        :param command: command name (to be resolved from system path)
        :param custom_path: custom path to be used for command resolution (overrides system path)
        :return: command path
        """

        # Provided path must be a file, if specified
        output = ""
        if custom_path:
            if Path(custom_path).is_file():
                # Custom path is OK, use it
                output = custom_path
                NmkLogger.debug(f"Using provided path for '{command}' command: {custom_path}")
            else:
                # Can't use it just warn about it
                NmkLogger.warning(f"Provided path for '{command}' command was not found: {custom_path}")

        # Detect from path if not already found
        if not output:
            system_path = shutil.which(command)
            if system_path is not None:
                output = command
                NmkLogger.debug(f"'{command}' command found in system path: {system_path}")
            else:
                NmkLogger.warning(f"'{command}' command was not found in system path")

        return output
