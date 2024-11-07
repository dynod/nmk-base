import shutil
from pathlib import Path

from nmk.tests.tester import NmkBaseTester
from tomlkit.toml_file import TOMLFile


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
        assert not output.is_file()
        self.check_logs("Python 3.")

        # Test 3
        (self.test_folder / "process_try2_input.txt").touch()
        self.nmk(prj, extra_args=["process_try3"])
        assert output.is_file()

    def test_toml_file_missing_config(self):
        file_fragment = self.test_folder / "missing_var.toml"
        shutil.copyfile(self.template("missing_var.toml"), file_fragment)
        self.nmk(
            self.prepare_project("toml_build_missing_var.yml"),
            extra_args=["generate.toml"],
            expected_error=f"An error occurred during task generate.toml build: While loading toml file template ({file_fragment}): Unknown config items referenced from template {self.test_folder / 'missing_var.toml'}: unknownConfig",
        )

    def test_toml_file_ok(self):
        shutil.copyfile(self.template("setup1.toml"), self.test_folder / "setup1.toml")
        shutil.copyfile(self.template("setup2.toml"), self.test_folder / "setup2.toml")
        self.nmk(
            self.prepare_project("toml_build_ok.yml"),
            extra_args=["generate.toml"],
        )
        generated_file = self.test_folder / "out" / "someFile.toml"
        assert generated_file.is_file()

        # Verify merged content
        doc = TOMLFile(generated_file).read()
        assert doc["dummy"]["foo"] == "bar"
        assert doc["dummy"]["bar"] == "venv"
        assert doc["dummy"]["other"] == "1,2,3"
        assert doc["dummy"]["ymlContributedValue"] == "foo"
        assert doc["dummy"]["someIntValue"] == 456
        assert doc["dummy"]["kwContrib"] == "wow"
        assert doc["anotherSection"]["foo"] == "bar"
        assert doc["anotherSection"]["arrayOfValues"] == ["azerty", "abc", "def"]
        assert doc["anotherSection"]["with_some_path"] == "src/foo"
