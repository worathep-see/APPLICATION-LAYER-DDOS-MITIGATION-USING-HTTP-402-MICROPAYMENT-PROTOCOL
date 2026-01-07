from locust import HttpUser, task, between
import requests
import uuid
import json


BANK_API_URL = "http://188.166.254.136"

class SmartClient(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):

        # เริ่มต้นผู้ใช้แต่ละคน
        self.user_id = None
        self.tokens = []
        self.prepare_bank_account()

    def prepare_bank_account(self):
        try:
            # สมัครสมาชิก
            username = f"user_{str(uuid.uuid4())[0:8]}"
            response_register = self.client.post(
                f"{BANK_API_URL}/users/", json={
                "username": username,
                "password": "password123",
                "initial_balance": 0.0
                },
                name ="/users/ [register]"
            )

            if response_register.status_code == 200:
                self.user_id = response_register.json()['id']

                topup_response = self.client.post(
                    f"{BANK_API_URL}/topup/", json={
                    "user_id": self.user_id,
                    "amount": 100.0},
                    name = "/topup/"
                )
                if topup_response.status_code != 200:
                    print(f"Topup failed: {topup_response.text}")
            else:
                print(f"Register failed: {response_register.text}")

        except Exception as e:
            print(f"Bank Connection Error: {e}")
    @task
    def access_service_with_payment(self):
        
        if not self.user_id:
            return
        
        headers = {}
        if self.tokens:
            headers = {"X-Payment-Token": self.tokens}
        
        with self.client.get("/premium-data", headers=headers, catch_response=True) as response:

            if response.status_code == 402:
                response.success()

                self.buy_token()

            elif response.status_code == 200:
                response.success()
            
                if self.tokens:
                    self.tokens.pop(0)

            else:
                response.failure(f"Unexpected Status: {response.status_code}")
    
    def buy_token(self):
        if not self.user_id:
            return
        
        try:
            response_buy = self.client.post(
                f"{BANK_API_URL}/purchase/", json={
                "user_id": self.user_id,
                "quantity": 50},
                name ="/purchase/"    
            )

            if response_buy.status_code == 200:
                token_data = response_buy.json()
                if 'tokens' in token_data:
                    self.tokens.extend(token_data['tokens'])
        except Exception as e:
            print(f"Purchase Error: {e}")