from odoo import models
import logging

_logger = logging.getLogger('__name__')

class MrpProduction(models.Model):
    _name='mrp.production'
    _inherit='mrp.production'

    def button_mark_partial_production(self):
        self._post_inventory(cancel_backorder=False)
        new_quantity_to_produce = self.product_qty - self.qty_producing
        
        self.write({
            'product_qty': new_quantity_to_produce,
            'qty_producing': 0
        })