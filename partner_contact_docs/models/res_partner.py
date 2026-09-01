# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # contatonome = fields.Char(string='Contato Emergência')
    # contatofone = fields.Char(string='Telefone Emergência')
    # birthdate_date = fields.Date('Data de Nascimento')
    # firstname = fields.Char(string='Prim. Nome')
    rg_emissao = fields.Date(string='Data Emissao RG')
    rg_orgao = fields.Char(string='Orgão emissor (RG)', size=30)
    cnh = fields.Char(string='CNH', size=30)
    cnh_emissao = fields.Date(string='Data Emissao CNH')
    cnh_primhabilita = fields.Date(string='Data Prim. Habilitação')
    cnh_vcto = fields.Date(string='Data Vencimento CNH')
    # revised = fields.Boolean(string='Revisado')
    estado_civil = fields.Selection([
        ('cel','Solteiro'),
        ('maried','Casado'),
        ('pacs', 'União Civil'),
        ('divorced','Divorciado'), 
        ('viuvo', 'Viúvo')], 'Estado Civil'
    )
