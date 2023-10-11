# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from odoo.exceptions import UserError
import logging
import json

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def export_google_contacts(self):
        SCOPES = ['https://www.googleapis.com/auth/contacts']
        conf = self.env['ir.config_parameter'].sudo()
        web_url = conf.get_param('web.base.url')
        aht_google_contact_credentials = conf.get_param('aht_google_contact_credentials')
        aht_google_contact_tokens = conf.get_param('aht_google_contact_tokens')
        creds = None

        if aht_google_contact_credentials in [False, None, '']:
            raise exceptions.MissingError("Credentials Required.")

        if aht_google_contact_tokens not in [False, None, '']:
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

            people = service.people().connections()
            people_list = people.list(resourceName='people/me', pageSize=25,
                                      personFields='phoneNumbers')
            google_contacts = []
            while people_list is not None:
                results = people_list.execute()
                google_contacts = google_contacts + results.get('connections', [])
                people_list = people.list_next(people_list, results)

            for record in self:
                google_resource = [{'resourceName':contact['resourceName'], 'phoneNumber': phone.get('value'),
                                    'etag': contact['etag']} for contact in google_contacts for phone in
                                   contact.get('phoneNumbers', []) if phone.get('value') == record.phone]
                body = {
                    "names": [{
                        "givenName": record.name
                    }],
                    "phoneNumbers": [{
                        'value': record.phone
                    }],
                    "emailAddresses": [{
                        'value': record.email
                    }],
                }
                if record.website:
                    body['urls'] = [{'value': record.website}]
                if record.mobile:
                    body['phoneNumbers'].append({'value': record.mobile})
                if google_resource:
                    for google_contact in google_resource:
                        body['etag'] = google_contact['etag']
                        service.people().updateContact(resourceName=google_contact['resourceName'],
                                                       updatePersonFields='emailAddresses,phoneNumbers,names,urls',
                                                       body=body).execute()
                else:
                    service.people().createContact(body=body).execute()
        except HttpError as e:
            _logger.info("HttpError :: " + str(e.__dict__))
            raise exceptions.ValidationError(e)
        except Exception as e:
            _logger.info("Exception :: " + str(e.__dict__))
            raise exceptions.ValidationError(e)
