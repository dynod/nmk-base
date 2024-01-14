"""
Python module for **buildenv** extension and tasks
"""

import sys
from argparse import Namespace
from pathlib import Path

from buildenv import BuildEnvExtension, BuildEnvManager
from nmk.model.builder import NmkTaskBuilder
from nmk.model.keys import NmkRootConfig
from nmk.utils import is_windows

from nmk_base import __version__


class BuildEnvInit(BuildEnvExtension):
    """
    Buildenv extension for **nmk**
    """

    def init(self, force: bool):
        """
        Buildenv init call back for nmk

        When called, this method:

        * registers **nmk** command for completion
        * adds activation scripts to call **nmk setup** command when buildenv is activated
        """

        # Register nmk command for CLI completion
        self.manager.register_completion("nmk")

        # Add nmk setup in activation files
        template = Path(__file__).parent / "templates" / "setup.jinja"
        for ext in [".sh"] + ([".bat"] if is_windows() else []):
            self.manager.add_activation_file("nmk", ext, template)

    def get_version(self) -> str:
        """
        Get extension version
        """

        return __version__


class BuildenvInitBuilder(NmkTaskBuilder):
    """
    **buildenv** task builder
    """

    # Venv path access
    def _venv_bin_path(self) -> Path:  # pragma: no cover
        return Path(sys.executable).parent

    def build(self, force: bool):
        """
        Triggers BuildEnvManager init, in order to refresh buildenv loadinf scripts
        """

        # Prepare manager
        m = BuildEnvManager(self.model.config[NmkRootConfig.PROJECT_DIR].value, self._venv_bin_path())

        # Trigger init
        m.init(Namespace(force=force))

        # Touch output files
        for f in self.outputs:
            f.touch()
