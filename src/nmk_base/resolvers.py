import subprocess

from nmk.model.keys import NmkRootConfig
from nmk.model.resolver import NmkStrConfigResolver


class GitVersionResolver(NmkStrConfigResolver):
    def get_value(self, name: str) -> str:
        # Get version from git
        cp = subprocess.run(
            ["git", "describe", "--tags", "--dirty"], cwd=self.model.config[NmkRootConfig.PROJECT_DIR].value, capture_output=True, text=True, check=True
        )
        return cp.stdout.splitlines(keepends=False)[0]
