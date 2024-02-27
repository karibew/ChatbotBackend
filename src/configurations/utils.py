import re
import json
import random
import hashlib
import pytz
from src.configurations.enums import URLs
from datetime import datetime
from src.configurations.redisConfig import RedisConfig
from src.configurations.supabaseConfig import SupabaseClient
from src.configurations.openaiConfig import  find_txt_examples
from src.configurations.logging import logging
from src.configurations.enums import TypeEnum, BotEnum

db = SupabaseClient()

ct_timezone = pytz.timezone("US/Central")


def generate_unique_id(phone_number, timestamp, message):
    unique_string = f"{phone_number}-{timestamp}-{message}"
    return hashlib.md5(unique_string.encode("utf-8")).hexdigest()


def its_already_processed(message_data):
    request_id = generate_unique_id(str(message_data))
    rd = RedisConfig().redis
    if rd.exists(f"request:{request_id}"):
        print("already processed")
        return True
    else:
        rd.set(f"request:{request_id}", 1, ex=10800)  # expires after 3 hours
        return False


def split_sms(message):
    # Use regular expressions to split the string at ., !, or ? followed by a space or newline
    sentences = re.split("(?<=[.!?]) (?=\\S)|(?<=[.!?])\n", message.strip())
    # Strip leading and trailing whitespace from each sentence
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Compute the total length of all sentences
    total_length = sum(len(sentence) for sentence in sentences)

    # Split the sentences into two parts such that the difference in their total lengths is minimized
    part1 = []
    part2 = []
    part1_length = 0
    i = 0
    while i < len(sentences) and part1_length + len(sentences[i]) <= total_length / 2:
        part1.append(sentences[i])
        part1_length += len(sentences[i])
        i += 1

    part2 = sentences[i:]
    if len(part1) == 0:
        strings = [" ".join(part2)]
    else:
        # half the time, include both parts in two strings
        if random.random() < 0.5:
            strings = [" ".join(part1), " ".join(part2)]
        else:
            # add both part1 and part2 into one string
            strings = [" ".join(part1 + part2)]

    return strings


def add_space_after_url(s):
    words = s.split()
    for i, word in enumerate(words):
        if word.startswith("http://") or word.startswith("https://"):
            if word[-1] in ".,!?;:":
                words[i] = word[:-1] + " " + word[-1] + " "
            else:
                words[i] = word + " "
    return " ".join(words)


def convert_calendly_time_and_timezone_to_invitee_nl_time(start_time, invitee_timezone):
    dt_utc = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    local_zone = pytz.timezone(invitee_timezone)
    dt_local = dt_utc.astimezone(local_zone)
    formatted_time = dt_local.strftime("%A, %B %d")

    if formatted_time[-1] == "1":
        formatted_time += "st,"
    elif formatted_time[-1] == "2":
        formatted_time += "nd,"
    elif formatted_time[-1] == "3":
        formatted_time += "rd,"
    else:
        formatted_time += "th,"
    formatted_time += " at " + dt_local.strftime("%I:%M %p %Z")
    return formatted_time


def modify_number(number: str):
    try:
        if number is not None:
            if "ext" in number:
                number_str = number.split(" ext")[0]
            number_str = re.sub(r"[^0-9]", "", number)
            if not number_str.startswith("+"):
                if not number_str.startswith("1"):
                    number_str = "1" + number_str
                number_str = "+" + number_str
            return number_str
        return "N/A"
    except Exception as e:
        logging.info("Exception occurred <<modify_number>>", exc_info=True)


def save_message(
    body,
    contactid,
    contact_phone,
    org_phone,
    direction,
    type,
    campaign,
    model=None,
    prompt_tokens=0,
    completion_tokens=0,
):
    message = {
        "contactid": contactid,
        "body": body,
        "org_phone": org_phone,
        "contact_phone": contact_phone,
        "direction": direction,
        "type": type,
        "model": model,
        "campaign": campaign,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }
    try:
        return db.insert("messages", message)
    except Exception as e:
        logging.exception("Exception occurred while saving message %s", contact_phone)


def get_bot_name_and_booking_link(contact_info):
    bot = db.get_prompt(contact_info.get("campaign")).data[0]
    if bot.get("id") == BotEnum.Joe_buyer.value:
        bot_name = bot.get("id")
        booking_link = URLs.BUYER_BOOKING_URL.value
    if bot.get("id") == BotEnum.Joe_supplier.value:
        bot_name = bot.get("id")
        booking_link = URLs.SUPPLIER_BOOKING_URL.value
    return bot_name, booking_link


def save_contact(data, contact_phone):
    contact = {
        "contactid": data.get("contactid", "none"),
        "firstname": data.get("firstname", "unknown"),
        "lastname": data.get("lastname", "unknown"),
        "companyname": data.get("companyname", "unknown"),
        "status": data.get("status", "unknown"),
        "type": data.get("leadtype", "unknown"),
        "commodities": data.get("commodities", "unknown"),
        "growing_method": data.get("growing_method", "unknown"),
        "need_availability": data.get("need_availability", "unknown"),
        "contact_phone": contact_phone,
        "contact_email": data.get("contact_email", "unknown"),
        "campaign": check_campaign(data.get("leadtype", "unknown")),
        "custom_data": data.get("custom_data", {}),
        "account_executive": data.get("account_executive", None),
    }
    try:
        return db.insert("contacts", contact)
    except Exception as e:
        logging.exception("Exception occurred while saving contact")


def check_campaign(leadtype):
    campaign = BotEnum.Joe_buyer.value
    if leadtype == TypeEnum.Supplier.value:
        campaign = BotEnum.Joe_supplier.value
    if leadtype == TypeEnum.OutBound.value:
        campaign = BotEnum.outbound_Joe.value
    return campaign


def transform_messages(raw_messages):
    ai_messages = []
    for raw_message in raw_messages:
        ai_message = {}
        if raw_message["direction"] == "outbound":
            ai_message["role"] = "assistant"
        else:
            ai_message["role"] = "user"
        ai_message["content"] = raw_message["body"]
        ai_messages.append(ai_message)
    return ai_messages


def prepare_ai_message_history(message_history, message_data, contact_info):
    ai_message_history = transform_messages(message_history)
    bot_name, booking_link = get_bot_name_and_booking_link(contact_info)
    prompt = db.get_prompt(bot_name).data[0]["prompt"]
    examples = find_txt_examples(message_data)
    if examples:
        prompt = prompt + "\n\n" + examples
    if bot_name == "outbound_Joe":
        variables = json.loads(contact_info["custom_data"])
    else:
        variables = {
            "name": "Joe",
            "lead_first_name": contact_info["firstname"],
            "buyer_or_supplier": contact_info["type"],
            "buyer_company_name": contact_info["companyname"],
            "booking_link": booking_link,
            "selected_commodities": str(contact_info["commodities"]),
            "growing_method": contact_info["growing_method"],
            "need_availability": contact_info["need_availability"],
            "bid_request_link": URLs.BID_REQUEST_LINK.value,
            "search_produce_link": URLs.SEARCH_PRODUCE_LINK.value,
        }
    logging.info("system prompt for >>>>>>>>>>>> %s ", contact_info["contact_phone"])
    logging.info("bot name is >>>>>>>>>>>> %s ", bot_name)
    prompt = prompt.format(**variables)
    prompt = {"role": "system", "content": prompt}
    ai_message_history.insert(0, prompt)
    return ai_message_history
