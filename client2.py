import os
import json
import requests

with open("config.json" , "r") as f:
    configs = f.read()
    configs = json.loads(configs)

server_username = configs["server_username"]
client_username = configs["client_username"]
client_api_token = configs["client_api_key"]

auth_header = {
    "Authorization":f"Bearer {client_api_token}"
}

#create challenge to make a channel for communication
payload = {
    "rated":False,
    "days":14,
    "color":"white",
    "variant":"standard",

}

r = requests.post(f"https://lichess.org/api/challenge/{server_username}" , headers=auth_header,json=payload)
print(r.status_code)
print(r.text)
