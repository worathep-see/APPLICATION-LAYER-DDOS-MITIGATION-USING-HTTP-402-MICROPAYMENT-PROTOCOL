from locust import HTTPUser, task, between
import requests
import uuid
import json


BANK_API_URL = "http://127.0.0.1:8000"

class SmartClient(HTTPUser):
    wait_time = between(1, 3)

    def on_start(self):

        # เริ่มต้นผู้ใช้แต่ละคน
        self.user_id = None
        self.token = None
        self.prepare_bank_account()

    def prepare_bank_account(self):
        try:
            # สมัครสมาชิก
            username = f"user_{str(uuid.uuid4())[0:8]}"
            response_register = requests.post(f"{BANK_API_URL}/users/", json={
                "username": username,
                "password": "password123",
                "initial_balance": 0.0
            })
            if response_register.status_code == 200:
                self.user_id = response_register.json()['id']

                requests.post(f"{BANK_API_URL}/topup/", json={
                    "user_id": self.user_id,
                    "amount": 100.0
                })
            else:
                print(f"Register failed: {response_register.text}")
        except Exception as e:
            print(f"Bank Connection Error: {e}")
    @task
    def access_service_with_payment(self):
        
        headers = {}
        if self.token:
            headers = {"X-Payment-Token": self.token}
        
        with self.client.get("/premium-data", headers=headers, catch_response=True) as response:

            if response.status_code == 402:
                response.failure("402 Payment Required")

                self.buy_token()

            elif response.status_code == 200:
                response.success()
            
            else:
                response.failure(f"Unexpected Status: {response.status_code}")
    
    def buy_token(self):
        try:
            response_buy = requests.post(f"{BANK_API_URL}/purchase/", json={
                "user_id": self.user_id,
                "quantity": 50
            })

            if response_buy.status_code == 200:
                token_data = response_buy.json()
                if 'token' in token_data and len(token_data['tokens']) > 0:
                    self.token = token_data['tokens'][0]
        except Exception as e:
            print(f"Purchase Error: {e}")
