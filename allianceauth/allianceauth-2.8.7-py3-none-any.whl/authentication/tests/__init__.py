from django.urls import reverse


def get_admin_change_view_url(obj: object) -> str:
    """returns URL to admin change view for given object"""
    return reverse(
        'admin:{}_{}_change'.format(
            obj._meta.app_label, type(obj).__name__.lower()
        ),
        args=(obj.pk,)
    )


def get_admin_search_url(ModelClass: type) -> str:
    """returns URL to search URL for model of given object"""
    return '{}{}/'.format(
        reverse('admin:app_list', args=(ModelClass._meta.app_label,)),
        ModelClass.__name__.lower()
    )
