from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_insurance_customer = fields.Boolean(string='Insurance Customer', default=False)
    insurance_policy_count = fields.Integer(
        string='Policies',
        compute='_compute_insurance_counts',
    )
    insurance_claim_count = fields.Integer(
        string='Claims',
        compute='_compute_insurance_counts',
    )

    def _compute_insurance_counts(self):
        for partner in self:
            partner.insurance_policy_count = self.env['insurance.policy'].search_count([
                ('partner_id', '=', partner.id),
            ])
            partner.insurance_claim_count = self.env['insurance.claim'].search_count([
                ('partner_id', '=', partner.id),
            ])

    def action_view_insurance_policies(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Insurance Policies',
            'res_model': 'insurance.policy',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_view_insurance_claims(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Insurance Claims',
            'res_model': 'insurance.claim',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
        }
