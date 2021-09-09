# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from product.recaptcha_invisible import _
from zope import schema
from zope.interface import Interface


class IRecatpchaInvisibleControlPanel(Interface):
    """ IRecatpchaInvisibleControlPanel
    """

    public_key = schema.TextLine(
        title=_('Public key'),
        required=True,
    )

    private_key = schema.TextLine(
        title=_('Private key'),
        required=True,
    )


class RecaptchaInvisibleControlPanelForm(RegistryEditForm):
    """ Recaptcha Invisible ControlPanel
    """

    schema = IRecatpchaInvisibleControlPanel
    schema_prefix = 'recaptcha_invisible'

    label = _('Recaptcha Invisible')
    description = _(
        'Settings for recaptcha invisible. Configure '
        'the public and private key'  # noqa: C812
    )


class RecaptchaInvisibleControlPanelView(ControlPanelFormWrapper):
    """ Recaptcha Invisible ControlPanel
    """
    form = RecaptchaInvisibleControlPanelForm
