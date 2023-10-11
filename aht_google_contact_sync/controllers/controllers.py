from __future__ import print_function
from odoo import http
from google_auth_oauthlib.flow import Flow
from odoo.http import request
import werkzeug
import json


class GoogleContactsApiAccess(http.Controller):
    @http.route('/response', auth='public')
    def get_response(self, **kwargs):
        try:
            if kwargs.get('state') and kwargs.get('code') and kwargs.get('scope'):
                config = request.env['ir.config_parameter'].sudo()
                SCOPES = ['https://www.googleapis.com/auth/contacts']
                web_url = config.get_param('web.base.url')
                aht_google_contact_credentials = config.get_param('aht_google_contact_credentials')

                flow = Flow.from_client_config(json.loads(aht_google_contact_credentials), SCOPES,
                                               redirect_uri=web_url + "/response")
                url = (web_url + "/response").replace('http', 'https')
                url += "?state=" + str(kwargs["state"])
                url += "&code=" + str(kwargs["code"])
                url += "&scope=" + str(kwargs["scope"]).replace('/', '%2F').replace(':', '%3A')
                try:
                    flow.fetch_token(authorization_response=url)
                except Exception as e:
                    return ("<div><h3 style='display: flex;justify-content: center;align-items: center;height:80vh;'>"
                            "<div><b>Google Server Error</b><br/>Authorize again</h3></div></div>")
                token = flow.credentials
                config.set_param('aht_google_contact_tokens', token.to_json())
                return werkzeug.utils.redirect('/web/')
            else:
                return ("<div><h3 style='display: flex;justify-content: center;align-items: center;height:80vh;'>"
                        "<b>Not a valid google response</b></h3></div>")
        except Exception as e:
            if 'Google Server Error</b><br/>Authorize again' in e:
                return e
            return ("<div><h3 style='display: flex;justify-content: center;align-items: center;height:80vh;'>"
                    "<b>Internal Server Error</b></h3></div>")
