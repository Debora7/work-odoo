from odoo import models, fields
import logging

_logger = logging.getLogger('__name__')

class MrpProduction(models.Model):
    _name='mrp.production'
    _inherit='mrp.production'

    produced_qty = fields.Integer()

    def button_mark_partial_production(self):
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