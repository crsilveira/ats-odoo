# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Adiciona aba Parcelas em Apolices de Seguro',
    'version': '18.0.1.0.0',
    'category': 'Insurance Management',
    'license': 'AGPL-3',
    'summary': "Opção para criar parcelas em apolices",
    'description': """
        Permite criar parcelas em apolices de seguro,
        informando o número de parcela, dia da parcela, e valor de entrada se necessário,
        e opção para editar as parcelas conforme necessidade.
        Permite colocar forma de pagamento diferenciada para cada parcela.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    "depends": [
        "leapai_insurance_management",
        "account_payment_mode",
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/insurance_installment_views.xml', # Carrega as views filhas primeiro
        # 'views/insurance_payment_views.xml',     # Carrega a view pai de pagamentos
        'views/insurance_policy_views.xml',      # Carrega a extensão da apólice
        # 'views/insurance_menus.xml',             # Carrega os menus por último
    ],
    "installable": True,
    "auto_install": False,
}

