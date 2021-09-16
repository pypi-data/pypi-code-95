import pytest
from jazal import PathChecker, ReactivePathChecker
from pathlib import Path


def test_init():
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	assert rpc.path == Path("ajxoj/io.txt")
	assert rpc.extension == (".pdf",)
	assert rpc.arg_name == "awesomeArg"


def test_eq_true():
	rpc1 = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	rpc2 = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	assert rpc1 == rpc2


def test_eq_false():
	rpc1 = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	rpc2 = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "formidableArg")
	assert rpc1 != rpc2


def test_rpc_eq_pc():
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	assert rpc != pc


def test_pc_eq_rpc():
	pc = PathChecker("ajxoj/io.txt", (".pdf",))
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	assert pc != rpc


def test_repr():
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	assert repr(rpc) in (
		"ReactivePathChecker('ajxoj/io.txt', ('.pdf',), 'awesomeArg')",
		"ReactivePathChecker('ajxoj\\io.txt', ('.pdf',), 'awesomeArg')")


def test_check_extension_correct():
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	except_msg =\
		"awesomeArg must be the path to a file with the extension '.pdf'."
	with pytest.raises(ValueError, match = except_msg):
		rpc.check_extension_correct()


def test_check_path_exists():
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	with pytest.raises(FileNotFoundError):
		rpc.check_path_exists()


def test_name_with_correct_exten():
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	assert rpc.name_with_correct_exten() == "io.pdf"


def test_path_with_correct_exten():
	rpc = ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
	correct_path = rpc.path_with_correct_exten()
	assert correct_path in (Path("ajxoj/io.pdf"), Path("ajxoj\\io.pdf"))
