"""
Python module for **nmk-base** helper tasks.
"""

from typing import Dict

from nmk import __version__
from nmk.model.builder import NmkTaskBuilder
from rich.emoji import Emoji


class VersionBuilder(NmkTaskBuilder):
    """
    Builder implementation for **version** task
    """

    def build(self, plugins: Dict[str, str]):
        """
        Build logic for **version** task:
        iterate on provided plugins version map and display them.

        :param plugins: Map of plugins versions
        """

        # Displays all versions
        all_versions = {"nmk": __version__}
        all_versions.update(plugins)
        for name, version in all_versions.items():
            self.logger.info(self.task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {version}")


class HelpBuilder(NmkTaskBuilder):
    """
    Builder implementation for **help** task
    """

    def build(self, links: Dict[str, str]):
        """
        Build logic for **help** task:
        iterate on provided plugins help links map and display them.

        :param links: Map of plugins help links
        """

        # Displays all online help links
        all_links = {"nmk": "https://github.com/dynod/nmk/wiki"}
        all_links.update(links)
        for name, link in all_links.items():
            self.logger.info(self.task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {link}")


class TaskListBuilder(NmkTaskBuilder):
    """
    Builder implementation for **tasks** task
    """

    def build(self):
        """
        Build logic for **tasks** task:
        iterate on build model tasks, and display them (with their emoji and description text)
        """

        # Iterate on all model tasks
        for name, task in ((k, self.model.tasks[k]) for k in sorted(self.model.tasks.keys())):
            self.logger.info(task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {task.description}")
