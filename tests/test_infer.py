import pytest
from Aquila_Resolve.infer import Infer


class _FakePhonemizeResult:
    def __init__(self, phonemes):
        self.phonemes = phonemes


def _fake_phonemise_list(text, lang=None, batch_size=None):
    mapping = {
        "": "",
        "a": "AH0",
        "b": "B IY1",
        "ioniformi": "IY0 AA2 N IH0 F AO1 R M IY0",
    }
    return _FakePhonemizeResult([mapping[w] for w in text])


@pytest.fixture
def infer(mocker):
    mocker.patch("Aquila_Resolve.infer.ensure_download")
    fake_phonemizer = mocker.MagicMock()
    fake_phonemizer.phonemise_list = _fake_phonemise_list
    mocker.patch(
        "Aquila_Resolve.infer.Phonemizer.from_checkpoint", return_value=fake_phonemizer
    )
    yield Infer()


# noinspection SpellCheckingInspection
@pytest.mark.parametrize(
    "case, exp",
    [
        ([""], [""]),
        (["a"], ["AH0"]),
        (["a", "a"], ["AH0", "AH0"]),  # Test De-duplication
        (["a", "b"], ["AH0", "B IY1"]),
        (["ioniformi"], ["IY0 AA2 N IH0 F AO1 R M IY0"]),  # OOV word
    ],
)
def test_infer(infer, case, exp):
    assert infer(case) == exp
