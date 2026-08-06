from odoo import api, fields, models


class InsuranceTerm(models.Model):
    _name = 'insurance.term'
    _description = 'Insurance Policy Term'
    _rec_name = 'name'
    _order = 'duration_months'

    name = fields.Char(string='Term Name', required=True)
    duration_months = fields.Integer(string='Duration (Months)', default=12)
    premium_amount = fields.Monetary(string='Premium Amount', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    active = fields.Boolean(string='Active', default=True)

    # _name_unique = models.Constraint(
    #     'unique(name)',
    #     'Term name must be unique.',
    # )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Term name must be unique.')
    ]
