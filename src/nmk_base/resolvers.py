from nmk.model.resolver import NmkStrConfigResolver


class GitVersionResolver(NmkStrConfigResolver):
    """
    Git version resolver for current project
    """

    def get_value(self, name: str) -> str:
        pass
