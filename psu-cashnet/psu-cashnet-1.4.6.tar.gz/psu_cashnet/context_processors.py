from psu_base.services import auth_service
from psu_base.classes.Log import Log
from psu_cashnet.models.transaction import Transaction

log = Log()


def cashnet(request):

    # Only admins need to know about these, so don't run the query for students
    if auth_service.has_authority(['admin', 'cashnet']):
        cn_unprocessed = Transaction.objects.filter(status_code='R').filter(cashnet_result_code=0).count()
    else:
        cn_unprocessed = None

    return {
        "cn_unprocessed": cn_unprocessed,
    }
