import pytest
from jazal import\
	MissingPathArgWarner,\
	PathChecker,\
	ReactivePathChecker


def test_init():
	warner = MissingPathArgWarner("awesomeArg", (".pdf",))
	assert warner.arg_name == "awesomeArg"
	assert warner.extension == (".pdf",)


def test_missing_arg_msg():
	warner = MissingPathArgWarner("arg", (".pdf",))
	assert warner.make_missing_arg_msg() ==\
		"arg: the path to a file with extension '.pdf' must be provided."


def test_make_path_checker():
	warner = MissingPathArgWarner("awesomeArg", (".pdf",))
	pc = warner.make_path_checker("ajxoj/io.txt")
	assert pc == PathChecker("ajxoj/io.txt", (".pdf",))


def test_make_reactive_path_checker():
	warner = MissingPathArgWarner("awesomeArg", (".pdf",))
	rpc = warner.make_reactive_path_checker("ajxoj/io.txt")
	assert rpc == ReactivePathChecker("ajxoj/io.txt", (".pdf",), "awesomeArg")
