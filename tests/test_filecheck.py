from pathlib import Path

import pytest

from mathshorts import filecheck


def test_stubs_refuse_rather_than_pass():
    with pytest.raises(NotImplementedError):
        filecheck.check_kit(None, Path("."))
    with pytest.raises(NotImplementedError):
        filecheck.check_upload(None, "abcdefghijk")
