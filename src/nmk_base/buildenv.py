"""
Python module for **buildenv** extension and tasks
"""

import sys
from argparse import Namespace
from pathlib import Path
from typing import cast

from buildenv import BuildEnvManager
from nmk.model.builder import NmkTaskBuilder
from nmk.model.keys import NmkRootConfig


class BuildenvInitBuilder(NmkTaskBuilder):
    """
    **buildenv** task builder -- legacy mode only
    """

    # Venv path access
    def _venv_bin_path(self) -> Path:  # pragma: no cover
        return Path(sys.executable).parent

    def build(self, force: bool):  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Triggers BuildEnvManager init, in order to refresh buildenv loading scripts
        """

        # Prepare manager
        m = BuildEnvManager(cast(Path, self.model.config[NmkRootConfig.PROJECT_DIR].value), self._venv_bin_path())

        # Trigger init, either in force mode (typically for tests) or in skip mode (nominal case)
        m.init(Namespace(force=force) if force else Namespace(skip=True))

        # Touch output files
        for f in self.outputs:
            f.touch()
