from dataclasses import dataclass
from typing import Dict, Tuple

from marisa_trie import Trie

from .download import default_file_name, default_output_dir, download_csv
from .utils import normalize, read_japan_post_data
from .version import __version__  # noqa


@dataclass(frozen=True)
class Address:
    prefecture: str
    city: str
    district: str
    remained_address: str


class AddressParser:
    def __init__(self, addr_dict: Dict[str, Tuple[str, str, str]]) -> None:
        self._addr_dict = addr_dict
        self._trie = Trie(list(addr_dict.keys()))

    def query(self, address: str, do_normalization=True):
        """Find the logest match on the Trie

        Args:
            address (str): address string
            do_normalization (bool, optional): flag to run normalization. Defaults to True.

        Returns:
            str: matched key
        """
        if do_normalization:
            address = normalize(address)

        prefixes = self._trie.prefixes(address)
        if len(prefixes) == 0:
            return None

        best_match = max(prefixes, key=len)
        return best_match

    def parse(self, address: str, do_normalization=True):
        """Split the address string and return as an Address object

        Args:
            address (str): address string
            do_normalization (bool, optional): flag to run normalization. Defaults to True.

        Raises:
            ValueError: The query address does not math with any entry on the Trie

        Returns:
            Address: parsed Address object
        """
        if do_normalization:
            address = normalize(address)

        key = self.query(address)
        if key is None:
            raise ValueError("unkown address {}".format(address))

        prefecture, city, district = self._addr_dict[key]
        key_len = len(key)
        remained = address[key_len:]

        return Address(prefecture, city, district, remained)


_default_address_file = default_output_dir.joinpath(default_file_name)
_default_address_parser = None


def get_default_parser():
    """Download the data is not exists and return the default parser.

    Returns:
        AddressParser: the default parser
    """
    if not _default_address_file.exists():
        download_csv()
    global _default_address_parser
    _default_address_parser = AddressParser(
        read_japan_post_data(_default_address_file, encoding="sjis")
    )
    return _default_address_parser
