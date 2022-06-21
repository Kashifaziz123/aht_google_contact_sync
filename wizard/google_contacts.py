from __future__ import print_function
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from odoo import models, fields, exceptions, _
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from odoo.exceptions import UserError
import requests
import base64
import json


class GoogleContactsSync(models.TransientModel):
    _name = 'google.contacts.sync'

    name = fields.Char('Name')
    email = fields.Char('Email')
    phone = fields.Char('Phone Number')
    mobile = fields.Char('Mobile Number')
    object = fields.Char('Object')

    # current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)

    def sync_google_contacts(self, kwargs=None):
        SCOPES = ['https://www.googleapis.com/auth/contacts']
        web_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        aht_google_contact_credentials = self.env['ir.config_parameter'].sudo().search([('key', '=', 'aht_google_contact_credentials')]).value
        if not aht_google_contact_credentials or aht_google_contact_credentials == "":
            raise exceptions.MissingError("Credentials Required.")
        creds = None

        aht_google_contact_tokens = self.env['ir.config_parameter'].sudo().get_param('aht_google_contact_tokens')
        if aht_google_contact_tokens and aht_google_contact_tokens != '':
            json_creds = json.loads(aht_google_contact_tokens)
            creds = Credentials.from_authorized_user_info(json_creds, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(json.loads(aht_google_contact_credentials),
                                                           SCOPES, redirect_uri=web_url + "/response")
                auth_url, _ = flow.authorization_url(prompt='consent')
                return {
                    "url": auth_url,
                    "type": "ir.actions.act_url"
                }
        try:
            service = build('people', 'v1', credentials=creds)
            results = service.people().connections().list(
                resourceName='people/me',
                pageSize=10,
                personFields='names,emailAddresses,phoneNumbers,photos,locales,locations,coverPhotos').execute()
            connections = results.get('connections', [])
            contacts = []
            for person in connections:
                # names = person.get('names', [])
                contacts.append(person)
            records = self.env['google.contacts.sync'].search([])
            for record in records:
                record.unlink()
            for contact in contacts:
                object = contact
                name = contact['names'][0]['displayName'] if 'names' in contact else 'N/A'
                email = contact['emailAddresses'][0]['value'] if 'emailAddresses' in contact else 'N/A'
                phone = contact['phoneNumbers'][0]['value'] if 'phoneNumbers' in contact else 'N/A'
                mobile = ''
                if len(contact['phoneNumbers'] > 1):
                    mobile = contact['phoneNumbers'][1]['value'] if 'phoneNumbers' in contact else 'N/A'
                self.create({
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'mobile': mobile,
                    'object': json.dumps(object),
                })
            return {
                'name': "Your contacts",  # Name You want to display on wizard
                'view_mode': 'tree',
                'view_id': self.env.ref('aht_google_contacts.view_contacts_tree').id,
                'res_model': 'google.contacts.sync',  # With . Example sale.order
                'type': 'ir.actions.act_window',
                'target': 'new',
                # 'tag': 'reload',
            }
        except HttpError as err:
            print(err)

    def import_contacts(self):
        res = self.env['res.partner']
        for rec in self:
            contact = self.env['res.partner'].search([('phone', '=', rec.phone)])
            if not contact.id:
                contact.create({
                    'company_type': 'person',
                    'name': rec.name,
                    'email': rec.email,
                    'phone': rec.phone,
                    # 'image_1024': json.loads(rec.object)['photos'][0]['url'],
                    'image_1920': base64.b64encode(requests.get(json.loads(rec.object)['photos'][0]['url']).content),
                })
            else:
                contact.update({
                    'company_type': 'person',
                    'name': rec.name,
                    'email': rec.email,
                    'phone': rec.phone,
                    'image_1920': base64.b64encode(requests.get(json.loads(rec.object)['photos'][0]['url']).content),
                })

    def call_url(self, link):
        return {
            'type': 'ir.actions.act_url',
            'url': link,
            'target': 'new',
        }
