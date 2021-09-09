# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    product_category_id = fields.Many2one(related="product_id.product_tmpl_id.categ_id")
    product_id = fields.Many2one(
        "product.product",
        compute='_compute_product',
        string="Product",
    )
    # TODO: check if we need is_telecom
    is_telecom = fields.Boolean(string="Is Telecom order?")
    is_mobile = fields.Boolean(
        compute='_get_is_mobile',
        store=True
    )
    is_broadband = fields.Boolean(
        compute='_get_is_broadband',
        store=True
    )
    broadband_isp_info = fields.Many2one(
        'broadband.isp.info',
        string='Broadband ISP Info'
    )
    mobile_isp_info = fields.Many2one(
        'mobile.isp.info',
        string='Mobile ISP Info'
    )

    def _compute_product(self):
        for order in self:
            if order.order_line:
                order.product_id = order.order_line[0].product_id

    @api.depends('product_id')
    def _get_is_mobile(self):
        mobile = self.env.ref('telecom.mobile_service')
        for record in self:
            record.is_mobile = (
                mobile.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends('product_id')
    def _get_is_broadband(self):
        adsl = self.env.ref('telecom.broadband_adsl_service')
        fiber = self.env.ref('telecom.broadband_fiber_service')
        radiofrequency = self.env.ref('telecom.broadband_radiofrequency_service')
        for record in self:
            record.is_broadband = (
                record.product_id.product_tmpl_id.categ_id.id in [adsl.id, fiber.id, radiofrequency.id]
            )

    def _get_default_substate_domain(self, state_val=False):
        domain = super(SaleOrder, self)._get_default_substate_domain(state_val)
        domain += [('product_category_ids', '=', self.product_category_id.id)]
        return domain

    def _get_substate_type(self):
        return self.env['base.substate.type'].search(
            [
                ('model', '=', self._name),
                ('product_category_ids', '=', self.product_category_id.id),
            ], limit=1)

    @api.constrains("substate_id", "state")
    def check_substate_id_value(self):
        sale_states = dict(self._fields["state"].selection)
        for order in self:
            order_category = order.product_id.product_tmpl_id.categ_id
            substate_categories = (
                order.substate_id.target_state_value_id.base_substate_type_id.product_category_ids
            )
            target_state = (
                order.substate_id.target_state_value_id.target_state_value
            )
            if order.substate_id and order.state != target_state:
                raise ValidationError(
                    _(
                        'The substate "%s" is not defined for the state'
                        ' "%s" but for "%s" '
                    )
                    % (
                        order.substate_id.name,
                        _(sale_states[order.state]),
                        _(sale_states[target_state]),
                    )
                )
            if order.substate_id and order_category not in substate_categories:
                raise ValidationError(
                    _(
                        'The substate "%s" is not in "%s"'
                    )
                    % (
                        order.substate_id.name,
                        substate_categories,
                    )
                )

    @api.multi
    def _prepare_contract_value(self, contract_template):
        self.ensure_one()
        values = super(SaleOrder, self)._prepare_contract_value(contract_template)
        values.update({
            'product_category_id': self.product_category_id.id,
            'broadband_isp_info': self.broadband_isp_info.id,
            'mobile_isp_info': self.mobile_isp_info.id,
        })
        return values
