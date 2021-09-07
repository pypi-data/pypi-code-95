from .utils import Utils
from .base import Base
from .user import User

def find_user(filter_ = None, offset=0, limit=1000, output='DataFrame'):
    '''Return the list of user in the system'''
    if not Base.db_service.is_user():
        print('ERROR: Login required')
        return
    filter_params = Utils.build_filter_params(filter_, offset, limit)
    from_server = Base.db_service.get(f'/users', query_params=filter_params)
    try:
        rows = Utils.output_form(User, from_server['users'], output)
        total = from_server['totalNumber']
        return rows, total
    except:
        return [], 0