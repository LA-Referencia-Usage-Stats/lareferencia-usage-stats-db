import configparser
from urllib.parse import quote

def read_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    #for section in config.sections():
    #    for key in config[section]:
    #        print((key, config[section][key]))
    
    return config


def _get_first_nonempty(config, sections, option):
    for section in sections:
        if config.has_section(section) and config.has_option(section, option):
            value = config.get(section, option).strip()
            if value:
                return value
    return None


def get_usage_stats_db_uri(config):
    host = _get_first_nonempty(config, ("USAGE_STATS_DB",), "HOST")
    username = _get_first_nonempty(config, ("USAGE_STATS_DB",), "USERNAME")
    password = _get_first_nonempty(config, ("USAGE_STATS_DB",), "PASSWORD")
    database = _get_first_nonempty(config, ("USAGE_STATS_DB",), "DATABASE")
    port = _get_first_nonempty(config, ("USAGE_STATS_DB",), "PORT") or "3306"

    if host and username is not None and password is not None and database:
        return _build_mysql_uri(host, username, password, database, port)

    # Backward compatibility.
    uri = _get_first_nonempty(
        config,
        ("USAGE_STATS_DB", "DB"),
        "SQLALCHEMY_DATABASE_URI",
    )
    if uri is not None:
        return uri

    raise KeyError(
        "Missing usage DB configuration. Expected [USAGE_STATS_DB] "
        "HOST/PORT/USERNAME/PASSWORD/DATABASE (preferred) "
        "or SQLALCHEMY_DATABASE_URI (legacy)."
    )


def _build_mysql_uri(host, username, password, database, port):
    safe_username = quote(username, safe="")
    safe_password = quote(password, safe="")
    safe_database = database.lstrip("/")
    safe_port = str(port or "3306").strip()
    return (
        f"mysql+pymysql://{safe_username}:{safe_password}"
        f"@{host}:{safe_port}/{safe_database}?charset=utf8mb4"
    )


def get_matomo_db_uri(config):
    # Preferred legacy form: full URI in [MATOMO]
    uri = _get_first_nonempty(config, ("MATOMO",), "SQLALCHEMY_DATABASE_URI")
    if uri is not None:
        return uri

    # Canonical root form: components in [MATOMO_DB]
    uri = _get_first_nonempty(config, ("MATOMO_DB",), "SQLALCHEMY_DATABASE_URI")
    if uri is not None:
        return uri

    host = _get_first_nonempty(config, ("MATOMO_DB",), "HOST")
    username = _get_first_nonempty(config, ("MATOMO_DB",), "USERNAME")
    password = _get_first_nonempty(config, ("MATOMO_DB",), "PASSWORD")
    database = _get_first_nonempty(config, ("MATOMO_DB",), "DATABASE")
    port = _get_first_nonempty(config, ("MATOMO_DB",), "PORT") or "3306"

    if host and username is not None and password is not None and database:
        return _build_mysql_uri(host, username, password, database, port)

    raise KeyError(
        "Missing Matomo DB configuration. Expected [MATOMO] "
        "SQLALCHEMY_DATABASE_URI (legacy) or [MATOMO_DB] HOST/USERNAME/PASSWORD/DATABASE."
    )
