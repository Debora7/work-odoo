from odoo import models, fields

class SmartContractTemplate(models.Model):
    _name = "smart.contract.template"
    _description = "Smart contract template"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name")
    elemente_ids = fields.One2many(comodel_name="smart.contract.template.element", inverse_name="template_id", string="Articles", copy=True)