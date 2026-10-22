import logging

import pydantic
import pytest
from granian.log import LogLevels

from app.settings import Settings


def test_api_bootstrapper_config_reads_instance_not_global() -> None:
    custom = Settings(service_name="custom-service", service_version="9.9.9")

    config = custom.api_bootstrapper_config

    assert config.service_name == "custom-service"
    assert config.service_version == "9.9.9"


def test_pool_pre_ping_is_off_by_default() -> None:
    assert Settings().db_pool_pre_ping is False


def test_pool_timeout_defaults_to_five_seconds() -> None:
    assert Settings().db_pool_timeout == 5  # noqa: PLR2004


def test_log_level_is_case_insensitive_and_reaches_app_logging() -> None:
    custom = Settings(log_level="WARNING")

    assert custom.log_level == LogLevels.warning
    assert custom.api_bootstrapper_config.logging_log_level == logging.WARNING


@pytest.mark.parametrize("pool_settings", [{"db_pool_size": 0}, {"db_max_overflow": -1}])
def test_pool_settings_reject_unbounded_pools(pool_settings: dict[str, int]) -> None:
    with pytest.raises(pydantic.ValidationError):
        Settings.model_validate(pool_settings)
