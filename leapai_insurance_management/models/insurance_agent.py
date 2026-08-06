from odoo import api, fields, models


class InsuranceAgent(models.Model):
    _name = 'insurance.agent'
    _description = 'Insurance Agent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Agent Name', required=True, tracking=True)
    code = fields.Char(string='Agent Code', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Contact', ondelete='restrict')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    commission_rate = fields.Float(string='Commission Rate (%)', default=5.0)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    policy_count = fields.Integer(
        string='Policies',
        compute='_compute_policy_count',
    )
    commission_total = fields.Monetary(
        string='Total Commission',
        compute='_compute_commission_total',
        currency_field='currency_id',
    )
    active = fields.Boolean(string='Active', default=True)
    note = fields.Text(string='Notes')

    # _code_unique = models.Constraint(
    #     'unique(code)',
    #     'Agent code must be unique.',
    # )
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Agent code must be unique.')
    ]

    @api.depends()
    def _compute_policy_count(self):
        for rec in self:
            rec.policy_count = self.env['insurance.policy'].search_count([
                ('agent_id', '=', rec.id)
            ])

    @api.depends('policy_count', 'commission_rate')
    def _compute_commission_total(self):
        for rec in self:
            policies = self.env['insurance.policy'].search([
                ('agent_id', '=', rec.id),
                ('state', 'not in', ['cancelled']),
            ])
            total_premium = sum(policies.mapped('premium_amount'))
            rec.commission_total = total_premium * (rec.commission_rate / 100.0)

    def action_view_policies(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Policies',
            'res_model': 'insurance.policy',
            'view_mode': 'list,form',
            'domain': [('agent_id', '=', self.id)],
            'context': {'default_agent_id': self.id},
        }
