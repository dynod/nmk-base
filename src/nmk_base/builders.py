import shutil
from pathlib import Path

from nmk.model.builder import NmkTaskBuilder


class CleanOutputBuilder(NmkTaskBuilder):
    def build(self):
        # Check output path
        output = Path(self.model.config["outputDir"].value)
        if output.is_dir():
            # Clean it
            self.logger.debug(f"Cleaning output folder: {output}")
            shutil.rmtree(output)
        else:
            # Nothing to clean
            self.logger.debug(f"Nothing to clean (output folder not found: {output})")
