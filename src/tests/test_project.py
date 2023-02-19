from pathlib import Path

from nmk.tests.tester import NmkBaseTester


class TestBasePluginApi(NmkBaseTester):
    @property
    def templates_root(self) -> Path:
        return Path(__file__).parent / "templates"

    def test_resolver(self):
        self.nmk(self.prepare_project("ref_base.yml"), extra_args=["--print", "projectName", "--print", "projectAuthor"])
        self.check_logs('Config dump: { "projectName": "MyProject", "projectAuthor": "Project Author" }')
