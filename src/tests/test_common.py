from pathlib import Path

from nmk.tests.tester import NmkBaseTester


# Tests for common utilities
class TestBasePlugin(NmkBaseTester):
    @property
    def templates_root(self) -> Path:
        return Path(__file__).parent / "templates"

    def test_template_builder_sh(self):
        prj = self.prepare_project("test_template_builder.yml")
        self.prepare_project("sample.jinja")
        self.nmk(prj, extra_args=["sample.sh", "sample.bat"])
        assert (self.test_folder / "out/generated.sh").is_file()
        assert (self.test_folder / "out/generated.bat").is_file()
