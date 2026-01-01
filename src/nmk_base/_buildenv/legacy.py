import os
import subprocess
import sys
from pathlib import Path

from buildenv import BuildEnvExtension, BuildEnvManager

from nmk_base import __version__
from nmk_base._buildenv import _ENV_VAR_NMK_IS_RUNNING  # pyright: ignore[reportPrivateUsage]


class BuildEnvInit(BuildEnvExtension):
    """
    Buildenv extension for **nmk**
    """

    def init(self, force: bool):
        """
        Buildenv init call back for nmk

        When called, this method:

        * registers **nmk** command for completion
        * calls **nmk setup** if project contains an **nmk.yml** file
        """

        # Register nmk command for CLI completion
        self.manager: BuildEnvManager
        self.manager.register_completion("nmk")

        # Check for nmk project file
        prj = self.manager.project_path / "nmk.yml"
        if prj.is_file() and os.getenv(_ENV_VAR_NMK_IS_RUNNING) is None:
            # Run "nmk setup" with amended env
            patched_env = dict(os.environ)
            patched_env[_ENV_VAR_NMK_IS_RUNNING] = "1"
            subprocess.run([Path(sys.executable).parent / "nmk", "setup"], check=True, cwd=self.manager.project_path, env=patched_env)

    def get_version(self) -> str:
        """
        Get extension version
        """

        return __version__
