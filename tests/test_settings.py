from app.settings import Settings


def test_api_bootstrapper_config_reads_instance_not_global() -> None:
    custom = Settings(service_name="custom-service", service_version="9.9.9")

    config = custom.api_bootstrapper_config

    assert config.service_name == "custom-service"
    assert config.service_version == "9.9.9"


def test_pool_pre_ping_is_off_by_default() -> None:
    assert Settings().db_pool_pre_ping is False
