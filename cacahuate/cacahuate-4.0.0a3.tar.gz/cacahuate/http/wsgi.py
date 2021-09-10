import logging.config
import os
import time

from flask import Flask
from flask.logging import default_handler
from flask_coralillo import Coralillo
from flask_cors import CORS
from yuid import yuid

from cacahuate.indexes import create_indexes
from cacahuate.models import bind_models
from cacahuate.http.mongo import mongo
from cacahuate.tasks import app as celery

from flask_sse import sse

# The flask application
app = Flask(__name__)
app.config.from_object('cacahuate.settings')
app.config.from_envvar('CACAHUATE_SETTINGS', silent=True)

# Setup logging
app.logger.removeHandler(default_handler)
logging.config.dictConfig(app.config['LOGGING'])

# Enalble cross origin
CORS(app)

# Timezone
os.environ['TZ'] = app.config.get('TIMEZONE', 'UTC')
time.tzset()

# Bind the redis database
cora = Coralillo(app, id_function=yuid)
bind_models(cora._engine)

# The mongo database
mongo.init_app(app)
create_indexes(app.config)

celery.conf.update(
    broker='amqp://{user}@{host}//'.format(
        user=app.config['RABBIT_USER'],
        host=app.config['RABBIT_HOST'],
    ),
    task_default_queue=app.config['RABBIT_QUEUE'],
)

# Url converters
import cacahuate.http.converters  # noqa

# Views
import cacahuate.http.views.api  # noqa
import cacahuate.http.views.auth  # noqa
import cacahuate.http.views.templates  # noqa
# sse
if app.config['SSE_ENABLED']:
    app.register_blueprint(sse, url_prefix='/stream')

# Error handlers
import cacahuate.http.error_handlers  # noqa
