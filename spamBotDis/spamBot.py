import discord
from discord.ext import commands

import requests
from json import dumps


# Сюда можно будет добавить многопоточность, асинхронность прокси и так далее...
def getToken(email: str, password: str):
    api = "https://discord.com/api/v10"
    headers = {
        "Content-Type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    data = dumps({
        "login": email,
        "password": password,
        "undelete": False,
        "captcha_key": None,
        "login_source": None,
        "gift_code_sku_id": None
    })
    response = requests.post(f"{api}/auth/login", headers=headers, data=data).json()
    if response.get('token') is not None:
        return response
    elif response.get('captcha_sitekey') is not None:
        exit(f"captcha detected\nsitekey: {response.get('captcha_sitekey')}")
        # Если есть желание сюда можно подключить rucaptcha
    else:
        exit(response)


headers = {"Content-Type": "application/json",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                         " (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
           'Authorization': 'Mjg2OTE0MDc0NDIyMjgwMTk0.GN4pHy.M5oVOvH1YSYGuMyYFg9Rpf8OtBVNQWaN8BKc1E'}
response = requests.get("https://discord.com/api/v10/guilds/899793728145858611/members", headers=headers).json()

print(response)

