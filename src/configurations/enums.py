from enum import Enum
import os

from dotenv import load_dotenv
load_dotenv()


class URLs(str, Enum):
    BUYER_BOOKING_URL = 'https://calendly.com/justin-munro1/30min'
    SUPPLIER_BOOKING_URL = 'https://calendly.com/stefaun-avakian/30min'
    SEARCH_PRODUCE_LINK = "https://app.karibew.com/listings/?anonymous=true"
    BID_REQUEST_LINK = 'https://app.karibew.com/bid_requests/new/specs'
    ZAPIER_URL =os.environ.get("ZAPIER_URL")
    ZAPIER_CONTACT_SAVE_WEBHOOK=os.environ.get("ZAPIER_CONTACT_SAVE_WEBHOOK")
    HARVEST_API_URL='http://app.karibew.com/api/supply_postings/priority_listing_activity'


class TypeEnum(str, Enum):
    Supplier = 'Supplier'
    Buyer = 'Buyer'
    OutBound = 'OutBound'


class BotEnum(str, Enum):
    outbound_Joe = 'outbound_Joe'
    Joe_supplier = 'Joe_supplier'
    Joe_buyer = 'Joe'


