from odoo.addons.component.core import Component


class CrmLeadListener(Component):
    _name = 'crm.lead.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['crm.lead']

    def on_record_write(self, record, fields=None):
        company = self.env.user.company_id
        if "stage_id" in fields and \
                record.stage_id.id == company.start_provisioning_crm_stage.id:
            for line in record.lead_line_ids:
                self.start_provisioning(line)

    # Overwrite if you use another system for the provisioning.
    def start_provisioning(self, line):
        line.start_provisioning()
