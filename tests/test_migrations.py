from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_has_single_head_revision() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    heads = script.get_heads()

    assert len(heads) == 1
    assert heads[0] == "35ab063bd9c7"
