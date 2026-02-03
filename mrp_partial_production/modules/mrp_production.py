from odoo import models, fields, api
import logging

_logger = logging.getLogger('__name__')

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

    @api.onchange('qty_producing')
    def _onchange_qty_producing(self):
        _logger.info(">>>>>>>>>on changed called!!!")
        quantity_right = self.qty_producing
        
        return super(MrpProduction, self.with_context(
            skip_qty_calculation=True, 
            quantity_right=quantity_right
        ))._onchange_qty_producing()
        
    def _change_producing(self):
        _logger.info('_change_producing called')
        if self.env.context.get('skip_qty_calculation'):
            self = self.with_context(
                skip_qty_calculation=True,
                quantity_right=self.env.context.get('quantity_right')
            )
        return super(MrpProduction, self)._change_producing()
    
    def _set_qty_producing(self, pick_manual_consumption_moves=True):
        if self.product_id.tracking == 'serial':
            qty_producing_uom = self.product_uom_id._compute_quantity(self.qty_producing, self.product_id.uom_id, rounding_method='HALF-UP')
            qty_production_uom = self.product_uom_id._compute_quantity(self.product_qty, self.product_id.uom_id, rounding_method='HALF-UP')
            # allow changing a non-zero value to a 0 to not block mass produce feature
            if qty_producing_uom != qty_production_uom and not (qty_producing_uom == 0 and self._origin.qty_producing != self.qty_producing):
                self.qty_producing = self.product_id.uom_id._compute_quantity(len(self.lot_producing_ids), self.product_uom_id, rounding_method='HALF-UP')

        # waiting for a preproduction move before assignement
        is_waiting = self.warehouse_id.manufacture_steps != 'mrp_one_step' and self.picking_ids.filtered(lambda p: p.picking_type_id == self.warehouse_id.pbm_type_id and p.state not in ('done', 'cancel'))

        for move in (
            self.move_raw_ids.filtered(lambda m: not is_waiting or m.product_id.tracking == 'none')
            | self.move_finished_ids.filtered(lambda m: m.product_id != self.product_id or m.product_id.tracking == 'serial')
        ):
            is_byproduct = move in self.move_byproduct_ids
            # Never update already produced by-product moves.
            if move.picked and (is_byproduct or move.manual_consumption):
                continue

            # sudo needed for portal users
            if move.sudo()._should_bypass_set_qty_producing():
                continue

            new_qty = move.product_uom.round((self.qty_producing - self.qty_produced) * move.unit_factor)

            if self.env.context.get('skip_qty_calculation'):
                move._set_quantity_done(self.env.context.get('quantity_right'))

            move._set_quantity_done(new_qty)
            if (not move.manual_consumption or pick_manual_consumption_moves) \
                    and move.quantity \
                    and not is_byproduct \
                    and (move.raw_material_production_id or move.product_id.tracking != 'serial'):
                move.picked = True