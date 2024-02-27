import requests

class Salesforce():
    def __init__(self):
        pass


def get_access_token():
    url = "https://fullharvesttechnologies.my.salesforce.com/services/oauth2/token"

    payload = 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOiIzTVZHOUtzVmN6Vk5jTTh6M29WYkFDa2xLV3oxNDFoeW02OGZFVTdBUGt6UTE4NUdUeGpyU1ZDc3Q5U1pzVHFWZXFxbXVYZVlvZ1JucTJuQzJMNW1UIiwic3ViIjoidXphaXIrZnVsbGhhcnZlc3RAaGVsbG9nZXBldG8uY29tIiwiYXVkIjoiaHR0cHM6Ly9sb2dpbi5zYWxlc2ZvcmNlLmNvbSIsImV4cCI6IjE3OTk5OTI1NDIifQ.VkQYgwUo8qh42G90YWOaeJ3o3Ar6ptvqTwcbcyWWVm_ra6II_dWN6pvq_2XeSnpkh_9dRzQpyo-xxVvQSzwPkIHBwKVJSpFGap9griXjBD3PFJ10KZ_cbwJec2qEo6HB7M7x0sSUx59Z7qIfslrOdzb6uvq7Lj_KAQRcJiuEfq2Tvjs5YNtvzbCoKroHcixzgB55lSOpqJfWKSj7zab8Tb5yl3759r1TOCf8fjXOn5hp0HZzuQ75_PuCdAbNYYGXJSJXX0aqouWOhOLncnF9P0v6IdCNmWgz1CLqFSPyZu9Rcdm0ArZVe-xKHeEffxV1ZHFA6ISzkNbh461i_kQvrw'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'BrowserId=gXJxpoMqEe6SLUWWiAkIeQ; CookieConsentPolicy=0:1; LSKey-c$CookieConsentPolicy=0:1'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()['access_token']




# Your Salesforce access token
access_token = get_access_token()

# Salesforce instance URL
instance_url = 'https://fullharvesttechnologies.my.salesforce.com'

# Headers for the request
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Endpoint for contacts or leads (choose one)
# For Contacts
#endpoint = '/services/data/vXX.0/query/?q=SELECT+Id,Name+FROM+Contact'
# For Leads
endpoint = '/services/data/v50.0/query/?q=SELECT+Id,Name+FROM+Lead'

# Making the GET request
response = requests.get(instance_url + endpoint, headers=headers)

# Checking if the request was successful
if response.status_code == 200:
    # Parsing the response
    data = response.json()
    print("Data Retrieved Successfully:", data)
else:
    print("Failed to retrieve data:", response.status_code, response.text)