from __future__ import print_function
from odoo import http
from google_auth_oauthlib.flow import Flow
from odoo.http import request
import json


class GoogleContactsApiAccess(http.Controller):
    @http.route('/response', auth='public')
    def get_response(self, **kwargs):
        try:
            web_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

            aht_google_contact_credentials = request.env['ir.config_parameter'].sudo().search(
                [('key', '=', 'aht_google_contact_credentials')]).value
            SCOPES = ['https://www.googleapis.com/auth/contacts']
            flow = Flow.from_client_config(json.loads(aht_google_contact_credentials),
                                           SCOPES, redirect_uri=web_url + "/response")
            url = (web_url + "/response").replace('http', 'https') if 'https' not in web_url else web_url
            url += "?state=" + str(kwargs["state"])
            url += "&code=" + str(kwargs["code"])
            url += "&scope=" + str(kwargs["scope"]).replace('/', '%2F').replace(':', '%3A')

            flow.fetch_token(authorization_response=url)
            token = flow.credentials
            request.env['ir.config_parameter'].sudo().set_param('aht_google_contact_tokens', token.to_json())
            return 'OK'
        except Exception as e:
            return "Error, start the authentication process again."
