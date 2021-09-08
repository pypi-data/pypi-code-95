from django import template

register = template.Library()


@register.filter
def cents_to_usd(cents):
    """
    Returns datetime object for given unix epoch time.
    :param unix_epoch: int Unix epoch time
    :returns str: USD formatted string .02d
    """

    return '%.2f' % (cents / 100.)
