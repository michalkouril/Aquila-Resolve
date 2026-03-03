# Fixtures for dictionary setup
import os
import sys
from pathlib import Path
import pytest
import unittest.mock as mock

# Ensure local src/ is used instead of any installed package.
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:
    import pytest_mock  # noqa: F401
except Exception:  # pragma: no cover - fallback when pytest-mock isn't installed
    class _PatchProxy:
        def __init__(self, parent):
            self._parent = parent

        def __call__(self, *args, **kwargs):
            return self._parent._start_patch(mock.patch, *args, **kwargs)

        def object(self, *args, **kwargs):
            return self._parent._start_patch(mock.patch.object, *args, **kwargs)

    class _Mocker:
        MagicMock = mock.MagicMock
        Mock = mock.Mock

        def __init__(self):
            self._patches = []
            self.patch = _PatchProxy(self)

        def _start_patch(self, patch_func, *args, **kwargs):
            p = patch_func(*args, **kwargs)
            started = p.start()
            self._patches.append(p)
            return started

        def stopall(self):
            for p in reversed(self._patches):
                p.stop()
            self._patches.clear()

    @pytest.fixture
    def mocker():
        m = _Mocker()
        yield m
        m.stopall()
from Aquila_Resolve import dictionary
from Aquila_Resolve.h2p import H2p
from Aquila_Resolve import download

file_mock_path = "path/to/custom_dict.json"
file_mock_content = """
{
    "absent": {
        "VERB": "AH1 B S AE1 N T",
        "DEFAULT": "AE1 B S AH0 N T"
    },
    "abstract": {
        "VERB": "AE0 B S T R AE1 K T",
        "DEFAULT": "AE1 B S T R AE2 K T"
    },
    "reject": {
        "VERB": "R IH0 JH EH1 K T",
        "DEFAULT": "R IY1 JH EH0 K T"
    },
    "read": {
        "VBD": "R EH1 D",
        "VBN": "R EH1 D",
        "VBP": "R EH1 D",
        "DEFAULT": "R IY1 D"
    },
    "(no-default)": {
        "VBD": "R EH1 D",
        "VBN": "R EH1 D",
        "VBP": "R EH1 D"
    }
}
"""


# Setup to ensure model is downloaded
def pytest_sessionstart(session):
    # Avoid network in default test runs. Set AQUILA_RESOLVE_TEST_DOWNLOAD=1 to enable.
    if os.getenv("AQUILA_RESOLVE_TEST_DOWNLOAD") == "1":
        assert download() is True


def pytest_collection_modifyitems(config, items):
    # If no model is available and downloads are disabled, skip model-dependent tests.
    if os.getenv("AQUILA_RESOLVE_TEST_DOWNLOAD") == "1":
        return
    try:
        from Aquila_Resolve.data import DATA_PATH
    except Exception:
        return
    if (DATA_PATH / "model.pt").exists():
        return
    skip = pytest.mark.skip(
        reason="Model checkpoint not available. Set AQUILA_RESOLVE_TEST_DOWNLOAD=1 to enable download."
    )
    for item in items:
        if item.fspath and item.fspath.basename in {"test_g2p.py", "test_processors.py"}:
            item.add_marker(skip)


# noinspection PyUnusedLocal
def always_exists(path):
    return True


@pytest.fixture
# Creates a H2p instance using mock dictionary
def h2p(mocker) -> H2p:
    # Patch builtins.open
    mocked_dict_data = mock.mock_open(read_data=file_mock_content)
    with mock.patch("builtins.open", mocked_dict_data):
        # Patch Dictionary exist check
        mocker.patch.object(dictionary, "exists", side_effect=always_exists)
        # Create H2p object
        result = H2p(file_mock_path)
    assert isinstance(result, H2p)
    assert result.dict.file_name == file_mock_path
    yield result


@pytest.fixture
# Creates a Dictionary object using mock dictionary
def mock_dict(mocker) -> dictionary.Dictionary:
    # Patch builtins.open
    mocked_dict_data = mock.mock_open(read_data=file_mock_content)
    with mock.patch("builtins.open", mocked_dict_data):
        # Patch Dictionary exist check
        mocker.patch.object(dictionary, "exists", side_effect=always_exists)
        # Create Dictionary object
        result = dictionary.Dictionary(file_mock_path)
    assert isinstance(result, dictionary.Dictionary)
    assert result.file_name == file_mock_path
    yield result


@pytest.fixture
# Creates a Dictionary object using default path
def mock_dict_def(mocker) -> dictionary.Dictionary:
    # Patch Dictionary exist check
    mocker.patch.object(dictionary, "exists", side_effect=always_exists)
    # Create Dictionary object
    result = dictionary.Dictionary()
    assert isinstance(result, dictionary.Dictionary)
    assert result.file_name == "heteronyms.json"
    yield result
