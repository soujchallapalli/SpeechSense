# tests/conftest.py
from dotenv import load_dotenv


# This hook runs automatically before ANY test files are imported or executed
def pytest_configure(config):
    load_dotenv()
