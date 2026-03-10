# tests/conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: 실제 외부 API 호출이 필요한 테스트"
    )
