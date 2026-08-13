import subprocess
import sys


def run_isolated_python(
    source: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-W",
            "error::DeprecationWarning",
            "-c",
            source,
        ],
        capture_output=True,
        check=False,
        text=True,
    )


def test_importing_mock_adapter_does_not_load_alpaca() -> None:
    result = run_isolated_python(
        """
import sys
from imie.execution import MockBrokerExecutionAdapter

assert MockBrokerExecutionAdapter.__name__ == "MockBrokerExecutionAdapter"
assert "imie.execution.alpaca_paper_execution_adapter" not in sys.modules
assert "imie.execution.alpaca_protected_order_request_builder" not in sys.modules
assert "alpaca.trading.client" not in sys.modules
"""
    )

    assert result.returncode == 0, result.stderr


def test_explicit_alpaca_paper_adapter_import_is_available() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from imie.execution import "
                "AlpacaPaperExecutionAdapter; "
                "assert AlpacaPaperExecutionAdapter.__name__ == "
                "'AlpacaPaperExecutionAdapter'"
            ),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_explicit_alpaca_request_builder_import_is_available() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from imie.execution import "
                "AlpacaProtectedOrderRequestBuilder; "
                "assert AlpacaProtectedOrderRequestBuilder.__name__ == "
                "'AlpacaProtectedOrderRequestBuilder'"
            ),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
