"""
Python module for **nmk-base** env backends handling.
"""

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


class BuildenvRefreshResolver(NmkBoolConfigResolver):
    """
    Resolver to know if the backend supports buildenv scripts refresh (legacy mode)
    """

    def get_value(self, name: str) -> bool:
        """
        State if the backend supports buildenv scripts refresh.

        :param name: The config name
        """
        return self.model.env_backend.is_legacy()
