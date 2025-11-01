"""
Python module for **nmk-base** env backends handling.
"""

import os

from nmk.model.resolver import NmkBoolConfigResolver, NmkStrConfigResolver


class VenvNameResolver(NmkStrConfigResolver):
    """
    Resolver for the virtual environment folder name from the backend.
    """

    def get_value(self, name: str) -> str:
        """
        Get the virtual environment folder name from the backend.

        :param name: The config name
        """
        return self.model.env_backend.venv_name


class VenvRootResolver(NmkStrConfigResolver):
    """
    Resolver for the virtual environment root folder from the backend.
    """

    def get_value(self, name: str) -> str:
        """
        Get the virtual environment root folder from the backend.

        :param name: The config name
        """
        return str(self.model.env_backend.venv_root)


class BackendUseRequirementsResolver(NmkBoolConfigResolver):
    """
    Resolver to know if the backend uses requirements files.
    """

    def get_value(self, name: str) -> bool:
        """
        State if the backend uses requirements files.

        :param name: The config name
        """
        return self.model.env_backend.use_requirements


class BackendLegacyResolver(NmkBoolConfigResolver):
    """
    Resolver to know if the running backend is a legacy one (buildenv 1.X)
    """

    def get_value(self, name: str) -> bool:
        """
        State if the running backend is a legacy backend (buildenv 1.X)

        :param name: The config name
        """
        return os.getenv("BUILDENV_LEVEL") is None
