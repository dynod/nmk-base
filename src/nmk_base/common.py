import subprocess
from pathlib import Path
from typing import Dict, List

from jinja2 import Template

from nmk.logs import NmkLogger
from nmk.model.builder import NmkTaskBuilder


def run_with_logs(args: List[str], logger=NmkLogger, check: bool = True, cwd: Path = None) -> subprocess.CompletedProcess:
    logger.debug(f"Running command: {args}")
    cp = subprocess.run(args, check=False, capture_output=True, text=True, encoding="utf-8", cwd=cwd)
    logger.debug(f">> rc: {cp.returncode}")
    logger.debug(">> stderr:")
    list(map(logger.debug, cp.stderr.splitlines(keepends=False)))
    logger.debug(">> stdout:")
    list(map(logger.debug, cp.stdout.splitlines(keepends=False)))
    assert not check or cp.returncode == 0, f"pip returned {cp.returncode}"
    return cp


class TemplateBuilder(NmkTaskBuilder):
    """
    Common builder logic to generate files from templates
    """

    def build_from_template(self, template: Path, output: Path, kwargs: Dict[str, str]):
        # Prepare keywords
        all_kw = {"nmkBaseVersion": self.model.config["nmkPluginsVersions"].value["base"]}
        all_kw.update(kwargs)

        # Load template
        self.logger.debug(f"Generating {output} from template {template}")
        with template.open() as f, output.open("w") as o:
            # Render it
            t = Template(f.read())
            o.write(t.render(all_kw))
