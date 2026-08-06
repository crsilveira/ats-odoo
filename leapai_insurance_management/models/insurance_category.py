from odoo import api, fields, models


class InsuranceCategory(models.Model):
    _name = 'insurance.category'
    _description = 'Insurance Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    parent_id = fields.Many2one(
        'insurance.category',
        string='Parent Category',
        ondelete='restrict',
        index=True,
    )
    child_ids = fields.One2many(
        'insurance.category',
        'parent_id',
        string='Sub-categories',
    )
    policy_count = fields.Integer(
        string='Policies',
        compute='_compute_policy_count',
    )
    color = fields.Integer(string='Color Index', default=0)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')

    # _name_parent_unique = models.Constraint(
    #     'unique(name, parent_id)',
    #     'Category name must be unique within the same parent.',
    # )
    _sql_constraints = [
        ('name_parent_unique', 'UNIQUE(name, parent_id)', 'Category name must be unique within the same parent.')
    ]

    @api.depends('child_ids')
    def _compute_policy_count(self):
        for rec in self:
            rec.policy_count = self.env['insurance.policy'].search_count([
                ('category_id', '=', rec.id)
            ])

    def action_view_policies(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Policies',
            'res_model': 'insurance.policy',
            'view_mode': 'list,form',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }
