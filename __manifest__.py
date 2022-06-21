# -*- coding: utf-8 -*-
{
    'name': "aht_google_contacts",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/google_contacts.xml',
        'views/res_config_settings_view_form_inherit.xml',
        'wizard/google_contacts_export.xml',
    ],
}
