import subprocess

from buildenv2.completion import ArgCompleteCompletionCommand
from buildenv2.extension import BuildEnvExtension, CompletionCommand


class NmkBaseBuildEnvExtension(BuildEnvExtension):
    def get_completion_commands(self) -> list[CompletionCommand]:
        # Simply handle completion for nmk
        return [ArgCompleteCompletionCommand("nmk")]

    def init(self, force: bool):
        # Auto-force if first init (no .nmk dir yet)
        is_forced = force or ((self.info.project_root is not None) and not (self.info.project_root / ".nmk").is_dir())

        # Check for init conditions
        if (
            (self.info.project_root is not None)
            and (self.info.project_root / "nmk.yml").is_file()  # Is it an nmk project?
            and is_forced
        ):
            # Run "nmk setup"
            subprocess.run([self.info.venv_bin / "nmk", "setup"] + (["--force"] if is_forced else []), check=True, cwd=self.info.project_root)
