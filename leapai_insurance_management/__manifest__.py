{
    'name': 'Insurance Management',
    'version': '18.0.1.0.0',
    'category': 'Insurance',
    'summary': 'Manage insurance policies, claims, agents, and nominees',
    'description': """
Insurance Management
====================
A comprehensive insurance management module for Odoo 19.

Features:
- Insurance Categories & Sub-categories
- Policy Management with full lifecycle
- Claim Management with approval workflow
- Agent Management with commission tracking
- Nominee Management
- Document Tracking
- Accounting Integration (Invoices & Settlements)
- PDF Reports for Policies and Claims
    """,
    'author': 'leapai.ai',
    'website': 'https://leapai.ai',
    'license': 'LGPL-3',
    'images': [
        'static/description/banner.png',
        'static/description/screenshot_01_policies_list.png',
        'static/description/screenshot_02_policy_form.png',
        'static/description/screenshot_03_claims_list.png',
        'static/description/screenshot_04_claim_form.png',
    ],
    'depends': ['base', 'mail', 'account', 'hr'],
    'data': [
        'security/insurance_security.xml',
        'security/ir.model.access.csv',
        'data/insurance_sequence.xml',
        'views/insurance_category_views.xml',
        'views/insurance_term_views.xml',
        'views/insurance_agent_views.xml',
        'views/insurance_policy_views.xml',
        'views/insurance_claim_views.xml',
        'views/res_partner_views.xml',
        'views/insurance_menu.xml',
        'report/insurance_policy_report.xml',
        'report/insurance_policy_report_template.xml',
        'report/insurance_claim_report.xml',
        'report/insurance_claim_report_template.xml',
    ],
    'demo': [
        'data/insurance_demo_data.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
