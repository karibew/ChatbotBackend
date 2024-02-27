import os
import logging
from twilio.rest import Client
from src.configurations.logging import logging 
from src.configurations.supabaseConfig  import retry


class twilioConfig:
    def __init__(self):
        account_sid = os.environ.get("FH_TWILIO_SID")
        auth_token = os.environ.get("FH_TWILIO_AUTH_TOKEN")
        self.client = Client(account_sid, auth_token)

    @retry(max_attempts=3, delay=2)
    def send_message(self, to_number, message):
        return  self.client.messages.create(
        body=message,
        from_= os.environ.get("FH_TWILIO_NUMBER"),
        to=to_number
        )
  
        

