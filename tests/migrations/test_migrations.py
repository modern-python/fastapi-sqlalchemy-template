from pytest_alembic.tests import (
    test_model_definitions_match_ddl,
    test_single_head_revision,
    test_up_down_consistency,
    test_upgrade,
)


_ = test_single_head_revision
_ = test_upgrade
_ = test_model_definitions_match_ddl
_ = test_up_down_consistency
