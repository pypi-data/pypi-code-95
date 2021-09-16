# -*- coding: utf-8 -*-

from collective.taxonomy.interfaces import ITaxonomy
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from datetime import datetime
from library.core.widget.textdate import TextDateFieldWidget
from library.core.widget.title import TextTitleFieldWidget
from plone.app.textfield import RichText
from plone.app.textfield.value import IRichTextValue
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform import directives as form
from plone.dexterity.browser import view
from plone.dexterity.content import Container
from plone.dexterity.utils import iterSchemata
from plone.indexer.decorator import indexer
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from re import match
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.validator import SimpleFieldValidator
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Invalid
from zope.schema import getFields
from zope.schema import ValidationError

import six


def fileSize(value):
    if value.size > 30000000:
        raise InvalidFileSizeError(value)
    return True


class InvalidFileSizeError(ValidationError):
    """Exception for file size too large"""

    __doc__ = "Le fichier doit faire moins de 30MB."


class IPatrimoine(model.Schema):
    """Marker interface for Patrimoine"""

    # model.load("patrimoine.xml")

    numero_inventaire = schema.TextLine(title=(u"Numéro d'inventaire"), required=False)
    informations = RichText(title=(u"Informations"), required=False)

    contenus_lies = RelationList(
        title=u"Contenus liés",
        default=[],
        value_type=RelationChoice(
            title=(u"Relation Choice"),
            source=CatalogSource(portal_type=("Folder", "patrimoine")),
        ),
        required=False,
    )

    fichier_pdf = namedfile.NamedBlobFile(
        title=(u"Fichier PDF"), required=False, constraint=fileSize
    )

    fieldset(
        "Publication",
        fields=[
            "auteur",
            "lieu",
            "editeur",
            "date",
            "nombre_de_pages",
            "format_1",
            "illustre",
        ],
    )
    auteur = schema.TextLine(title=(u"Auteur"), required=False)
    lieu = schema.TextLine(title=(u"Lieu"), required=False)
    editeur = schema.TextLine(title=(u"Éditeur"), required=False)

    form.widget("date", TextDateFieldWidget)
    date = schema.TextLine(title=(u"Date"), required=False)

    nombre_de_pages = schema.TextLine(title=(u"Nombre de pages"), required=False)
    format_1 = schema.TextLine(title=(u"Format"), required=False)

    illustre = schema.Bool(title=(u"Illustré"), required=False)
    # form.widget(illustre=RadioFieldWidget)

    fieldset(
        "Carte postale",
        fields=["nom_de_rue", "couleur"],
    )
    nom_de_rue = schema.TextLine(title=(u"Nom de rue"), required=False)
    couleur = schema.Choice(
        title=(u"Couleur"),
        required=False,
        vocabulary="library.core.vocabularies.colors_vocabulary",
    )

    fieldset(
        "Registre",
        fields=[
            "nom_prenom_1",
            "nom_du_conjoint_1",
            "evenement_date_1",
            "date_evenement_1",
            "nom_prenom_2",
            "nom_du_conjoint_2",
            "evenement_date_2",
            "date_evenement_2",
            "nom_prenom_3",
            "nom_du_conjoint_3",
            "evenement_date_3",
            "date_evenement_3",
            "nom_prenom_4",
            "nom_du_conjoint_4",
            "evenement_date_4",
            "date_evenement_4",
        ],
    )

    nom_prenom_1 = schema.TextLine(title=(u"Nom prénom 1"), required=False)
    nom_du_conjoint_1 = schema.TextLine(title=(u"Nom du conjoint 1"), required=False)
    evenement_date_1 = schema.Choice(
        title=(u"Evénement lié à la date 1"),
        required=False,
        vocabulary="library.core.vocabularies.eventsdate_vocabulary",
    )
    date_evenement_1 = schema.TextLine(
        title=(u"Date événement 1"), description="(jj/mm/aaaa)", required=False
    )

    nom_prenom_2 = schema.TextLine(title=(u"Nom prénom 2"), required=False)
    nom_du_conjoint_2 = schema.TextLine(title=(u"Nom du conjoint 2"), required=False)
    evenement_date_2 = schema.Choice(
        title=(u"Evénement lié à la date 2"),
        required=False,
        vocabulary="library.core.vocabularies.eventsdate_vocabulary",
    )
    date_evenement_2 = schema.TextLine(
        title=(u"Date événement 2"), description="(jj/mm/aaaa)", required=False
    )

    nom_prenom_3 = schema.TextLine(title=(u"Nom prénom 3"), required=False)
    nom_du_conjoint_3 = schema.TextLine(title=(u"Nom du conjoint 3"), required=False)
    evenement_date_3 = schema.Choice(
        title=(u"Evénement lié à la date 3"),
        required=False,
        vocabulary="library.core.vocabularies.eventsdate_vocabulary",
    )
    date_evenement_3 = schema.TextLine(
        title=(u"Date événement 3"), description="(jj/mm/aaaa)", required=False
    )

    nom_prenom_4 = schema.TextLine(title=(u"Nom prénom 4"), required=False)
    nom_du_conjoint_4 = schema.TextLine(title=(u"Nom du conjoint 4"), required=False)
    evenement_date_4 = schema.Choice(
        title=(u"Evénement lié à la date 4"),
        required=False,
        vocabulary="library.core.vocabularies.eventsdate_vocabulary",
    )
    date_evenement_4 = schema.TextLine(
        title=(u"Date événement 4"), description="(jj/mm/aaaa)", required=False
    )

    fieldset("Média", fields=["auteur_du_media", "duree", "couleur_du_media"])

    auteur_du_media = schema.TextLine(title=(u"Auteur du média"), required=False)
    duree = schema.TextLine(title=(u"Durée"), required=False)
    couleur_du_media = schema.Choice(
        title=(u"Couleur du média"),
        required=False,
        vocabulary="library.core.vocabularies.colors_vocabulary",
    )

    fieldset(
        "Bien et PPPW",
        fields=[
            "group_identification",
            "nature_du_bien",
            "lieu_dit",
            "appellation_courante",
            "primary_category",
            "secondary_category",
            "autre",
            "group_localisation",
            "provinces",
            "municipal_entity",
            "group_owner",
            "owner_datas",
            "owner_name",
            "owner_address",
            "owner_zip_code",
            "owner_entity",
            "owner_email",
            "owner_phone",
            "group_item_status",
            "item_status",
            "group_item_description",
            "descriptif",
            "dimensions",
            "materiaux",
            "inscription_datation",
            "urban_context",
            "public_visibility",
            "direct_reachability",
            "group_item_conservation",
            "item_state",
            "noted_degradation",
            "reallocation_project",
            "group_item_history",
            "fonction_passee_et_actuelle",
            "group_item_notes_and_comments",
            "remarques_commentaires",
        ],
    )
    # 1. Identification de l'élément
    form.widget("group_identification", TextTitleFieldWidget)
    group_identification = schema.TextLine(
        title=(u"Identification de l’élément"), required=False
    )
    nature_du_bien = schema.TextLine(title=(u"Nature du bien"), required=False)
    lieu_dit = schema.TextLine(title=(u"Lieu dit"), required=False)
    appellation_courante = schema.TextLine(
        title=(u"Appellation courante"), required=False
    )
    form.widget("primary_category", TextTitleFieldWidget)
    primary_category = schema.TextLine(
        title=(u"Catégorie principale"),
        description=(
            u'La catégorie principale est renseignée sous l\'onglet "Catégorisation"'
        ),
        required=False,
    )
    form.widget("secondary_category", TextTitleFieldWidget)
    secondary_category = schema.TextLine(
        title=(u"Catégorie secondaire"),
        description=(
            u'La catégorie secondaire est renseignée sous l\'onglet "Catégorisation"'
        ),
        required=False,
    )
    autre = schema.Text(title=(u"Autre..."), required=False)
    # 2. Localisation de l'élément
    form.widget("group_localisation", TextTitleFieldWidget)
    group_localisation = schema.TextLine(
        title=(u"Localisation de l’élément"), required=False
    )

    provinces = schema.Choice(
        title=("Province"),
        required=False,
        vocabulary="library.core.vocabularies.provinces_vocabulary",
        default=None,
    )
    municipal_entity = schema.Choice(
        title=(u"Entité"),
        required=False,
        vocabulary="library.core.vocabularies.municipalentities_vocabulary",
        default=None,
    )

    # 3. Données relatives au propriétaire
    form.widget("group_owner", TextTitleFieldWidget)
    group_owner = schema.TextLine(
        title=(u"Données relatives au propriétaire"), required=False
    )

    form.read_permission(owner_datas="cmf.ModifyPortalContent")
    form.widget("owner_datas", RadioFieldWidget)
    owner_datas = schema.Choice(
        title=(u"Type de propriété"),
        required=False,
        values=["Privé", "Publique", "Statut inconnu"],
        default=None,
    )

    form.read_permission(owner_name="cmf.ModifyPortalContent")
    owner_name = schema.TextLine(
        title=(u"Nom-Prénom / Nom de l’organisme"), required=False
    )

    form.read_permission(owner_address="cmf.ModifyPortalContent")
    owner_address = schema.TextLine(title=(u"Adresse"), required=False)

    form.read_permission(owner_zip_code="cmf.ModifyPortalContent")
    owner_zip_code = schema.TextLine(title=(u"Code postal"), required=False)

    form.read_permission(owner_entity="cmf.ModifyPortalContent")
    owner_entity = schema.TextLine(title=(u"Entité/Commune"), required=False)

    form.read_permission(owner_email="cmf.ModifyPortalContent")
    owner_email = schema.TextLine(title=(u"Adresse e-mail"), required=False)

    form.read_permission(owner_phone="cmf.ModifyPortalContent")
    owner_phone = schema.TextLine(title=(u"Téléphone / Gsm"), required=False)

    # 4. Statut de l’élément
    form.widget("group_item_status", TextTitleFieldWidget)
    group_item_status = schema.TextLine(title=(u"Statut de l’élément"), required=False)

    form.widget(item_status=MultiSelect2FieldWidget)
    item_status = schema.List(
        title=(u"Statuts"),
        value_type=schema.Choice(
            title=(u"District(s) concerned"),
            values=[
                u"Monument",
                u"Site",
                u"Ensemble architectural",
                u"Zone de protection",
                safe_unicode(u"IPIC (repris à l'inventaire régional)"),
            ],
        ),
        required=False,
    )

    # 5. Description de l’élément

    form.widget("group_item_description", TextTitleFieldWidget)
    group_item_description = schema.TextLine(
        title=(u"Description de l’élément"), required=False
    )
    descriptif = schema.Text(title=(u"Descriptif"), required=False)
    dimensions = schema.TextLine(title=(u"Dimensions"), required=False)
    materiaux = schema.TextLine(title=(u"Matériaux"), required=False)
    inscription_datation = schema.Text(
        title=(u"Inscription(s) - Datation"), required=False
    )
    urban_context = schema.Text(
        title=(u"Contexte urbanistique et abords"), required=False
    )
    form.widget("public_visibility", RadioFieldWidget)
    public_visibility = schema.Bool(
        title=(u"Visibilité depuis le domaine public"), required=False
    )
    form.widget("direct_reachability", RadioFieldWidget)
    direct_reachability = schema.Bool(title=(u"Accessibilité directe"), required=False)

    # 6. Etat de conservation de l’élément

    form.widget("group_item_conservation", TextTitleFieldWidget)
    group_item_conservation = schema.TextLine(
        title=(u"Etat de conservation de l’élément"), required=False
    )

    # quid id=etat.
    form.widget("owner_datas", RadioFieldWidget)
    item_state = schema.Choice(
        title=(u"Etat général de l’élément"),
        required=False,
        values=["Bon", "Moyen", "Mauvais"],
        default=None,
    )
    noted_degradation = schema.Text(title=(u"Dégradation constatée"), required=False)
    form.widget("reallocation_project", RadioFieldWidget)
    reallocation_project = schema.Bool(
        title=(u"Projet de conservation/ Réaffectation en cours"), required=False
    )

    # 7. Historique/Anecdotes
    form.widget("group_item_history", TextTitleFieldWidget)
    group_item_history = schema.TextLine(
        title=(u"Historique/Anecdotes"), required=False
    )
    fonction_passee_et_actuelle = schema.Text(
        title=(u"Fonction(s) passée(s) et actuelle(s)"), required=False
    )

    # 8. Remarques
    form.widget("group_item_notes_and_comments", TextTitleFieldWidget)
    group_item_notes_and_comments = schema.TextLine(
        title=(u"Remarques"), required=False
    )
    remarques_commentaires = schema.Text(
        title=(u"Remarques et commentaires"), required=False
    )


