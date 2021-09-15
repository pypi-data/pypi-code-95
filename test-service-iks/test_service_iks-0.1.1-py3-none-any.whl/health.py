import os
import multiprocessing
from flask import Blueprint, jsonify, request
from flask import current_app as app

bp = Blueprint('health', __name__, url_prefix='/health')


@bp.route('/full', methods=('GET',))
def index():
    """
    End point for health checks
    ---
    tags:
      - Admin
    produces:
      - text/html
    schemes: ['http', 'https']
    deprecated: false
    responses:
      200:
        description: JSON data with CPU count, environment name, server mode, asset id and gist list
    """
    args = request.args
    details = args.get('details', None)
    if details and details.lower() in ['yes', 'on', '1', 'ok']:
        # detailed response
        d = {"status": "Healthy",
             "cpu_count": str(multiprocessing.cpu_count()),
             "env": os.getenv('APP_ENV', 'local'),
             "asset": os.getenv('ASSET_ID')}
    else:
        d = {"status": "I am Healthy!"}
    return jsonify(d)