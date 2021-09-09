# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BaseSubstateType(models.Model):
    _inherit = 'base.substate.type'
    product_category_ids = fields.Many2many(
        "product.category",
        string="Product categories",
    )


class TargetStateValue(models.Model):
    _inherit = 'target.state.value'


class BaseSubstate(models.Model):
    _inherit = 'base.substate'
    product_category_ids = fields.Many2many(
        related="target_state_value_id.base_substate_type_id.product_category_ids"
    )
    force_state_change = fields.Boolean(
        string="Force state change",
        help="Set to true to set sale order state to substate target value"
    )
