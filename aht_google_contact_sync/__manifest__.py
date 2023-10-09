# -*- coding: utf-8 -*-
{
    'name': "Google Contacts Sync",
    'summary': """
        Google Contacts import and export. 
        """,
    'description': """
        This application facilitates users and managers to synchronize their Google account related contacts with Odoo. Users can import and export contacts between Google contacts and Odoo. Synchronization facilitates users to keep their Google contacts updated in their Odoo account.
    """,
    'author': "Alhaditech",
    'license': 'AGPL-3',
    'website': "https://www.alhaditech.com/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'contacts'],
    'price': 65, 'currency': 'USD',
    'images': ['static/description/google-contacts-logo.jpg'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/google_contacts.xml',
        'views/res_config_settings_view_form_inherit.xml',
        'wizard/google_contacts_export.xml',
    ],
}
