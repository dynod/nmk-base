"""
Python module for **nmk-base** env backends handling.
"""

from pathlib import Path

from nmk._internal.envbackend import EnvBackend, EnvBackendFactory
from nmk.model.keys import NmkRootConfig
from nmk.model.resolver import NmkBoolConfigResolver, NmkConfigResolver, NmkStrConfigResolver


# Common logic to access to the backend from the project path
class _EnvBackendResolver(NmkConfigResolver):
    @property
    def backend(self) -> EnvBackend:
        # Resolve backend from project path
        v = self.model.config[NmkRootConfig.PROJECT_DIR].value
        assert isinstance(v, Path)
        return EnvBackendFactory.detect(v)


class VenvNameResolver(NmkStrConfigResolver, _EnvBackendResolver):
    """
    Resolver for the virtual environment folder name from the backend.
    """

    def get_value(self, name: str) -> str:
        """
        Get the virtual environment folder name from the backend.

        :param name: The config name
        """
        return self.backend.venv_name


class BackendUseRequirementsResolver(NmkBoolConfigResolver, _EnvBackendResolver):
    """
    Resolver to know if the backend uses requirements files.
    """

    def get_value(self, name: str) -> bool:
        """
        State if the backend uses requirements files.

        :param name: The config name
        """
        return self.backend.use_requirements
