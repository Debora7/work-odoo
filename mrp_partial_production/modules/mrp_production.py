from odoo import models, fields
import logging

_logger = logging.getLogger('__name__')

class MrpProduction(models.Model):
    _name='mrp.production'
    _inherit='mrp.production'

    produced_qty = fields.Integer()

    def button_mark_partial_production(self):
        if not self.env.context.get('skip_warning'):
            if self.qty_producing > self.product_qty or (self.qty_producing + self.produced_qty) > self.product_qty:
                return {
                    'name': 'Warning',
                    'type': 'ir.actions.act_window',
                    'res_model': 'partial.production.warning',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': 'You will produce more than planned. Is this intended?',
                        'active_id': self.id,
                    }
                }
            
        self._post_inventory(cancel_backorder=False)
        produced_qty = self.produced_qty + self.qty_producing

        if(produced_qty == self.product_qty):
            self.write({
                'state': 'done',
            })
        
        self.write({
            'produced_qty': produced_qty,
            'qty_producing': 0
        })