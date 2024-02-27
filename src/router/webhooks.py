import os
from rq import Queue
from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
from src.configurations.logging import logging
from src.configurations.redisConfig import RedisConfig
from src.configurations.zapierConfig import ZapierConfig
from worker import inbound_outbound_responder,booking_link
from src.configurations.utils import (
    modify_number,
    save_message,
    save_contact,
    check_campaign
)

webhook_router = APIRouter(prefix="/v1")
kb_q = Queue("kb_q", connection=RedisConfig().redis)


##################################################################
###########   Webhook for listening inbound messages  ############
##################################################################

@webhook_router.post(
    "/fh_webhook", tags=["webhook"], summary="Webhook for inbound/outbound messages"
)

async def fh_webhook(request: Request):
    form_data = await request.form()
    sms_data = dict(form_data)
    logging.info("INBOUND MESSAGE %s",sms_data)  
    #if sms_data["To"] == os.environ.get("FH_TWILIO_NUMBER"):
    try:
        logging.info("Sms payload: %s", sms_data)
        kb_q.enqueue(inbound_outbound_responder, sms_data)
        return JSONResponse(content={"status": "success", "response": "test"}, status_code=200)
    except Exception as e:
        logging.exception("Exception occurred")
    return JSONResponse(content={"status": "success"}, status_code=200)


##################################################################
###########    Webhook for new booking appointment    ############
##################################################################


@webhook_router.post("/fh_booking", tags=["webhook"], summary="Webhook for booking appointment")
async def new_booking(booking_data: dict):
    logging.info("Booking data payload: %s", booking_data)
    try:
        kb_q.enqueue(booking_link, booking_data)
    except Exception as e:
        logging.exception("Exception occurred")


##################################################################
#######    Webhook for listening new contact insertion    ########
##################################################################


@webhook_router.post(
    "/fh_new_contact", tags=["webhook"], summary="Webhook for new contact"
)
async def new_contact(request:Request):
    data = await request.json()
    logging.info("new contact", data)
    contact_phone = modify_number(str(data.get("phone")))
    data['contact_email'] = data.get('email', None)
    save_contact(data, contact_phone)
    save_message(
        data.get("initial_text", None),
        data.get("contactid", None),
        contact_phone,
        "+16509556151",
        "outbound",
        "initial_text",
        check_campaign(data.get('leadtype', 'unknown'))
    )
    content = data.get("initial_text", "unknown")
    contactid = data.get("contactid", "unknown")
    ZapierConfig().save_into_salesforce(content, contactid, "outbound")
    return {"status": "success", "response": "test"}

