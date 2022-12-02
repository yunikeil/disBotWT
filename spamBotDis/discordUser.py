import requests
from json import dumps
import time
from threading import Thread


class Client():
    def __init__(self):
        self.token = None
        self.password = None
        self.email = None
        self.api = "https://discord.com/api/v9"
        self.headers = {
            "Content-Type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }

    def login(self, email: str, password: str):
        data = dumps({
            "login": email,
            "password": password,
            "undelete": False,
            "captcha_key": None,
            "login_source": None,
            "gift_code_sku_id": None
        })
        response = requests.post(
            f"{self.api}/auth/login",
            headers=self.headers,
            data=data).json()
        try:
            self.email = email
            self.password = password
            self.token = response["token"]
            self.headers["Authorization"] = self.token
        except KeyError:
            exit(response)
        return response

    def my_channels(self):
        return requests.get(
            f"{self.api}/users/@me/channels",
            headers=self.headers).json()

    def send_message(self, content: str = None, channel_id: int = None):
        data = dumps({"content": content})
        return requests.post(
            f"{self.api}/channels/{channel_id}/messages",
            headers=self.headers,
            data=data).json()


client = Client()
client.login(email='iyunakov@inbox.ru', password='nina24011953nina')

message = 'Your message'

channels = client.my_channels()
for i in range(len(channels)):
    try:
        print(channels[i]['id'], ' : ', channels[i]['recipients'][0]['username'])
    except:
        print(channels[i]['id'])
channe_id = input("Введите id канала для спама>> ")


def spam_func(message, channe_id):
    try:
        while True:
            for i in range(5):
                client.send_message(message, channe_id)
                time.sleep(100)
    except:
        print("Произошла ошибка!")


for i in range(3):
    Thread(target=spam_func, args=(message, channe_id)).start()
