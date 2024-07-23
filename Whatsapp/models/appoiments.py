from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    partner_phones = fields.Text(string="Partner Phones", compute="_compute_partner_phones")
    start_minus_3_hours = fields.Datetime(string="Start Minus 3 Hours", compute="_compute_start_times")
    start_minus_1_day = fields.Datetime(string="Start Minus 1 Day", compute="_compute_start_times")

    @api.depends('start')
    def _compute_start_times(self):
        for record in self:
            if record.start:
                record.start_minus_3_hours = record.start - timedelta(hours=3)
                record.start_minus_1_day = record.start - timedelta(days=1)
            else:
                record.start_minus_3_hours = False
                record.start_minus_1_day = False


    @api.depends('partner_ids')
    def _compute_partner_phones(self):
        for record in self:
            phones = record.partner_ids.mapped('phone')
            if phones:
                record.partner_phones = '\n'.join(phone for phone in phones if phone)
            else:
                record.partner_phones = ''

    def action_send_whatsapp_message(self):
        # Enviar mensaje a todos los números de teléfono en `partner_phones`
        for record in self:
            partner_phones = record.partner_phones.split('\n')
            for phone in partner_phones:
                phone = phone.strip()
                if phone:
                    self._send_whatsapp_message(phone)

    def _send_whatsapp_message(self, phone):
        url = 'https://graph.facebook.com/v20.0/318264768046374/messages'
        headers = {
            'Authorization': 'Bearer EAAawtkadohMBOZBTZAdAbkDafcmLK8qeKoxsumSaKVgxecgZAWsBAkuecaR64dXaX0F83g2GJ8sbDZAMavWK4PM56ZA7SWukAZCmL2OUZBa5W0fJ9Oo8sFO7gDvq2io7slZBAcA9ZCbWZALicOxjXxrzX7FPXJ55SpZCY1DONpOK3xBleEeEX8CbAeoyql9ontJn8R7fA4vpBC8Lo7RQnSbQs8ZD',
            'Content-Type': 'application/json',
        }
        data = {
            "messaging_product": "whatsapp",
            "to": phone,  # Número del destinatario
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Mensaje enviado exitosamente
            logging.info(f'Message sent successfully to {phone}.')
        else:
            # Registra la respuesta o lanza un error
            logging.error(f'Failed to send message to {phone}. Response: {response.text}')
            raise UserError(f'Failed to send message to {phone}. Response: {response.text}')
