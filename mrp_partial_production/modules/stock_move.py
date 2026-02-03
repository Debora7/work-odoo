from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _set_quantity_done(self, qty):
        _logger.info('_set_quantity_done called')
        if self.env.context.get('skip_qty_calculation'):
            _logger.info(f"self.env.context.get('skip_qty_calculation'): {self.env.context.get('skip_qty_calculation')}")
            return super(StockMove, self)._set_quantity_done(self.env.context.get('quantity_right'))
        
        return super(StockMove, self)._set_quantity_done(qty)