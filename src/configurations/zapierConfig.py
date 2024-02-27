from datetime import datetime
import requests
import pytz
from src.configurations.enums import URLs
from src.configurations.logging import logging


class ZapierConfig():

    def save_into_salesforce(self,message_data,contactid, direction):
        try:
            url = URLs.ZAPIER_URL.value
            now_utc = datetime.now(pytz.utc)
            central_time = now_utc.astimezone(pytz.timezone('US/Central'))
            formatted_central_time = central_time.strftime("%Y/%m/%d %H:%M:%S")

            payload = {
                'content': message_data,
                'time': formatted_central_time,
                'direction': direction,
                'contactid': contactid
            }
            requests.post(url, data = payload)
        except Exception as e:
            logging.exception("Error in saving into salesforce %s", contactid)

    def save_contact_into_database_using_email(self,email):
        try:
            url = URLs.ZAPIER_CONTACT_SAVE_WEBHOOK.value
            payload = {'email': email}
            requests.post(url, data = payload)
        except Exception as e:
            logging.exception("Error in saving into salesforce %s", email)        


           
