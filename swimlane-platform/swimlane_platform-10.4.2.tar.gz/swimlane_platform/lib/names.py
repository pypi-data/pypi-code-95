# noinspection PyPep8Naming
class names:
    # general
    SWIMLANE_PREFIX = 'SWIMLANE_'
    APP_NAME = 'swimlane_platform'
    # database
    TURBINE_DATABASE = 'SwimlaneTurbine'
    DB_ENCRYPTION_KEY = 'database_encryption.key'
    DB_INIT_SCRIPT = 'init-mongodb-users.sh'
    # ssl related
    SSL_WEB_KEY = 'swimlane.key'
    SSL_WEB_CERTIFICATE = 'swimlane.crt'
    # docker files
    DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    DOCKER_COMPOSE_TURBINE_FILE = 'docker-compose.turbine.yml'
    DOCKER_IMAGE_ARCHIVE_NAME = 'swimlane-images.tgz'
    TEMPLATE_REPOSITORY_TAG = '<sw_docker_image_repo_placeholder>'
    TEMPLATE_VERSION_TAG = '<sw_docker_image_tag_placeholder>'
    DEV_REPOSITORY = 'nexus.swimlane.io:5000/'
    DOCKER_COMPOSE_OVERRIDE_FILE = 'docker-compose.override.yml'
    DOCKER_COMPOSE_INSTALL_FILE = 'docker-compose.install.yml'
    # docker service names
    SW_API = 'sw_api'
    SW_WEB = 'sw_web'
    SW_NEO_J = 'sw_neo4j'
    SW_TASKS = 'sw_tasks'
    SW_MONGO = 'sw_mongo'
    SW_REPORTS = 'sw_reports'
    SW_TURBINE_ENGINE = 'sw_turbine_engine'
    # file and folder locations
    SECRETS_SUB_FOLDER = '.secrets/'
    DB_INIT_SUB_FOLDER = 'db-init'
    TEMPLATE_DIR = 'swimlane_template_dir'
    INSTALL_DIR = '/opt/swimlane'
    # environment files and variables
    TURBINE_ENV_FILE = '.turbine-env'
    API_ENV_FILE = '.api-env'
    TASKS_ENV_FILE = '.tasks-env'
    MONGO_ENV_FILE = '.mongo-env'
    MONGO_ENV_ADMIN_NAME = 'MONGO_INITDB_ROOT_USERNAME'
    MONGO_ENV_ADMIN_PASSWORD = 'MONGO_INITDB_ROOT_PASSWORD'
    MONGO_ENV_SW_PASSWORD = 'SW_MONGO_INITDB_SWIMLANE_PASSWORD'
    MONGO_ENV_SW_NAME = 'SW_MONGO_INITDB_SWIMLANE_USERNAME'
    DOT_NET_SWIMLANE_CONN_KEY = 'SWIMLANE_Data__Mongo__SwimlaneConnectionString'
    DOT_NET_HISTORY_CONN_KEY = 'SWIMLANE_Data__Mongo__HistoryConnectionString'
    DOT_NET_ADMIN_CONN_KEY = 'SWIMLANE_Data__Mongo__AdminConnectionString'

    def __init__(self):
        pass

