import subprocess

from nmk.errors import NmkStopHereError
from nmk.model.builder import NmkTaskBuilder
from nmk.model.keys import NmkRootConfig
from nmk.model.resolver import NmkStrConfigResolver


class GitVersionRefresh(NmkTaskBuilder):
    def build(self, version: str):
        # Check if update is needed
        self.logger.debug(f"New version: {version}")
        do_update = True
        stamp_file = self.main_output
        if stamp_file.is_file():
            with stamp_file.open() as f:
                persisted_version = f.read().splitlines(keepends=False)[0]
                self.logger.debug(f"Previously persisted version: {persisted_version}")
                do_update = version != persisted_version
        if do_update:
            # Yep, update persisted version
            self.logger.info(self.task.emoji, self.task.description)
            with stamp_file.open("w") as f:
                f.write(version)
        else:
            self.logger.debug("Persisted git version already up to date")


class GitClean(NmkTaskBuilder):
    def build(self):
        # Full clean, just warn before
        self.logger.warning("Clean all git ignored files; use loadme script to setup the project again")
        subprocess.run(["git", "clean", "-fdX"], cwd=self.model.config[NmkRootConfig.PROJECT_DIR].value, check=True)
        raise NmkStopHereError()


class GitVersionResolver(NmkStrConfigResolver):
    def get_value(self, name: str) -> str:
        # Get version from git
        cp = subprocess.run(
            ["git", "describe", "--tags", "--dirty"], cwd=self.model.config[NmkRootConfig.PROJECT_DIR].value, capture_output=True, text=True, check=True
        )
        return cp.stdout.splitlines(keepends=False)[0]
