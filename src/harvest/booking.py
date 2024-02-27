from src.configurations.supabaseConfig import SupabaseClient
from src.configurations.zapierConfig import ZapierConfig
from src.configurations.twilioConfig import twilioConfig
from src.configurations.utils import (
    split_sms,
    convert_calendly_time_and_timezone_to_invitee_nl_time,
    add_space_after_url,
    save_message
)
from src.configurations.enums import TypeEnum,BotEnum
import time
from datetime import datetime
import pytz
from src.configurations.logging import logging

db = SupabaseClient()
# zapier = ZapierConfig()
# twilio = twilioConfig()



def send_booking_link(booking_data):
    contact = db.fetch_by_contact_email("contacts", booking_data["contact_email"]).data
    if len(contact) == 0:
        logging.info("no contact in db for email %s" , booking_data["contact_email"])
        return 200

    elif len(contact) > 1:
        logging.info("multiple contacts in db for email %s", booking_data["contact_email"])

    contact = contact[0]
    nl_start_time = convert_calendly_time_and_timezone_to_invitee_nl_time(  booking_data["start_time"], booking_data["lead_timezone"])

    now_utc = datetime.now(pytz.utc).isoformat()
    db.update_by_id( "contacts", {"last_contact_date": now_utc, "status": "booked"}, contact["contactid"])
     
    if contact.get("type") == TypeEnum.Buyer.value:
        response = f"Just saw that you booked a call on {nl_start_time}. In the meantime, feel free to browse our marketplace at https://app.karibew.com/listings/?anonymous=true or place a bid request at https://app.karibew.com/bid_requests/new/specs . Looking forward to our chat!"
    elif contact.get("type") == TypeEnum.Supplier.value:
        response = f"Just saw that you booked a call on {nl_start_time}. In the meantime, feel free to browse what buyers need at https://app.karibew.com/opportunities or place a listing at https://app.karibew.com/supply_posting/new . Looking forward to our chat!"
    else:
        response = f"Just saw that you booked a call on {nl_start_time}. Looking forward to our chat!"
    logging.info("contact type %s", contact["type"])
    logging.info("contact response %s", response)
    sentences = split_sms(add_space_after_url(response))

    for text in sentences:
        logging.info("length of message for BOOKING TEXT %s and lead phone number %s", len(text), contact["contact_phone"])
        if len(text) > 0 and contact['contact_phone'] != 'N/A':  
            try:
                # twilio.send_message(contact["contact_phone"], text)
                # twilio.send_message("+17736206534", "FH OUTBOUND TO " + contact["contact_phone"] + ":\n\n" + text)
                # zapier.save_into_salesforce(text, contact["contactid"], "outbound")
                save_message(
                    text,
                    contact["contactid"],
                    contact["contact_phone"],
                    "+16509556151",
                    "outbound",
                    "confirmation",
                    contact['campaign'],
                )
                time.sleep(7)
            except Exception as e:
                print("error sending message", e)
                return 200

    print(booking_data)
    return 200


