# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class res_company(models.Model):
  _inherit = 'res.company'

  start_provisioning_crm_stage = fields.Many2one('crm.stage',
    string=_("Start provisioning CRM stage"), ondelete='restrict')