class DateValidator(SimpleFieldValidator):

    regex_formats = {
        "\d{8}$": "%d%m%Y",
        "\d{6}$": "%m%Y",
        "\d{4}$": "%Y",
        "\d{1,2}/\d{1,2}/\d{4}$": "%d/%m/%Y",
        "\d{1,2}/\d{4}$": "%m/%Y",
        "\d{1,2}-\d{1,2}-\d{4}$": "%d-%m-%Y",
        "\d{1,2}-\d{4}$": "%m-%Y",
    }

    def validate(self, value, force=False):
        super(DateValidator, self).validate(value, force)
        if value:
            stripped = value.strip()
            for regex, datetime_format in self.regex_formats.items():
                if match(regex, stripped):
                    try:
                        datetime.strptime(stripped, datetime_format).date()
                        return True
                    except ValueError:
                        raise Invalid(u"Date invalide")
            raise Invalid(
                u"Format d'encodage non reconnu (jour/mois/année, mois/année ou année)"
            )


@implementer(IPatrimoine)
class Patrimoine(Container):
    """ """


class PatrimoineView(view.DefaultView):
    """ """

    def is_TextTitleWidget(self, current_widget):
        from library.core.widget.title import TextTitleWidget

        return isinstance(current_widget, TextTitleWidget)

    def is_there_any_fields_after_this_title(self, current_widget, lst_widgets):
        current_index = lst_widgets.index(current_widget)
        if (current_index + 1) < len(lst_widgets) and len(
            lst_widgets[current_index + 1].value
        ) > 0:
            return True
        else:
            return False

    def is_there_any_values(self, lst_widgets):
        if lst_widgets:
            return (
                False
                if set(
                    [
                        widget.value
                        if not isinstance(widget.value, list)
                        else widget.value[0]
                        if widget.value != [] and widget.value[0] != "unselected"
                        else ""
                        for widget in lst_widgets
                    ]
                )
                == {""}
                else True
            )
        else:
            return False

    def is_geolocated(self):
        return is_geolocated(self.context)


