from nmk_base.resolvers import FilesResolver


class SampleResolver(FilesResolver):
    @property
    def folder_config(self) -> str:
        return "fooFolder"

    @property
    def extension(self) -> str:
        return "*.py"
