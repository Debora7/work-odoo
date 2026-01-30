from odoo import models, fields

class PartialProductionWarning(models.Model):
    _name = 'partial.production.warning'

    message = fields.Text(readonly=True)

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        production = self.env["mrp.production"].browse(active_id)

        return production.with_context(skip_warning=True).button_mark_partial_production()