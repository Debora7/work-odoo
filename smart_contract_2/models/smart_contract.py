from odoo import models, fields
from odoo.exceptions import UserError

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
    
    def populate_with_data(self):
        """Populate current record with data from template_contract_id."""
        self.ensure_one()
        if not self.template_contract_id:
            raise UserError("No template selected.")

        # 1. Curățăm datele existente (folosind 5 - UNLINK ALL)
        # Sudo() este folosit doar pe scriere dacă userul nu are drepturi pe template
        vals = {
            'related_object_ids': [(5, 0, 0)],
            'child_ids': [(5, 0, 0)],
            'elemente_ids': [(5, 0, 0)],
        }

        # 2. Mapăm datele din template folosind metode recursive simplificate
        template = self.template_contract_id
        
        if template.related_object_ids:
            vals['related_object_ids'] = self._prepare_related_objects(template.related_object_ids)

        if template.child_ids:
            vals['child_ids'] = self._prepare_child_contracts(template.child_ids)

        if template.elemente_ids:
            # Filtrăm doar rădăcinile pentru a începe recursivitatea corect
            root_elements = template.elemente_ids.filtered(lambda e: not e.parent_id)
            vals['elemente_ids'] = self._prepare_child_elements(root_elements)

        # 3. Aplicăm toate modificările într-un singur write pentru performanță
        self.sudo().write(vals)
        self.sudo().reNumber()

    def _prepare_related_objects(self, related_objects):
        """Prepares commands for related_object_ids including nested aditional_data."""
        res = []
        for ro in related_objects:
            ro_data = {
                'server_action': ro.server_action.id,
                'autoexec': ro.autoexec,
                'racursiv': ro.racursiv,
                'exec_date': ro.exec_date,
                'aditional_data_ids': [
                    (0, 0, adro.copy_data()[0]) for adro in ro.aditional_data_ids
                ]
            }
            res.append((0, 0, ro_data))
        return res

    def _prepare_child_contracts(self, child_contracts):
        """Recursive preparation for child contracts."""
        res = []
        for child in child_contracts:
            child_data = {
                'company_id': child.company_id.id,
                'document_type': child.document_type,
                'elemente_ids': self._prepare_child_elements(child.elemente_ids),
                # Dacă child_ids este recursiv și în contracte:
                'child_ids': self._prepare_child_contracts(child.child_ids) if child.child_ids else []
            }
            res.append((0, 0, child_data))
        return res

    def _prepare_child_elements(self, elements):
        """Recursive preparation for elements and their attributes."""
        res = []
        for elem in elements:
            # Folosim copy_data() pentru a prelua automat câmpurile simple (name, numar, tip, text)
            # și excludem câmpurile relaționale pe care le gestionăm manual
            elem_vals = elem.copy_data()[0]
            
            # Curățăm sau suprascriem câmpurile ierarhice
            elem_vals.update({
                'child_ids': self._prepare_child_elements(elem.child_ids),
                'attribute_ids': [
                    (0, 0, attr.copy_data()[0]) for attr in elem.attribute_ids
                ]
            })
            res.append((0, 0, elem_vals))
        return res