import os
import sys
from fastapi import FastAPI
from src.router.webhooks import webhook_router
from src.configurations.logging import logging
from dotenv import load_dotenv

load_dotenv()

# required_env_vars = [
#     "FH_SUPABASE_URL", "FH_SUPABASE_KEY", "REDIS_PORT", "REDIS_HOST",
#     "REDIS_PASSWORD", "FH_TWILIO_NUMBER", "OPENAI_API_KEY",
#     "FH_TWILIO_SID", "FH_TWILIO_AUTH_TOKEN","ZAPIER_URL","ZAPIER_CONTACT_SAVE_WEBHOOK"
# ]
required_env_vars = [
    "FH_SUPABASE_URL", "FH_SUPABASE_KEY", "REDIS_PORT", "REDIS_HOST",
    "REDIS_PASSWORD", "OPENAI_API_KEY"
]


def check_env_vars():
    for var in required_env_vars:
        if not os.getenv(var):
            logging.info("Error: Environment variable %s is not set.", var)
            return False
    return True


if not check_env_vars():
    sys.exit("Exiting: Required environment variables are not set.")

app = FastAPI(title="KARIBEW")


@app.get('/', tags=['health'], summary="Check server health")
def root():
    return {"message": 'healthy'}


app.include_router(webhook_router)
