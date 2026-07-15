from imie.engines.structure.core import ChochEngine


def test_detects_bullish_choch_from_bearish_structure():
    result = ChochEngine().evaluate(
        structure_direction="short",
        bullish_break=True,
        bearish_break=False,
    )

    assert result.detected is True
    assert result.bullish_choch is True
    assert result.bearish_choch is False


def test_detects_bearish_choch_from_bullish_structure():
    result = ChochEngine().evaluate(
        structure_direction="long",
        bullish_break=False,
        bearish_break=True,
    )

    assert result.detected is True
    assert result.bullish_choch is False
    assert result.bearish_choch is True


def test_does_not_detect_choch_in_neutral_structure():
    result = ChochEngine().evaluate(
        structure_direction="neutral",
        bullish_break=True,
        bearish_break=False,
    )

    assert result.detected is False
    assert result.bullish_choch is False
    assert result.bearish_choch is False


def test_does_not_detect_choch_when_break_matches_structure():
    bullish_structure_result = ChochEngine().evaluate(
        structure_direction="long",
        bullish_break=True,
        bearish_break=False,
    )

    bearish_structure_result = ChochEngine().evaluate(
        structure_direction="short",
        bullish_break=False,
        bearish_break=True,
    )

    assert bullish_structure_result.detected is False
    assert bullish_structure_result.bullish_choch is False
    assert bullish_structure_result.bearish_choch is False

    assert bearish_structure_result.detected is False
    assert bearish_structure_result.bullish_choch is False
    assert bearish_structure_result.bearish_choch is False


def test_does_not_detect_choch_when_breaks_conflict():
    result = ChochEngine().evaluate(
        structure_direction="long",
        bullish_break=True,
        bearish_break=True,
    )

    assert result.detected is False
    assert result.bullish_choch is False
    assert result.bearish_choch is False