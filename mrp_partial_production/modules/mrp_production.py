from odoo import models, fields, api
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit='mrp.production'

    produced_qty = fields.Integer()

    def button_mark_partial_production(self):
        """
            self.product_qty -> Total quantity to produce to finish the MO
            self.qty_producing -> Quantity that you produce now (can be less, equal or more than product_qty)
            self.produced_qty -> Quantity already produced through a partial production
        """

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
            
        move_quantity = self.product_uom_id.round(self.qty_producing, rounding_method='HALF-UP')
        self.with_context(skip_qty_calculation_finished=move_quantity)._post_inventory(cancel_backorder=False)

        produced_qty = self.produced_qty + self.qty_producing

        moves = self.env['stock.move'].search([('production_id', '=', self.id)])
        moves_to_finish = moves.filtered(lambda x: x.state not in ('done', 'cancel'))

        if moves_to_finish:
            moves_to_finish._action_done()

        if produced_qty == self.product_qty:
            return self.with_context(last_partial_production=True, skip_backorder=True).button_mark_done()

        self.write({
            'produced_qty': produced_qty,
            'qty_producing': 0
        })
        

    @api.onchange('qty_producing')
    def _onchange_qty_producing(self):
        _logger.info('_onchange_qty_producing trigger')
        super(MrpProduction, self.with_context(skip_qty_calculation=True ))._onchange_qty_producing()

    def _post_inventory(self, cancel_backorder):
        if self.env.context.get('last_partial_production'):
            return True
        
        return super(MrpProduction, self)._post_inventory(cancel_backorder=cancel_backorder)