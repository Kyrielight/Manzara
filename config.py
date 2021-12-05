
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    environments=False,
    envvar_prefix="USAGI12",
    env_switcher="USAGI12_ENV",
    load_dotenv=False,
    settings_files=['settings.toml', '.secrets.toml'],
    validators=[
        Validator('AYUMI_LOG_LEVEL', is_type_of=str),
        Validator('AYUMI_LOG_FORMAT', is_type_of=str),
        Validator('AYUMI_DATE_FORMAT', is_type_of=str),
        Validator('AYUMI_CONSOLE_FORMAT', is_type_of=str),
        Validator('AYUMI_EXCHANGE', is_type_of=str),
    ]
)

# `envvar_prefix` = export envvars with `export USAGI12_FOO=bar`.
# `settings_files` = Load this files in the order.