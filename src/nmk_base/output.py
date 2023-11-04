"""
Python module for **nmk-base** output tasks.
"""

import shutil
from pathlib import Path

from nmk.model.builder import NmkTaskBuilder


class CleanBuilder(NmkTaskBuilder):
    """
    Builder for **clean** task
    """

    def build(self, path: str):
        """
        Build logic for **clean** task:
        delete (recursively) provided directory, if it exists

        :param path: Directory to be deleted
        """

        # Check path
        to_delete = Path(path)
        if to_delete.is_dir():
            # Clean it
            self.logger.debug(f"Cleaning folder: {to_delete}")
            shutil.rmtree(to_delete)
        else:
            # Nothing to clean
            self.logger.debug(f"Nothing to clean (folder not found: {to_delete})")
