"""
Python module for **nmk-base** loadme tasks.
"""

from typing import Dict, List

from nmk_base.common import TemplateBuilder


class BuildLoadMe(TemplateBuilder):
    """
    Builder for **loadme** task
    """

    def _prepare_deps(self, deps: Dict[str, Dict[str, str]], source: str) -> Dict[str, str]:
        # Builds a map of filtered source URLs for given install method.
        return {
            name: " ".join(sources[source]) if isinstance(sources[source], list) else sources[source]
            for name, sources in filter(lambda t: source in t[1], deps.items())
        }

    def build(self, deps: Dict[str, Dict[str, str]], venv_pythons: List[str]):
        """
        Build logic for **loadme** task:
        trigger loadme script generation from template, with required dependencies source URLs.

        :param deps: Maps of source URLs, indexed by name, then by install method (apt, http, ...)
        :param venv_pythons: List of python executable name in venv
        """

        # Prepare sysdeps list per keys
        apt_deps = self._prepare_deps(deps, "apt")
        url_deps = self._prepare_deps(deps, "url")
        kwargs = {
            "aptDeps": apt_deps,
            "urlDeps": url_deps,
        }

        # Iterate on combination of templates, outputs and venv command
        for template, output, venv_python in zip(self.inputs, self.outputs, venv_pythons):
            specific_kwargs = {"pythonForVenv": venv_python}
            specific_kwargs.update(kwargs)
            self.build_from_template(template, output, specific_kwargs)
