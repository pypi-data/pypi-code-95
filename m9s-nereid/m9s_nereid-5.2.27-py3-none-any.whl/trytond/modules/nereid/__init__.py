# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool

from . import party
from . import user
from . import website
from . import static_file
from . import currency
from . import configuration
from . import translation
from . import country
from . import model

__all__ = ['register']


def register():
    Pool.register(
        party.Address,
        party.Party,
        party.ContactMechanism,
        user.NereidUser,
        user.NereidAnonymousUser,
        website.WebSiteLocale,
        website.WebSite,
        website.WebsiteCountry,
        website.WebsiteCurrency,
        website.WebsiteWebsiteLocale,
        static_file.NereidStaticFolder,
        static_file.NereidStaticFile,
        currency.Currency,
        configuration.NereidConfigStart,
        translation.Translation,
        country.Country,
        country.Subdivision,
        model.ModelData,
        module='nereid', type_='model')
    Pool.register(
        configuration.NereidConfig,
        party.PartyErase,
        translation.TranslationSet,
        translation.TranslationUpdate,
        translation.TranslationClean,
        module='nereid', type_='wizard')
