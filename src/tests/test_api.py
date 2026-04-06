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
        self.nmk(self.prepare_project("ref_base_resolver.yml"), extra_args=["--print", "barConfig"])
        self.check_logs(f'Config dump: {{ "barConfig": [ {self.jsonify(self.test_folder / "base_sample.py")} ] }}')

    def test_download_simple(self):
        self.nmk(self.prepare_project("ref_base_download.yml"), extra_args=["download_raw"])
        assert (self.test_folder / "sample.zip").is_file()

    def test_download_n_extract(self):
        self.nmk(self.prepare_project("ref_base_download.yml"), extra_args=["download_n_extract"])
        assert (self.test_folder / "sample_dir" / "nmk-base-1.2.0" / "nmk.yml").is_file()

    def test_bad_download(self):
        self.nmk(self.prepare_project("ref_base_download.yml"), extra_args=["bad_download"], expected_rc=1)
        self.check_logs("Error while importing request function foo.bar.download: No module named 'foo'")

    def test_download_not_an_archive(self):
        self.nmk(self.prepare_project("ref_base_download.yml"), extra_args=["download_not_an_archive"], expected_rc=1)
        self.check_logs("Unknown archive format")
