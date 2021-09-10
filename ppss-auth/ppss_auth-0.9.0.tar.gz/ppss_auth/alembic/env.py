from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
#target_metadata = None
from ppss_auth.models import (
#from multilandingengine.models import (
    Base,


)
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_object(object, name, type_, reflected, compare_to):
    print ("{},{},{},{},{}".format(object, name, type_, reflected, compare_to)  )
    return True

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        version_table="ppss_auth_alembic_version",
        target_metadata=target_metadata,
        include_object = include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            version_table="ppss_auth_alembic_version",
            include_object = include_object,
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


def extraParse(context):
    import os
    x = context.get_x_argument()
    print(x)
    x = context.get_x_argument(True)
    print(x)
    if "sqluri" in x:

        import configparser
        config = configparser.ConfigParser()
        #print(x["sqluri"])
        here = x.get("cwd", os.getcwd())

        config.read(os.path.join(here, x["sqluri"] ) )
        config["app:main"]["here"] = here
        connection_string = config["app:main"]["sqlalchemy.url"]
        print("connection_string: {}".format(connection_string))
        context.config.set_main_option('sqlalchemy.url', connection_string)


#print (repr(context))
#print (dir (context))

#print (repr(context.config))
#print (dir (context.config))
#print (context.get_x_argument("pippo"))


extraParse(context)

#exit(0)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
