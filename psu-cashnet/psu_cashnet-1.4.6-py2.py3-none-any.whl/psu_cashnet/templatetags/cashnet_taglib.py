from django import template
from django.urls import reverse
from psu_base.classes.Log import Log
from psu_base.templatetags.tag_processing import (
    html_generating,
    supporting_functions as support,
)
from psu_base.services import utility_service, auth_service
from psu_cashnet.models.transaction import Transaction
from psu_cashnet import cn_admin_roles

register = template.Library()
log = Log()


@register.tag()
def cashnet_error_tab(parser, token):
    """
    Include a link to transactions that had an error (for admins)
    """
    log.trace()
    if auth_service.has_authority(cn_admin_roles):
        tx_list = Transaction.objects.filter(
            app_code=utility_service.get_app_code(), status_code="E"
        )
        num_errors = len(tx_list) if tx_list else 0
        if num_errors:
            badge = f'<sup class="badge badge-pill badge-danger">{num_errors}</sup>'
            url = f"{reverse('cashnet:transaction_index')}?keywords=error"
            return html_generating.HeaderNavTab(
                [
                    'junk="hi"',
                    f'url="cashnet:transaction_errors"',
                    'url_arg="error"',
                    f'label="Cashnet Errors - {num_errors}"',
                ]
            )
    return ""
