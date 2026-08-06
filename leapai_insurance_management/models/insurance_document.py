from odoo import fields, models


class InsuranceDocument(models.Model):
    _name = 'insurance.document'
    _description = 'Insurance Policy Document'
    _rec_name = 'name'

    policy_id = fields.Many2one(
        'insurance.policy',
        string='Policy',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection(
        selection=[
            ('id', 'ID/Passport'),
            ('medical', 'Medical Report'),
            ('income', 'Income Proof'),
            ('other', 'Other'),
        ],
        string='Document Type',
        required=True,
        default='other',
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
    )
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('submitted', 'Submitted'),
            ('verified', 'Verified'),
        ],
        string='Status',
        default='pending',
        required=True,
    )
    note = fields.Char(string='Notes')
