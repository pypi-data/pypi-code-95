from Products.PloneMeeting.Meeting import Meeting
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.PloneMeeting.config import WriteRiskyConfig

from Products.Archetypes.atapi import BooleanField, Schema


def update_item_schema(baseSchema):
    baseSchema['detailedDescription'].widget.description = "DetailedDescriptionMethode"
    baseSchema['detailedDescription'].widget.description_msgid = "detailedDescription_item_descr"
    return baseSchema


MeetingItem.schema = update_item_schema(MeetingItem.schema)


def update_meeting_schema(baseSchema):
    baseSchema['assembly'].widget.description_msgid = "assembly_meeting_descr"
    return baseSchema


Meeting.schema = update_meeting_schema(Meeting.schema)


def update_config_schema(baseSchema):
    specificSchema = Schema((
        BooleanField(
            name='initItemDecisionIfEmptyOnDecide',
            default=True,
            widget=BooleanField._properties['widget'](
                description="InitItemDecisionIfEmptyOnDecide",
                description_msgid="init_item_decision_if_empty_on_decide",
                label='Inititemdecisionifemptyondecide',
                label_msgid='MeetingIDEA_label_initItemDecisionIfEmptyOnDecide',
                i18n_domain='PloneMeeting'),
            write_permission=WriteRiskyConfig,
        ),
    ), )

    completeConfigSchema = baseSchema + specificSchema.copy()
    return completeConfigSchema


MeetingConfig.schema = update_config_schema(MeetingConfig.schema)

# Classes have already been registered, but we register them again here
# because we have potentially applied some schema adaptations (see above).
# Class registering includes generation of accessors and mutators, for
# example, so this is why we need to do it again now.
from Products.PloneMeeting.config import registerClasses

registerClasses()
