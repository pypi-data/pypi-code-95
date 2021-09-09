import copy
import json
import pytest
from tuxrun.tuxmake import TuxMakeBuild
from tuxrun.tuxmake import InvalidTuxMakeBuild


metadata = {
    "results": {
        "artifacts": {"kernel": ["bzImage"], "modules": ["modules.tar.xz"]},
    },
    "build": {"target_arch": "arm64"},
}


def build_directory(directory, metadata=metadata):
    directory.mkdir()
    (directory / "metadata.json").write_text(json.dumps(metadata))
    return directory


@pytest.fixture
def directory(tmp_path):
    return build_directory(tmp_path / "tuxmake-build")


@pytest.fixture
def directory_with_invalid_metadata(tmp_path):
    d = tmp_path / "invalid-metadata"
    d.mkdir()
    (d / "metadata.json").touch()
    return d


@pytest.fixture
def tuxmake_build(directory):
    return TuxMakeBuild(directory)


class TestTuxMakeBuild:
    def test_kernel(self, tuxmake_build, directory):
        assert tuxmake_build.kernel == directory / "bzImage"

    def test_modules(self, tuxmake_build, directory):
        assert tuxmake_build.modules == directory / "modules.tar.xz"

    def test_target_arch(self, tuxmake_build):
        assert tuxmake_build.target_arch == "arm64"

    def test_no_kernel(self, tmp_path):
        metadata1 = copy.deepcopy(metadata)
        del metadata1["results"]["artifacts"]["kernel"]
        directory = build_directory(tmp_path / "build", metadata1)
        tuxmake_build = TuxMakeBuild(directory)
        assert tuxmake_build.kernel is None

    def test_no_modules(self, tmp_path):
        metadata1 = copy.deepcopy(metadata)
        del metadata1["results"]["artifacts"]["modules"]
        directory = build_directory(tmp_path / "build", metadata1)
        tuxmake_build = TuxMakeBuild(directory)
        assert tuxmake_build.modules is None

    def test_no_metadata(self, tmp_path):
        with pytest.raises(InvalidTuxMakeBuild):
            TuxMakeBuild(tmp_path)

    def test_no_directory(self, tmp_path):
        f = tmp_path / "somefile"
        f.touch()
        with pytest.raises(InvalidTuxMakeBuild):
            TuxMakeBuild(f)

    def test_invalid_metadata(self, directory_with_invalid_metadata):
        with pytest.raises(InvalidTuxMakeBuild):
            TuxMakeBuild(directory_with_invalid_metadata)
