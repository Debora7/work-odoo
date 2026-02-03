from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _set_quantity_done(self, qty):
        if self.env.context.get('skip_qty_calculation'):
            new_quant = 2
            
            return super(StockMove, self)._set_quantity_done(self.env.context.get('quantity_right'))
        
        return super(StockMove, self)._set_quantity_done(qty)