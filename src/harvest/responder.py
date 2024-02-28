from src.configurations.supabaseConfig import SupabaseClient
# from src.configurations.zapierConfig import ZapierConfig
from src.configurations.openaiConfig import OpenAiConfig
# from src.configurations.twilioConfig import twilioConfig
from src.configurations.logging import logging
from src.configurations.redisConfig import RedisConfig
from src.configurations.utils import (
    split_sms,
    add_space_after_url,
    modify_number,
    save_message,
    prepare_ai_message_history,
)
from datetime import datetime
from rq import Queue
import pytz
import time


rd = RedisConfig().redis
kb_q = Queue("kb_q", connection=rd)

db = SupabaseClient()
# zapier = ZapierConfig()
# twilio = twilioConfig()



def process_message(sms_data):
    contact_phone = modify_number(sms_data.get("From"))
    try:
        contact_info = db.fetch_by_contact_phone("contacts", contact_phone).data[0]
        contact_id = contact_info["contactid"]
        if contact_info.get("gepeto_switch") == False:
            return 200
    except:
        logging.info("Contact not found in database %s", contact_phone)
        return 200

    # SAVE INBOUND MESSAGE INTO HARVEST DATABASE
    save_message(
        sms_data.get("Body"),
        contact_id,
        contact_phone,
        sms_data.get("To"),
        "inbound",
        "inquiry",
        contact_info.get("campaign"),
    )

    # SAVE INBOUND MESSAGE TO SALE FORCE CRM AGAINST CONTACT ID
    #zapier.save_into_salesforce(sms_data.get("Body"), contact_id, "inbound")

    # VALIDATION ON INBOUND MESSAGE 

    if (
        sms_data.get("Body").lower() == "stop"
        or sms_data.get("Body").lower() == "unsubscribe"
    ):
        db.update_by_org_id_and_id(
            "contacts", {"followup_count": "X"}, "karibew", contact_id
        )
        logging.info("X on followups for contact_id %s", contact_id)
        logging.info("X on followups for contact_phone %s", contact_phone)
        return 200

    # IMPLEMENT CHILL BRO
    for job in kb_q.jobs:
        logging.info("Job ID: %s, Status: %s", job.id, job.get_status())
        payload = job.args[0]
        if job.func_name == "worker.inbound_outbound_responder" and payload.get(
            "From", "none"
        ) == sms_data.get("From"):
            logging.info("already in queue")
            return 200

    

    now_utc = datetime.now(pytz.utc).isoformat()
    db.update_by_id("contacts", {"last_contact_date": now_utc}, contact_id)

    message_history = db.fetch_all_messages_by_campaign(
        "messages", contact_id, contact_info.get("campaign")
    ).data
    logging.info(
        "contact_id >> %s << with campaign >> %s << having messages >> %s << in database",
        contact_id,
        contact_info.get("campaign"),
        len(message_history),
    )
    ai_message_history = prepare_ai_message_history(
        message_history, sms_data.get("Body"), contact_info
    )

    response = None
    try:
        (
            response,
            prompt_tokens,
            completion_tokens,
            model,
        ) = OpenAiConfig().generate_response(ai_message_history, "gpt-4")
        logging.info("ai generated response %s", response)
        logging.info("prompt_tokens %s", prompt_tokens)
        logging.info("completion_tokens %s", completion_tokens)
        logging.info("model %s", model)
    except Exception as e:
        print(e)
        time.sleep(5)

    responses = split_sms(add_space_after_url(response))

    for message in responses:
        logging.info(
            "length of message for RESPONDER %s and lead phone number %s",
            len(message),
            contact_phone,
        )
        if len(message) > 0 and contact_phone != "N/A":
            try:
                # twilio.send_message(contact_phone, message)

                # SAVE OUTBOUND MESSAGE TO SALE FORCE CRM AGAINST CONTACT ID
                # zapier.save_into_salesforce(message, contact_id, "outbound")

                # SAVE OUTBOUND MESSAGE INTO HARVEST DATABASE
                save_message(
                    message,
                    contact_id,
                    contact_phone,
                    sms_data.get("To", None),
                    "outbound",
                    "response",
                    contact_info.get("campaign"),
                    model,
                    prompt_tokens,
                    completion_tokens,
                )
                time.sleep(7)
            except Exception as e:
                print("error sending message", e)
                return 200

    return {"message": "healthy"}  # Return a standard response

def process_live_message(chat_data):

    # SAVE INBOUND MESSAGE INTO HARVEST DATABASE
    save_message(
        chat_data.get("Body"),
        '',
        '',
        chat_data.get("To"),
        "inbound",
        "inquiry",
        'live_chat',
    )

    # SAVE INBOUND MESSAGE TO SALE FORCE CRM AGAINST CONTACT ID
    # zapier.save_into_salesforce(sms_data.get("Body"), contact_id, "inbound")

    # VALIDATION ON INBOUND MESSAGE

    if (
            chat_data.get("Body").lower() == "stop"
            or chat_data.get("Body").lower() == "unsubscribe"
    ):
        db.update_by_org_id_and_id(
            "contacts", {"followup_count": "X"}, "karibew", 'unknown'
        )
        logging.info("X on followups for contact_id %s", 'unknown')
        logging.info("X on followups for contact_phone %s", 'unknown')
        return 200

    # IMPLEMENT CHILL BRO
    for job in kb_q.jobs:
        logging.info("Job ID: %s, Status: %s", job.id, job.get_status())
        payload = job.args[0]
        if job.func_name == "worker.inbound_outbound_responder" and payload.get(
                "From", "none"
        ) == chat_data.get("From"):
            logging.info("already in queue")
            return 200

    now_utc = datetime.now(pytz.utc).isoformat()
    db.update_by_id("contacts", {"last_contact_date": now_utc}, 'unknown')

    message_history = db.fetch_all_messages_by_campaign(
        "messages", 'unknown', 'live_chat'
    ).data
    logging.info(
        "contact_id >> %s << with campaign >> %s << having messages >> %s << in database",
        'unknown',
        'live_chat',
        len(message_history),
    )
    ai_message_history = prepare_ai_message_history(
        message_history, chat_data.get("Body"), 'unknown'
    )

    response = None
    try:
        (
            response,
            prompt_tokens,
            completion_tokens,
            model,
        ) = OpenAiConfig().generate_response(ai_message_history, "gpt-4")
        logging.info("ai generated response %s", response)
        logging.info("prompt_tokens %s", prompt_tokens)
        logging.info("completion_tokens %s", completion_tokens)
        logging.info("model %s", model)
    except Exception as e:
        print(e)
        time.sleep(5)

    responses = split_sms(add_space_after_url(response))

    for message in responses:
        logging.info(
            "length of message for RESPONDER %s and lead phone number %s",
            len(message),
            'unknown',
        )
        if len(message) > 0 and 'unknown' != "N/A":
            try:
                # twilio.send_message(contact_phone, message)

                # SAVE OUTBOUND MESSAGE TO SALE FORCE CRM AGAINST CONTACT ID
                # zapier.save_into_salesforce(message, contact_id, "outbound")

                # SAVE OUTBOUND MESSAGE INTO HARVEST DATABASE
                save_message(
                    message,
                    'unknown',
                    'unknown',
                    'unknown',
                    "outbound",
                    "response",
                    'live_chat',
                    model,
                    prompt_tokens,
                    completion_tokens,
                )
                time.sleep(7)
            except Exception as e:
                print("error sending message", e)
                return 200

    return {"message": response}  # Return a standard response