@indexer(IPatrimoine)
def searchabletext_patrimoine(object, **kw):
    """
    Indexes the following field types in Patrimoine objects,
    making them available in Full Text Search:
    - text
    - rich text
    - keywords
    - taxonomies
    """
    result = []
    subjects = getattr(object, "subject", None)
    if type(subjects) is tuple:
        text = " ".join([s for s in subjects if isinstance(s, six.text_type)])
        result.append(text)

    for schemata in iterSchemata(object):
        if "collective.taxonomy.generated" in str(schemata):
            value = getattr(object, "taxonomy_{0}".format(schemata.__name__), None)
            if value:
                value = [value] if isinstance(value, six.text_type) else value
                translator = queryUtility(
                    ITaxonomy, name="collective.taxonomy.{0}".format(schemata.__name__)
                )
                for taxonomy_id in value:
                    translation = translator.translate(
                        taxonomy_id, target_language="fr"
                    )
                    text = translation
                    result.append(text)
            continue

        for field_name, field_type in getFields(schemata).items():
            value = getattr(object, field_name, None)
            if isinstance(value, six.text_type):
                text = value
                result.append(text)
            elif IRichTextValue.providedBy(value):
                transforms = getToolByName(object, "portal_transforms")
                text = (
                    transforms.convertTo(
                        "text/plain", value.raw, mimetype=value.mimeType
                    )
                    .getData()
                    .strip()
                )
                result.append(text)

    return " ".join(result)


def is_geolocated(obj):
    if getattr(obj, "geolocation", None) is not None:
        if (
            getattr(obj.geolocation, "latitude", None) is not None
            and getattr(obj.geolocation, "longitude", None) is not None
        ):
            if float(obj.geolocation.latitude) != float(0) and float(
                obj.geolocation.longitude
            ) != float(0):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


@indexer(IPatrimoine)
def is_geolocated_indexer(obj):
    return is_geolocated(obj)
