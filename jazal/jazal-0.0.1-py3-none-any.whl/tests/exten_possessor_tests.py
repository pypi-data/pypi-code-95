import pytest
from jazal import ExtensionPossessor


def test_init_none():
	suffixes = None
	ep = ExtensionPossessor(suffixes)
	assert ep.extension == ()
	assert ep.extension_to_str() == ""


def test_init_list_one_suffix():
	suffixes = [".docx"]
	ep = ExtensionPossessor(suffixes)
	assert ep.extension == (".docx",)
	assert ep.extension_to_str() == ".docx"


def test_init_tuple_one_suffix():
	suffixes = (".docx",)
	ep = ExtensionPossessor(suffixes)
	assert ep.extension == (".docx",)
	assert ep.extension_to_str() == ".docx"


def test_init_list_two_suffixes():
	suffixes = [".tar", ".gz"]
	ep = ExtensionPossessor(suffixes)
	assert ep.extension == (".tar", ".gz")
	assert ep.extension_to_str() == ".tar.gz"


def test_init_tuple_two_suffixes():
	suffixes = (".tar", ".gz")
	ep = ExtensionPossessor(suffixes)
	assert ep.extension == (".tar", ".gz")
	assert ep.extension_to_str() == ".tar.gz"


def test_init_exception():
	except_msg =\
		"The extension must be None or a list or tuple of suffixes."
	with pytest.raises(TypeError, match = except_msg):
		ep = ExtensionPossessor(3)
