from imie.engines.structure.core import MssEngine
from imie.models import ChochResult


def test_detects_bullish_mss():
    choch = ChochResult(
        bullish_choch=True,
        bearish_choch=False,
    )

    result = MssEngine().evaluate(
        choch=choch,
    )

    assert result.detected is True
    assert result.bullish_mss is True
    assert result.bearish_mss is False
    assert result.confidence == 90.0
    assert "bullish" in result.reason.lower()


def test_detects_bearish_mss():
    choch = ChochResult(
        bullish_choch=False,
        bearish_choch=True,
    )

    result = MssEngine().evaluate(
        choch=choch,
    )

    assert result.detected is True
    assert result.bullish_mss is False
    assert result.bearish_mss is True
    assert result.confidence == 90.0
    assert "bearish" in result.reason.lower()


def test_returns_no_mss_without_choch():
    choch = ChochResult(
        bullish_choch=False,
        bearish_choch=False,
    )

    result = MssEngine().evaluate(
        choch=choch,
    )

    assert result.detected is False
    assert result.bullish_mss is False
    assert result.bearish_mss is False
    assert result.confidence == 0.0
    assert "absent" in result.reason.lower()