import pytest
from pathlib import Path
from jazal import\
	extension_to_str,\
	get_file_stem,\
	make_altered_name,\
	make_altered_path,\
	make_altered_stem


EMPTY_STR = ""


def assert_exten_str(path_str, expected_exten):
	p = Path(path_str)
	exten_str = extension_to_str(p)
	assert exten_str == expected_exten


def assert_file_stem(path_str, expected_stem):
	p = Path(path_str)
	stem = get_file_stem(p)
	assert stem == expected_stem


def assert_altered_stem(path_str, before_stem, after_stem, expected_stem):
	p = Path(path_str)
	stem = make_altered_stem(p, before_stem, after_stem)
	assert stem == expected_stem


def assert_altered_name(
		path_str, before_stem, after_stem, extension, expected_name):
	p = Path(path_str)
	name = make_altered_name(p, before_stem, after_stem, extension)
	assert name == expected_name


def assert_altered_path(
		path_str, before_stem, after_stem, extension, expected_path_str):
	p = Path(path_str)
	path = make_altered_path(p, before_stem, after_stem, extension)
	assert path == Path(expected_path_str)


def test_exten_str_no_path():
	p = Path()
	exten_str = extension_to_str(p)
	assert exten_str == EMPTY_STR


def test_exten_str_empty_path():
	assert_exten_str("", EMPTY_STR)


def test_exten_str_dir():
	assert_exten_str("some_dir", EMPTY_STR)


def test_exten_str_one_suffix():
	assert_exten_str("something.pdf", ".pdf")


def test_exten_str_two_suffixes():
	assert_exten_str("something.tar.gz", ".tar.gz")


def test_exten_str_three_suffixes():
	assert_exten_str("something.x.y.z", ".x.y.z")


def test_file_stem_empty():
	assert_file_stem("", EMPTY_STR)


def test_file_stem_no_exten():
	assert_file_stem("some_dir", "some_dir")


def test_file_stem_one_suffix():
	assert_file_stem("something.pdf", "something")


def test_file_stem_two_suffixes():
	assert_file_stem("something.tar.gz", "something")


def test_altered_stem_no_adding():
	assert_altered_stem("some_dir/gugusse.docx", None, None, "gugusse")


def test_altered_stem_adding_before():
	assert_altered_stem("some_dir/gugusse.docx", "a", None, "agugusse")


def test_altered_stem_adding_after():
	assert_altered_stem("some_dir/gugusse.docx", None,"b", "gugusseb")


def test_altered_stem_adding_before_and_after():
	assert_altered_stem("some_dir/gugusse.docx", "a", "b", "agugusseb")


def test_altered_name_no_exten():
	assert_altered_name(
		"some_dir/gugusse.docx", "a", "b", None, "agugusseb.docx")


def test_altered_name_with_exten():
	assert_altered_name(
		"some_dir/gugusse.docx", "a", "b", ".pdf", "agugusseb.pdf")


def test_altered_path_no_exten():
	assert_altered_path(
		"some_dir/gugusse.docx", "a", "b", None, "some_dir/agugusseb.docx")


def test_altered_path_with_exten():
	assert_altered_path(
		"some_dir/gugusse.docx", "a", "b", ".pdf", "some_dir/agugusseb.pdf")
