"""
Python module for **nmk-base** venv tasks.
"""

import sys
from pathlib import Path

from nmk.model.builder import NmkTaskBuilder
from nmk.model.resolver import NmkListConfigResolver, NmkStrConfigResolver

from .backends import get_backend


class ExeResolver(NmkStrConfigResolver):
    """
    Resolver class for **venvPython** config item
    """

    def get_value(self, name: str) -> str:
        """
        Resolution logic: returns sys.executable
        """
        return sys.executable


class BinResolver(NmkStrConfigResolver):
    """
    Resolver class for **venvBin** config item
    """

    def get_value(self, name: str) -> str:
        """
        Resolution logic: returns sys.executable parent folder
        """
        return str(Path(sys.executable).parent)


class FileDepsContentResolver(NmkListConfigResolver):
    """
    Resolver class for **venvFileDepsContent** config item
    """

    def get_value(self, name: str) -> list[str]:
        """
        Resolution logic: merge content from files listed in **venvFileDeps** config item
        """

        file_requirements: list[str] = []

        # Merge all files content
        req_file_list = self.model.config["venvFileDeps"].value
        assert isinstance(req_file_list, list)
        for req_file in map(Path, req_file_list):
            with req_file.open() as f:
                # Append file content + one empty line
                file_requirements.extend(f.read().splitlines(keepends=False))
                file_requirements.append("")

        return file_requirements


class VenvUpdateBuilder(NmkTaskBuilder):
    """
    Builder for **py.venv** task
    """

    def build(self, pip_args: str = "", requirements_updated: bool = False):
        """
        Build logic for **py.venv** task

        This logic depends on the backend used:
        - if the backend is not mutable, it just warns the user that requirements have been updated (+exit properly)
        - if the backend is mutable, it calls **pip install** with generated requirements file,
          then **pip freeze** to list all dependencies in secondary output file.

        :param pip_args: Extra arguments to be used when invoking **pip install**; deprecated, not used anymore
        :param requirements_updated: State if requirements file content was actually updated
        """

        # If backend is not mutable, just stop here
        backend = get_backend(self.model)
        if not backend.is_mutable():
            # Were requirements *really* updated?
            if requirements_updated:
                self.logger.warning("Requirements have been updated; please:")
                self.logger.warning("-- either exit and re-enter the environment to apply changes")
                self.logger.warning("-- or call 'buildenv2 upgrade' command to spawn a new upgraded environment")
                raise RuntimeError("Build stopped")
            else:
                # Nothing to do
                self.logger.debug("Requirements are up to date, nothing to do")
                self.main_output.touch()
        else:
            # Delegate to backend
            backend.upgrade()
            self.main_output.touch()

        # Dump installed packages
        venv_status = self.outputs[1]
        backend.lock(venv_status)
