from collections import Sequence


class LazyPoliciesDefaultSequence(Sequence):
    """
    Since the path to iba_mgmt and dde_snapshot may not be loaded yet when this module is loaded, using sequence
    that only imports dde_snapshot when it is accessed.
    """
    def __getitem__(self, index):
        from iba_api.server.models import OriginatedByType

        if index == 0:
            return OriginatedByType.SYSTEM_POLICY
        elif index == 1:
            return OriginatedByType.USER_POLICY
        else:
            return super().__getitem__(index)

    def __len__(self):
        return 2


POLICIES_BLUEPRINT = {
    "default": LazyPoliciesDefaultSequence()
}
