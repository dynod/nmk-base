"""
Python module for **nmk-base** env backends handling.
"""

from pathlib import Path

from nmk._internal.envbackend import EnvBackend, EnvBackendFactory
from nmk.model.keys import NmkRootConfig
from nmk.model.model import NmkModel
from nmk.model.resolver import NmkBoolConfigResolver, NmkStrConfigResolver


# Common logic to access to the backend from the project path
def get_backend(model: NmkModel) -> EnvBackend:
    # Resolve backend from project path
    v = model.config[NmkRootConfig.PROJECT_DIR].value
    assert isinstance(v, Path)
    return EnvBackendFactory.detect(v)


class VenvNameResolver(NmkStrConfigResolver):
    """
    Resolver for the virtual environment folder name from the backend.
    """

    def get_value(self, name: str) -> str:
        """
        Get the virtual environment folder name from the backend.

        :param name: The config name
        """
        return get_backend(self.model).venv_name


class BackendUseRequirementsResolver(NmkBoolConfigResolver):
    """
    Resolver to know if the backend uses requirements files.
    """

    def get_value(self, name: str) -> bool:
        """
        State if the backend uses requirements files.

        :param name: The config name
        """
        return get_backend(self.model).use_requirements


class BuildenvRefreshResolver(NmkBoolConfigResolver):
    """
    Resolver to know if the backend supports buildenv scripts refresh (legacy mode)
    """

    def get_value(self, name: str) -> bool:
        """
        State if the backend supports buildenv scripts refresh.

        :param name: The config name
        """
        return get_backend(self.model).is_legacy()
