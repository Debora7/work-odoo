from odoo import models, fields, api

class SmartContract(models.Model):
    _name = "smart.contract"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Smart Contract"
    
    name = fields.Char(string="Name", store=True)
    
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    signed_date = fields.Date(string="Sign Date")
     
    contract_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('undefined', 'Undefined'),
    ], string="Tip Contract", required=True, default='undefined')
    
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible', index=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")
    legal_partner_id = fields.Many2one("res.partner", string="Legal Customer Person")
    
    template_contract_id = fields.Many2one(comodel_name="smart.contract.template", string="Contract Template")
    
    visible_elements_ids = fields.Many2many(
        'smart.contract.template.element', 
        compute='_compute_visible_elements',
        string='Elemente Template'
    )

    @api.depends('template_contract_id')
    def _compute_visible_elements(self):
        for record in self:
            if record.template_contract_id:
                record.visible_elements_ids = record.template_contract_id.elemente_ids
            else:
                record.visible_elements_ids = [(5, 0, 0)]