# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from odoo.exceptions import UserError
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def export_google_contacts(self):
        SCOPES = ['https://www.googleapis.com/auth/contacts']
        web_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        aht_google_contact_credentials = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aht_google_contact_credentials')]).value
        if not aht_google_contact_credentials or aht_google_contact_credentials == "":
            raise exceptions.MissingError("Credentials Required.")
        creds = None

        aht_google_contact_tokens = self.env['ir.config_parameter'].sudo().get_param('aht_google_contact_tokens')
        if aht_google_contact_tokens and aht_google_contact_tokens != '':
            creds = json.loads(aht_google_contact_tokens)
            creds = Credentials.from_authorized_user_info(creds, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(json.loads(aht_google_contact_credentials),
                                                           SCOPES, redirect_uri=web_url + '/response')
                auth_url, _ = flow.authorization_url(prompt='consent')
                return {
                    "url": auth_url,
                    "type": "ir.actions.act_url"
                }

        try:
            service = build('people', 'v1', credentials=creds)
            results = service.people().connections().list(
                resourceName='people/me',
                pageSize=100,
                personFields='names,emailAddresses,phoneNumbers,photos').execute()
            connections = results.get('connections', [])
            activeContacts = self.env['res.partner'].search([('id', '=', self._context['active_ids'])])
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            for contact in activeContacts:
                phone = contact.phone
                contactFound = 0
                for person in connections:
                    if 'emailAddresses' in person:
                        if person['phoneNumbers'][0]['value'] == phone:
                            body = {
                                'etag': person['etag'],
                                "names": [
                                    {
                                        "givenName": contact.name
                                    }
                                ],
                                "phoneNumbers": [],
                                "emailAddresses": [
                                    {
                                        'value': contact.email
                                    }
                                ],
                                "photos": [],
                            }
                            if contact.phone:
                                body['phoneNumbers'].append({'value': contact.phone})
                            if contact.mobile:
                                body['phoneNumbers'].append({'value': contact.mobile})
                            service.people().updateContact(resourceName=person['resourceName'],
                                                           updatePersonFields='emailAddresses,phoneNumbers,names',
                                                           body=body).execute()

                if contactFound == 0:
                    body = {
                        "names": [
                            {
                                "givenName": contact.name
                            }
                        ],
                        "phoneNumbers": [],
                        "emailAddresses": [
                            {
                                'value': contact.email
                            }
                        ],
                        "photos": [],
                    }
                    if contact.phone:
                        body['phoneNumbers'].append({'value': contact.phone})
                    if contact.mobile:
                        body['phoneNumbers'].append({'value': contact.mobile})
                    # if contact.image_1920:
                    #     body['photos'].append({'url': base_url + "/web/image?model=res.partner&id=" + str(contact.id) + "&field=image_1920"})
                service.people().createContact(body=body).execute()
        except HttpError as err:
            print(err)
