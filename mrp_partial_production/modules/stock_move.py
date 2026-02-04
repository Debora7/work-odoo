from odoo import models
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _set_quantity_done(self, qty):
        _logger.error("_set_quantity_done called!!!")
        if self.env.context.get('skip_qty_calculation'):
            _logger.info(f"self.production_id.qty_producing: {self.production_id.qty_producing}")
            qty = self.product_uom.round((self.production_id.qty_producing) * self.unit_factor) 
        
        return super(StockMove, self)._set_quantity_done(qty)
    
    def write(self, vals):
        if self.env.context.get('skip_qty_calculation_finished') and vals.get('quantity'):
            vals['quantity'] = self.env.context.get('skip_qty_calculation_finished')

        return super().write(vals)