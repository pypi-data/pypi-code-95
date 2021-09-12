from argparse import Action, ArgumentError, ArgumentParser, Namespace
from typing import Any, Dict, Optional, Sequence, Union

from ...utils.collections.dicts import merge_dicts


class StoreKV(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[str] = None,
    ) -> None:
        if isinstance(values, list):
            setattr(
                namespace,
                self.dest,
                merge_dicts(*[self.parse_kv(i) for i in values]),
            )

        if isinstance(values, str):
            setattr(namespace, self.dest, self.parse_kv(values))

    def parse_kv(self, string: str) -> Dict[str, str]:
        if not isinstance(string, str) or not "=" in string:
            raise ArgumentError(self, string)

        k, v = string.split("=", 1)  # pylint: disable = C0103
        return {k: v}
