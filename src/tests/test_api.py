from pathlib import Path

from nmk.tests.tester import NmkBaseTester


class TestBasePluginApi(NmkBaseTester):
    @property
    def templates_root(self) -> Path:
        return Path(__file__).parent / "templates"

    def jsonify(self, to_escape: Path) -> str:
        # Escape backslashes (for Windows paths in json print)
        return '"' + str(to_escape).replace("\\", "\\\\") + '"'

    def test_resolver(self):
        self.prepare_project("base_sample.py")
        self.nmk(self.prepare_project("ref_base_resolver.yml"), extra_args=["--print", "fooConfig"])
        self.check_logs(f'Config dump: {{ "fooConfig": [ {self.jsonify(self.test_folder / "base_sample.py")} ] }}')
