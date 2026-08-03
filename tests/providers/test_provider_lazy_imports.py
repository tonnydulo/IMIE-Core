import subprocess
import sys


def run_isolated_python(source: str) -> subprocess.CompletedProcess[str]:
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


def test_importing_provider_manager_does_not_load_alpaca() -> None:
    result = run_isolated_python(
        """
import sys
from imie.providers import ProviderManager

assert ProviderManager.__name__ == "ProviderManager"
assert "imie.providers.alpaca_provider" not in sys.modules
"""
    )

    assert result.returncode == 0, result.stderr


def test_creating_mock_provider_does_not_load_alpaca() -> None:
    result = run_isolated_python(
        """
import sys
from imie.providers import ProviderFactory

provider = ProviderFactory.create("mock")

assert type(provider).__name__ == "MockProvider"
assert "imie.providers.alpaca_provider" not in sys.modules
"""
    )

    assert result.returncode == 0, result.stderr


def test_explicit_alpaca_import_remains_available() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from imie.providers import AlpacaProvider; "
                "assert AlpacaProvider.__name__ == 'AlpacaProvider'"
            ),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
