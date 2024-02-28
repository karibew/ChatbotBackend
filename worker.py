import pytz
from rq import Queue, Worker
from src.configurations.redisConfig import RedisConfig
from src.configurations.supabaseConfig import SupabaseClient
# from src.configurations.twilioConfig import twilioConfig
from src.configurations.logging import logging
from src.harvest.responder import process_message
from src.harvest.responder import process_live_message
from src.harvest.booking import send_booking_link



db = SupabaseClient()
# twilio = twilioConfig()
rd =RedisConfig().redis


kb_q = Queue("kb_q", connection=rd)
ct_timezone = pytz.timezone("US/Central")


##################################################################
#########    function for inbound/outbound responder    ##########
##################################################################


def inbound_outbound_responder(chat: dict):
    try:
        
        return process_message(chat)
    except Exception as e:
        logging.exception("Exception occurred")


def live_inbound_outbound_responder(sms: dict):
    try:

        return process_live_message(sms)
    except Exception as e:
        logging.exception("Exception occurred")


##################################################################
###############    function for booking link     #################
##################################################################


def booking_link(booking_data: dict):
    try:
        return send_booking_link(booking_data)
    except Exception as e:
        logging.exception("Exception occurred")





if __name__ == "__main__":
    try:
        worker = Worker([kb_q], connection=rd)
        worker.work() 
    except:
        logging.exception("exception occur in worker")     
