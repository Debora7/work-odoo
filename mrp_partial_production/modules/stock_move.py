from odoo import models
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _set_quantity_done(self, qty):
        if self.env.context.get('skip_qty_calculation'):
            production = self.raw_material_production_id or self.production_id
            if production:
                qty = self.product_uom.round((production.qty_producing) * self.unit_factor)

        return super(StockMove, self)._set_quantity_done(qty)
    
    def write(self, vals):
        skip_qty = self.env.context.get('skip_qty_calculation_finished')
        
        if skip_qty:
            for move in self:
                if move.production_id:
                    vals['quantity'] = skip_qty
                    
        return super().write(vals)