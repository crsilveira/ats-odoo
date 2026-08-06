from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InsuranceNominee(models.Model):
    _name = 'insurance.nominee'
    _description = 'Insurance Policy Nominee'
    _rec_name = 'name'

    policy_id = fields.Many2one(
        'insurance.policy',
        string='Policy',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Nominee Name', required=True)
    age = fields.Integer(string='Age')
    relationship = fields.Selection(
        selection=[
            ('spouse', 'Spouse'),
            ('child', 'Child'),
            ('parent', 'Parent'),
            ('sibling', 'Sibling'),
            ('other', 'Other'),
        ],
        string='Relationship',
        required=True,
    )
    percentage = fields.Float(string='Benefit Percentage (%)', default=100.0)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    @api.constrains('percentage')
    def _check_percentage(self):
        for rec in self:
            if rec.percentage <= 0 or rec.percentage > 100:
                raise ValidationError(_('Benefit percentage must be between 1 and 100.'))

    @api.constrains('policy_id', 'percentage')
    def _check_total_percentage(self):
        for rec in self:
            nominees = self.env['insurance.nominee'].search([
                ('policy_id', '=', rec.policy_id.id),
            ])
            total = sum(nominees.mapped('percentage'))
            if total > 100:
                raise ValidationError(_('Total nominee benefit percentage cannot exceed 100%.'))
