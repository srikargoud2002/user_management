import os
import logging
import app.utils.common as common
import pytest

@pytest.mark.asyncio
async def test_setup_logging(monkeypatch):
    dummy_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dummy_logging.conf')

    # ✅ Patch global os.path.normpath
    monkeypatch.setattr(os.path, 'normpath', lambda path: dummy_path)

    # ✅ Patch logging.config.fileConfig (separately)
    monkeypatch.setattr(logging.config, 'fileConfig', lambda path, disable_existing_loggers=False: None)

    try:
        common.setup_logging()
    except Exception as e:
        pytest.fail(f"setup_logging() raised an exception: {e}")
