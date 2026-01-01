import subprocess

from buildenv.completion import ArgCompleteCompletionCommand
from buildenv.extension import BuildEnvExtension, CompletionCommand


class NmkBaseBuildEnvExtension(BuildEnvExtension):
    def get_completion_commands(self) -> list[CompletionCommand]:
        # Simply handle completion for nmk
        return [ArgCompleteCompletionCommand("nmk")]

    def init(self, force: bool):
        # Nothing to do if no project
        if self.info.project_root is None:
            return

        # Check for init conditions
        if (
            (self.info.project_root / "nmk.yml").is_file()  # Is it an nmk project?
            and (force or (not (self.info.project_root / ".nmk").is_dir()))  # Auto-force if first init (no .nmk dir yet)
        ):
            # Run "nmk setup"
            subprocess.run([self.info.venv_bin / "nmk", "setup", "--force"], check=True, cwd=self.info.project_root)
