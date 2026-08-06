from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class InsurancePolicy(models.Model):
    _name = 'insurance.policy'
    _description = 'Insurance Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'issue_date desc, id desc'

    name = fields.Char(
        string='Policy Name',
        required=True,
        default='/',
        tracking=True,
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        tracking=True,
    )
    category_id = fields.Many2one(
        'insurance.category',
        string='Category',
        required=True,
        tracking=True,
        domain=[('parent_id', '=', False)],
    )
    sub_category_id = fields.Many2one(
        'insurance.category',
        string='Sub-category',
        tracking=True,
    )
    policy_term_id = fields.Many2one(
        'insurance.term',
        string='Policy Term',
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Policyholder',
        required=True,
        tracking=True,
    )
    agent_id = fields.Many2one(
        'insurance.agent',
        string='Agent',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True,
    )
    premium_amount = fields.Monetary(
        string='Premium Amount',
        currency_field='currency_id',
        tracking=True,
    )
    payment_type = fields.Selection(
        selection=[
            ('fixed', 'Lump Sum'),
            ('installment', 'Monthly Installments'),
        ],
        string='Payment Type',
        default='fixed',
        tracking=True,
    )
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    duration = fields.Integer(
        string='Duration (Months)',
        compute='_compute_duration',
        store=True,
        readonly=False,
    )
    insured_name = fields.Char(string='Insured Person Name')
    insured_dob = fields.Date(string='Date of Birth')
    insured_gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        string='Gender',
    )
    insured_phone = fields.Char(string='Phone')
    insured_email = fields.Char(string='Email')
    nominee_ids = fields.One2many(
        'insurance.nominee',
        'policy_id',
        string='Nominees',
    )
    document_ids = fields.One2many(
        'insurance.document',
        'policy_id',
        string='Documents',
    )
    claim_ids = fields.One2many(
        'insurance.claim',
        'policy_id',
        string='Insurance Claims',
    )
    claim_count = fields.Integer(
        string='Claims Count',
        compute='_compute_claim_count',
    )
    invoice_count = fields.Integer(
        string='Invoices',
        compute='_compute_invoice_count',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('running', 'Running'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    description = fields.Html(string='Description')
    terms_conditions = fields.Html(string='Terms & Conditions')
    note = fields.Text(string='Internal Notes')

    def _compute_claim_count(self):
        for rec in self:
            rec.claim_count = len(rec.claim_ids)

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([
                ('insurance_policy_id', '=', rec.id),
                ('move_type', '=', 'out_invoice'),
            ])

    @api.depends('policy_term_id')
    def _compute_duration(self):
        for rec in self:
            if rec.policy_term_id:
                rec.duration = rec.policy_term_id.duration_months
            elif not rec.duration:
                rec.duration = 12

    @api.onchange('policy_term_id')
    def _onchange_policy_term_id(self):
        if self.policy_term_id:
            self.premium_amount = self.policy_term_id.premium_amount
            self.duration = self.policy_term_id.duration_months
            if self.issue_date:
                self.expiry_date = self.issue_date + relativedelta(months=self.policy_term_id.duration_months)

    @api.onchange('issue_date', 'duration')
    def _onchange_issue_date(self):
        if self.issue_date and self.duration:
            self.expiry_date = self.issue_date + relativedelta(months=self.duration)

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.sub_category_id = False

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft policies can be confirmed.'))
            if not rec.reference:
                rec.reference = self.env['ir.sequence'].next_by_code('insurance.policy') or '/'
            rec.write({'state': 'confirmed'})
            rec.message_post(body=_('Policy confirmed. Reference: %s') % rec.reference)

    def action_running(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError(_('Only confirmed policies can be set to running.'))
            rec.write({'state': 'running'})
            rec.message_post(body=_('Policy is now active/running.'))

    def action_expire(self):
        for rec in self:
            if rec.state not in ('running', 'confirmed'):
                raise UserError(_('Cannot expire policy in current state.'))
            rec.write({'state': 'expired'})
            rec.message_post(body=_('Policy has expired.'))

    def action_cancel(self):
        for rec in self:
            if rec.state in ('cancelled',):
                raise UserError(_('Policy is already cancelled.'))
            rec.write({'state': 'cancelled'})
            rec.message_post(body=_('Policy has been cancelled.'))

    def action_renew(self):
        self.ensure_one()
        new_policy = self.copy({
            'name': self.name + ' (Renewed)',
            'reference': False,
            'state': 'draft',
            'issue_date': fields.Date.today(),
        })
        self.message_post(body=_('Policy renewed. New policy: %s') % new_policy.name)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Renewed Policy'),
            'res_model': 'insurance.policy',
            'res_id': new_policy.id,
            'view_mode': 'form',
        }

    def action_create_invoice(self):
        self.ensure_one()
        if self.state not in ('confirmed', 'running'):
            raise UserError(_('Invoice can only be created for confirmed or running policies.'))

        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        if not journal:
            raise UserError(_('No sales journal found. Please configure a sales journal.'))

        # Find or create insurance premium product
        product = self.env['product.product'].search([
            ('name', '=', 'Insurance Premium'),
            ('type', '=', 'service'),
        ], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Insurance Premium',
                'type': 'service',
            })

        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'insurance_policy_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'name': _('Insurance Premium: %s') % (self.reference or self.name),
                'quantity': 1.0,
                'price_unit': self.premium_amount,
                'product_id': product.id,
            })],
        }
        move = self.env['account.move'].create(move_vals)
        self.message_post(body=_('Invoice created: %s') % move.name)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice'),
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [
                ('insurance_policy_id', '=', self.id),
                ('move_type', '=', 'out_invoice'),
            ],
        }

    def action_view_claims(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Claims'),
            'res_model': 'insurance.claim',
            'view_mode': 'list,form',
            'domain': [('policy_id', '=', self.id)],
            'context': {'default_policy_id': self.id},
        }
