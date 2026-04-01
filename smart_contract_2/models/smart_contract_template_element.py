from odoo import models, fields

class SmartContractTemplateElement(models.Model):
    _name = "smart.contract.template.element"
    _description = "Smart Contract Template element"

    name = fields.Char(string="Name")
    numar = fields.Char(string="Number", store=True)
    tip = fields.Selection([("capitol", "Chapter"), ("articol", "Article"), ("alineat", "Paragraph")], string="Type")
    text = fields.Html(string="Content")
    template_id = fields.Many2one(comodel_name="smart.contract.template", string="Template", ondelete="cascade", required=True, readonly=True)