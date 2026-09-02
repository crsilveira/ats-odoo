# -*- coding: utf-8 -*- © 2026 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError

class InsurancePolicy(models.Model):
    _inherit = 'insurance.policy'
   
    parcela_ids = fields.One2many(
        'insurance.installment', 'insurance_policy_id',
        string=u"Parcelas", copy=False)
    num_parcela = fields.Integer('Núm. Parcela')
    dia_vcto = fields.Integer('Dia Vencimento', default=0)
    # vlr_prim_prc = fields.Monetary('Valor Prim. Parcela', default=0.0)
    payment_mode_install_id = fields.Many2one(
        'account.payment.mode', string=u"Modo de pagamento")
    enviar_message = fields.Boolean(string="Enviar Mensagem", default=False)
    tipo_message = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('email', 'E-mail'),
        ('sem_mensagem', 'Sem Mensagem')
    ], string='Tipo de Mensagem', default='sem_mensagem')

    def action_confirma_parcela(self):
        valor_total = 0
        for prc in self.parcela_ids:
            valor_total += prc.valor
        if round(self.premium_amount, 2) != round(valor_total, 2):
            raise UserError(_(f"Valor da soma das parcelas: {str(valor_total)}, diferente do valor total: {str(self.premium_amount)}.")) 
        if self.num_parcela > 0:
            date_due = False
            parcelas = []
            for prc in self.parcela_ids:
                # a data de vencimento da fatura sera o ultimo vencimento
                date_due = prc.data_vencimento
            if date_due:
                self.update({'invoice_date_due': date_due})
            sign = 1                
            for prc in self.parcela_ids:
                for line in self.line_ids:
                    if line.account_type in ('asset_receivable', 'liability_payable'):
                        sign = 1 if line.balance > 0.0 else -1
                        conta_lancamento = line.account_id
                        line.with_context(check_move_validity=False, dynamic_unlink=True).unlink()
            #     create_method = {
            #             'name': prc.numero_fatura,
            #             'debit': valor_deb if valor_deb else 0.0,
            #             'credit': -valor_cre if valor_cre else 0.0,
            #             'balance': valor_deb if valor_deb else -valor_cre,
            #             'quantity': 1.0,
            #             'amount_currency': sign * prc.valor,
            #             'date_maturity': prc.data_vencimento,
            #             'move_id': self.id,
            #             'currency_id': self.currency_id.id,
            #             'account_id': conta_lancamento.id,
            #             'partner_id': self.commercial_partner_id.id,
            #             'payment_mode_id': prc.payment_mode_id.id or self.payment_mode_id.id or False,
            #     }
            #     parcelas.append(create_method)
            # self.env['account.move.line'].with_context(check_move_validity=False,dynamic_unlink=True).create(parcelas)
   
    def calcular_vencimento(self, dia_preferencia, parcela):
        dt = self.issue_date
        dia = dt.day
        # calcula a data de vencimento  
        if dia_preferencia:
            if dia >= dia_preferencia:
                parcela += 1
            dia = dia_preferencia
        else:
            parcela += 1
        year = divmod(dt.month+parcela - 1, 12)[0] + dt.year
        next_month = (dt.month + parcela) % 12 or 12
        if next_month == 2 and dia > 28:
            dia = 28
        if dia == 31 and next_month not in (1,3,5,7,8,10,12):
            dia = 30
        data_vcto = datetime(year, next_month, dia)
        return data_vcto

    @api.depends('num_parcela', 'dia_vcto')
    def action_calcula_parcela(self):
        prcs = []       
        prc = 0
        total = self.premium_amount
        valor_prc = 0.0
        # if self.vlr_prim_prc:
        #     total = self.currency_id.round(total - self.vlr_prim_prc)
        #     if self.num_parcela > 1:
        #         valor_prc = self.currency_id.round(total / (self.num_parcela - 1))
        #     else:
        #         if self.num_parcela > 1:
        #             valor_prc = self.currency_id.round(total / (self.num_parcela - 1))
        #         else:
        #             valor_prc = self.currency_id.round(total)
        # else:
        if self.num_parcela > 0:
            valor_prc = self.currency_id.round(total / self.num_parcela)
        else:
            valor_prc = self.currency_id.round(total)
        valor_parc = valor_prc
        while (prc < self.num_parcela):
            data_parc = self.calcular_vencimento(self.dia_vcto,prc)
            # if prc == 0 and self.vlr_prim_prc > 0.0:
            #     valor_parc = self.currency_id.round(self.vlr_prim_prc)
            # if prc == 0 and self.vlr_prim_prc == 0.0:
            total -= valor_parc
            if (self.num_parcela - prc) == 1:
                if total > 0.0 or total < 0.0:
                    valor_parc = self.currency_id.round(valor_parc + total)
            prcs.append((0, None, {
                'data_vencimento': data_parc,
                'valor': self.currency_id.round(valor_parc),
                'name': str(prc+1).zfill(2),
                'payment_mode_id': self.payment_mode_install_id.id,
                'insurance_policy_id': self.id,
                'currency_id': self.currency_id.id
            }))
            valor_parc = valor_prc
            prc += 1
        if prcs:
            if self.parcela_ids:
                self.parcela_ids.unlink()
            self.parcela_ids = prcs


class InsuranceInstallment(models.Model):
    _name = 'insurance.installment'
    _order = 'data_vencimento'
    _description = "Parcelas do pagamento"

    name = fields.Char(string="Descrição") 
    insurance_policy_id = fields.Many2one("insurance.policy", string="Apólice" )
    # data_apolice = fields.Date(string="Data Apólice", related="payment_id.insurance_policy_id.issue_date")
    data_vencimento = fields.Date(string="Data Vencimento")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    valor = fields.Monetary(string="Valor Parcela")
    payment_mode_id = fields.Many2one(
       'account.payment.mode', string=u"Modo de pagamento")
    enviado_message = fields.Boolean(string="Mensagem Enviada", default=False)
    messag_date_send = fields.Datetime(string="Data Envio Mensagem", compute="_compute_date_send", store=True)
    tipo_message = fields.Selection(related='insurance_policy_id.tipo_message', string='Tipo de Mensagem')
    parcela_paga = fields.Boolean(string="Parcela Paga", default=False)
   
    @api.depends('enviado_message')
    def _compute_date_send(self):
        for record in self:
            if record.enviado_message:
                record.messag_date_send = datetime.now()
            else:
                record.messag_date_send = False
