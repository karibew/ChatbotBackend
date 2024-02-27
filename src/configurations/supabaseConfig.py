# supabase_client.py
from supabase import create_client
import os
import time
from src.configurations.logging import logging
import functools


def retry(max_attempts, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < max_attempts:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    logging.exception(f"Exception occurred. Retrying... {e}")
                    retries += 1
                    logging.info(f"Exception occurred. Retrying <{func.__name__}>")
                    time.sleep(delay)
            pass
        return wrapper
    return decorator


class SupabaseClient:
    def __init__(self):
        url: str = os.environ.get("FH_SUPABASE_URL")
        key: str = os.environ.get("FH_SUPABASE_KEY")
        self.db = create_client(url, key)

    @retry(max_attempts=5, delay=2)
    def insert(self, table_name: str, row: dict):
        return self.db.table(table_name).insert([row]).execute()

    @retry(max_attempts=5, delay=2)
    def fetch(self, table_name):
        return self.db.table(table_name).select("*").execute()

    @retry(max_attempts=5, delay=2)
    def fetch_by_id(self, table_name, id):
        return self.db.table(table_name).select("*").eq("contactid", id).execute()

    @retry(max_attempts=5, delay=2)
    def fetch_by_contact_phone(self, table_name, contact_phone):
        return (
            self.db.table(table_name)
            .select("*")
            .eq("contact_phone", contact_phone)
            .execute()
        )

    @retry(max_attempts=5, delay=2)
    def fetch_by_contact_email(self, table_name, contact_email):
        return (
            self.db.table(table_name)
            .select("*")
            .eq("contact_email", contact_email)
            .execute()
        )
    @retry(max_attempts=5, delay=2)
    def fetch_by_contact_email_and_last_initial_message(self, table_name, contact_email, last_contact):
        return (
            self.db.table(table_name)
            .select("*")
            .eq("contact_email", contact_email)
            .lt("initial_message_last_contact_date", last_contact)
            .execute()
        )

    @retry(max_attempts=5, delay=2)
    def get_system_prompt(self, table_name, org_id):
        return (
            self.db.table(table_name)
            .select("*")
            .order("created_at", desc=True)
            .limit(1)
            .eq("org_id", org_id)
            .execute()
        )

    @retry(max_attempts=5, delay=2)
    def update(self, table_name: str, row: dict, id: str):
        return self.db.table(table_name).update([row]).eq("id", id).execute()
    

    @retry(max_attempts=5, delay=2)
    def update_by_contactid(self, table_name: str, row: dict, contactid: str):
        return (
            self.db.table(table_name).update([row]).eq("contactid", contactid).execute()
        )

    @retry(max_attempts=5, delay=2)
    def update_by_org_id(self, table_name: str, row: dict, org_id: str):
        return self.db.table(table_name).update([row]).eq("org_id", org_id).execute()

    @retry(max_attempts=5, delay=2)
    def delete(self, table_name, id):
        return self.db.table(table_name).delete().eq("id", id).execute()

    @retry(max_attempts=5, delay=2)
    def check_by_contact_phone(self, table_name, contact_phone):
        return (
            self.db.table(table_name)
            .select("*")
            .eq("contact_phone", contact_phone)
            .eq("org_id", "karibew")
            .execute()
        )

    @retry(max_attempts=5, delay=2)
    def fetch_messages(self, table_name, direction, org_id, contact_phone):
        return (
            self.db.table(table_name)
            .select("utc_datetime, content, direction")
            .order("utc_datetime", desc=False)
            .eq("direction", direction)
            .eq("org_id", org_id)
            .eq("contact_phone", contact_phone)
            .execute()
        )

    @retry(max_attempts=5, delay=2)
    def fetch_all_messages(self, table_name, contactid):
        return (
            self.db.table(table_name)
            .select("*")
            .order("created_at", desc=False)
            .eq("contactid", contactid)
            .execute()
        )

    @retry(max_attempts=5, delay=2)
    def fetch_initial_message(self, table_name, contactid):
        return (
            self.db.table(table_name)
            .select("*")
            .eq("contactid", contactid)
            .eq("type", "initial_text")
            .eq("campaign", "outbound_Joe")
            .execute()
        )
    @retry(max_attempts=5, delay=2)
    def delete_contact(self, contact_email):
        return self.db.table("contacts").delete().eq("contact_email", contact_email).execute()

    @retry(max_attempts=5, delay=2)
    def fetch_all_messages_by_campaign(self, table_name, contactid, campaign):
        return (
            self.db.table(table_name)
            .select("*")
            .order("created_at", desc=False)
            .eq("contactid", contactid)
            .eq("campaign", campaign)
            .execute()
        )

    @retry(max_attempts=5, delay=2)
    def get_prompt(self, bot_name):
        return self.db.table("bots").select("*").eq("id", bot_name).execute()

    @retry(max_attempts=5, delay=2)
    def update_by_id(self, table_name: str, row: dict, id: str):
        return self.db.table(table_name).update([row]).eq("contactid", id).execute()

    @retry(max_attempts=5, delay=2)
    def update_by_contact_email(self, table_name: str, row: dict, contact_email: str):
        return (
            self.db.table(table_name)
            .update([row])
            .eq("contact_email", contact_email)
            .execute()
        )
