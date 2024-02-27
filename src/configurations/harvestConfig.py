
import requests
from src.configurations.enums import URLs
from src.configurations.logging import logging


class Harvest():

    def get_priority_listing_activity(start_date,end_date):
        try:
            url = URLs.HARVEST_API_URL.value
            params = {'start_date':start_date, 'end_date' :end_date}
            headers = {'Content-Type':'application/json'}
            response = requests.get(url,headers=headers, params = params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logging.exception("Getting error while calling harvest api %s")
           