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

    def test_process_builder(self):
        prj = self.prepare_project("ref_base_process.yml")

        # Test 1
        (self.test_folder / "process_try1_input.txt").touch()
        output = self.test_folder / "process_try1_output.txt"
        if output.is_file():
            output.unlink()
        self.nmk(prj, extra_args=["process_try1"])
        assert output.is_file()

        # Test 2
        (self.test_folder / "process_try2_input.txt").touch()
        output = self.test_folder / "process_try2_output.txt"
        if output.is_file():
            output.unlink()
        self.nmk(prj, extra_args=["process_try2"])
        assert output.is_file()
        self.check_logs("Python 3.")
