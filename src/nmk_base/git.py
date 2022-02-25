import subprocess

from nmk_base.common import run_with_logs

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
        cwd = self.model.config[NmkRootConfig.PROJECT_DIR].value
        cp = run_with_logs(["git", "describe", "--tags", "--dirty"], cwd=cwd, check=False)
        if cp.returncode == 0:
            # At least one tag
            return cp.stdout.splitlines(keepends=False)[0]
        else:
            # Probably no tags, build the version by hand
            # 1. get latest commit
            cp = run_with_logs(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, check=False)
            if cp.returncode != 0:
                # Definitely not a git repo; use a default version
                return "0.0.0"
            ref = cp.stdout.splitlines(keepends=False)[0]

            # 2. get revisions count
            rev_count = run_with_logs(["git", "rev-list", "--count", ref], cwd=cwd).stdout.splitlines(keepends=False)[0]
            # 3. get hash
            rev_hash = run_with_logs(["git", "describe", "--always", "--dirty"], cwd=cwd).stdout.splitlines(keepends=False)[0]

            # Build version from parts
            return f"0.0.0-{rev_count}-g{rev_hash}"
