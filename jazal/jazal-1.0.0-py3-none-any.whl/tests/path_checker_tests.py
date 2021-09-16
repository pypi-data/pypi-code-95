import pytest
from jazal import PathChecker
from pathlib import Path


def test_init_no_exten():
	pc = PathChecker("ajxoj/io.txt", None)
	assert pc.path == Path("ajxoj/io.txt")
	assert pc.extension == ()


def test_init_with_exten():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert pc.path == Path("ajxoj/io.txt")
	assert pc.extension == (".pdf",)


def test_init_path_exception():
	except_msg = "The given path must be an instance of pathlib.Path or str."
	with pytest.raises(TypeError, match = except_msg):
		pc = PathChecker(["ajxoj", "io.txt"], (".pdf",))


def test_eq_same():
	pc1 = PathChecker("ajxoj/io.txt", (".pdf",))
	pc2 = PathChecker("ajxoj/io.txt", (".pdf",))
	assert pc1 == pc2


def test_eq_different_paths():
	pc1 = PathChecker("ajxoj/io.txt", (".pdf",))
	pc2 = PathChecker("ajxoj/tio.txt", (".pdf",))
	assert pc1 != pc2


def test_eq_different_extensions():
	pc1 = PathChecker("ajxoj/io.txt", (".pdf",))
	pc2 = PathChecker("ajxoj/io.txt", (".docx",))
	assert pc1 != pc2


def test_eq_different_types():
	pc1 = PathChecker("ajxoj/io.txt", (".pdf",))
	pc2 = 5
	assert pc1 != pc2


def test_repr():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert repr(pc) in (
		"PathChecker('ajxoj/io.txt', ('.pdf',))",
		"PathChecker('ajxoj\\io.txt', ('.pdf',))")


def test_exten_is_correct_true():
	pc = PathChecker("ajxoj/io.txt", (".txt",))
	assert pc.extension_is_correct()


def test_exten_is_correct_true_no_exten():
	pc = PathChecker("ajxoj/io", None)
	assert pc.extension_is_correct()


def test_exten_is_correct_false():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert not pc.extension_is_correct()


def test_exten_is_correct_false_no_exten():
	pc = PathChecker("ajxoj/io", (".pdf",))
	assert not pc.extension_is_correct()


def test_exten_is_correct_false_no_expected_exten():
	pc = PathChecker("ajxoj/io.txt", None)
	assert not pc.extension_is_correct()


def test_get_file_name():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert pc.get_file_name() == "io.txt"


def test_get_file_stem():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert pc.get_file_stem() == "io"


def test_path_exists_true():
	pc = PathChecker("some_dir/un_fichier_pdf.pdf", (".pdf",))
	assert pc.path_exists()


def test_path_exists_false():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert not pc.path_exists()


def test_path_is_dir_true():
	pc = PathChecker("some_dir", (".pdf",))
	assert pc.path_is_dir()


def test_path_is_dir_false():
	pc = PathChecker("some_dir/un_fichier_pdf.pdf", (".pdf",))
	assert not pc.path_is_dir()


def test_path_is_dir_inexistent():
	pc = PathChecker("ajxoj", (".pdf",))
	assert not pc.path_is_dir()


def test_path_is_file_true():
	pc = PathChecker("some_dir/un_fichier_pdf.pdf", (".pdf",))
	assert pc.path_is_file()


def test_path_is_file_false():
	pc = PathChecker("some_dir", (".pdf",))
	assert not pc.path_is_file()


def test_path_is_file_inexistent():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert not pc.path_is_file()
