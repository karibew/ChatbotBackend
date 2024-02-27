<h1 align="center" id="title">Karibew Joe</h1>


# create virtual environment
python -m venv .venv
 
# activate environment for MacOs
source ./env/bin/activate (macos)


# activate environment for Windows
source ./env/Scripts/activate (window)


# install dependencies
pip install -r requirements.txt

# start application
uvicorn main:app --port=3000 --reload


# start worker
python worker.py


# need environment variables
* FH_SUPABASE_URL = 
* FH_SUPABASE_KEY =
* REDIS_PORT = 
* REDIS_HOST = 
* REDIS_PASSWORD = 
* FH_TWILIO_NUMBER = 
* OPENAI_API_KEY =
* FH_TWILIO_SID = 
* FH_TWILIO_AUTH_TOKEN = 
* ZAPIER_URL ="https://hooks.zapier.com/hooks/catch/15188930/3k91xbz/" 
* ZAPIER_CONTACT_SAVE_WEBHOOK="https://hooks.zapier.com/hooks/catch/15188930/3fei07y/"


<h6 align="center" id="title">Powered By Gepeto</h6>



