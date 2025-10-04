import subprocess

from buildenv2.completion import ArgCompleteCompletionCommand
from buildenv2.extension import BuildEnvExtension, CompletionCommand


class NmkBaseBuildEnvExtension(BuildEnvExtension):
    def get_completion_commands(self) -> list[CompletionCommand]:
        # Simply handle completion for nmk
        return [ArgCompleteCompletionCommand("nmk")]

    def init(self, force: bool):
        # Check for init conditions
        if (
            (self.info.project_root is not None)
            and (self.info.project_root / "nmk.yml").is_file()  # Is it an nmk project?
            and (force or not (self.info.project_root / ".nmk").is_dir())  # Forced init, or first init (no .nmk dir yet)?
        ):
            # Run "nmk setup"
            subprocess.run([self.info.venv_bin / "nmk", "setup"] + (["--force"] if force else []), check=True, cwd=self.info.project_root)
