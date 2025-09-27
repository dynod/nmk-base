import os
import subprocess
import sys
from pathlib import Path

from buildenv2.completion import ArgCompleteCompletionCommand
from buildenv2.extension import BuildEnvExtension, CompletionCommand

from nmk_base._buildenv import _ENV_VAR_NMK_IS_RUNNING  # pyright: ignore[reportPrivateUsage]


class NmkBaseBuildEnvExtension(BuildEnvExtension):
    def get_completion_commands(self) -> list[CompletionCommand]:
        # Simply handle completion for nmk
        return [ArgCompleteCompletionCommand("nmk")]

    def init(self, force: bool):
        # Is it an nmk project?
        if (self.info.project_root is not None) and (self.info.project_root / "nmk.yml").is_file() and (os.getenv(_ENV_VAR_NMK_IS_RUNNING) is None):
            # Run "nmk setup" with amended env
            patched_env = dict(os.environ)
            patched_env[_ENV_VAR_NMK_IS_RUNNING] = "1"
            subprocess.run(
                [Path(sys.executable).parent / "nmk", "setup"] + (["--force"] if force else []), check=True, cwd=self.info.project_root, env=patched_env
            )
