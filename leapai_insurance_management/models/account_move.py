from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    insurance_policy_id = fields.Many2one(
        'insurance.policy',
        string='Insurance Policy',
        copy=False,
    )
    insurance_claim_id = fields.Many2one(
        'insurance.claim',
        string='Insurance Claim',
        copy=False,
    )
