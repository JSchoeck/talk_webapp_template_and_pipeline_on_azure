import pytest  # noqa: F401

import app


def test_main() -> None:
    assert app.main() is None
