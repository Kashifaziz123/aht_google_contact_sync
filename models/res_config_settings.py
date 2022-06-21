# -*- coding: utf-8 -*-

from odoo import api, fields, models
import os.path


class GeneralSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "credentials for google contacts API"

    aht_google_contact_credentials = fields.Char('Credentials')

    def get_values(self):
        res = super(GeneralSettings, self).get_values()
        aht_google_contact_credentials = self.env["ir.config_parameter"].get_param("aht_google_contact_credentials", default=None)
        res.update(
            aht_google_contact_credentials=aht_google_contact_credentials or False,
        )
        return res

    def set_values(self):
        super(GeneralSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].set_param("aht_google_contact_credentials", record.aht_google_contact_credentials or '')
            self.env['ir.config_parameter'].set_param('aht_google_contact_tokens', '')

