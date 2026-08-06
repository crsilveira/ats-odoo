from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InsuranceClaim(models.Model):
    _name = 'insurance.claim'
    _description = 'Insurance Claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'claim_date desc, id desc'

    name = fields.Char(
        string='Claim Name',
        required=True,
        default='/',
        tracking=True,
    )
    reference = fields.Char(string='Reference', readonly=True, copy=False)
    policy_id = fields.Many2one(
        'insurance.policy',
        string='Policy',
        required=True,
        tracking=True,
        ondelete='restrict',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Policyholder',
        related='policy_id.partner_id',
        store=True,
    )
    claim_date = fields.Date(
        string='Claim Date',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    claim_amount = fields.Monetary(
        string='Claim Amount',
        currency_field='currency_id',
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    reason = fields.Selection(
        selection=[
            ('accident', 'Accident'),
            ('theft', 'Theft'),
            ('fire', 'Fire'),
            ('medical', 'Medical Emergency'),
            ('natural_disaster', 'Natural Disaster'),
            ('other', 'Other'),
        ],
        string='Claim Reason',
        required=True,
        tracking=True,
    )
    reason_detail = fields.Text(string='Reason Details')
    document_ids = fields.Many2many(
        'ir.attachment',
        'insurance_claim_attachment_rel',
        'claim_id',
        'attachment_id',
        string='Supporting Documents',
    )
    invoice_count = fields.Integer(
        string='Settlements',
        compute='_compute_invoice_count',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('to_approve', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    rejection_reason = fields.Text(string='Rejection Reason', tracking=True)
    settlement_amount = fields.Monetary(
        string='Settlement Amount',
        currency_field='currency_id',
        tracking=True,
    )
    note = fields.Text(string='Internal Notes')

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([
                ('insurance_claim_id', '=', rec.id),
                ('move_type', '=', 'in_invoice'),
            ])

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft claims can be submitted.'))
            if not rec.reference:
                rec.reference = self.env['ir.sequence'].next_by_code('insurance.claim') or '/'
            rec.write({'state': 'submitted'})
            rec.message_post(body=_('Claim submitted.'))

    def action_to_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted claims can be sent for approval.'))
            rec.write({'state': 'to_approve'})
            rec.message_post(body=_('Claim sent for approval.'))

    def action_approve(self):
        for rec in self:
            if rec.state != 'to_approve':
                raise UserError(_('Only claims pending approval can be approved.'))
            rec.write({'state': 'approved'})
            rec.message_post(body=_('Claim approved.'))

    def action_reject(self):
        for rec in self:
            if rec.state not in ('submitted', 'to_approve'):
                raise UserError(_('Only submitted or pending approval claims can be rejected.'))
            rec.write({'state': 'rejected'})
            rec.message_post(body=_('Claim rejected.'))

    def action_reset(self):
        for rec in self:
            if rec.state not in ('submitted', 'rejected'):
                raise UserError(_('Cannot reset claim in current state.'))
            rec.write({'state': 'draft'})
            rec.message_post(body=_('Claim reset to draft.'))

    def action_create_settlement(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_('Only approved claims can have a settlement bill created.'))

        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        if not journal:
            raise UserError(_('No purchase journal found. Please configure a purchase journal.'))

        # Find or create insurance settlement product
        product = self.env['product.product'].search([
            ('name', '=', 'Insurance Settlement'),
            ('type', '=', 'service'),
        ], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Insurance Settlement',
                'type': 'service',
            })

        move_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'insurance_claim_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'name': _('Settlement for Claim: %s') % self.reference or self.name,
                'quantity': 1.0,
                'price_unit': self.settlement_amount or self.claim_amount,
                'product_id': product.id,
            })],
        }
        move = self.env['account.move'].create(move_vals)
        self.message_post(body=_('Settlement bill created: %s') % move.name)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Settlement Bill'),
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Settlements'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('insurance_claim_id', '=', self.id), ('move_type', '=', 'in_invoice')],
        }
