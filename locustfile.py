from locust import HttpUser, task, between
import json
import logging
import random

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # 각 요청 사이에 1-3초 대기

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.username = None

    def generate_random_username(self):
        return f"testuser{random.randint(1000, 9999)}"

    def register_and_login(self):
        max_attempts = 3
        for _ in range(max_attempts):
            try:
                # 랜덤 사용자 생성
                self.username = self.generate_random_username()
                logging.info(f"Attempting to register user: {self.username}")
                
                # 회원가입
                register_response = self.client.post(
                    "/auth/register",
                    json={
                        "username": self.username,
                        "password": "testpass",
                        "email": f"{self.username}@example.com"
                    }
                )
                
                if register_response.status_code == 200:
                    logging.info(f"Successfully registered user: {self.username}")
                    
                    # 로그인
                    login_response = self.client.post(
                        "/auth/login",
                        json={"username": self.username, "password": "testpass"}
                    )
                    
                    if login_response.status_code == 200:
                        self.token = login_response.json()["access_token"]
                        logging.info(f"Successfully logged in as: {self.username}")
                        return True
                    else:
                        logging.error(f"Login failed for {self.username}")
                else:
                    logging.error(f"Registration failed for {self.username}")
                    
            except Exception as e:
                logging.error(f"Error during registration/login: {str(e)}")
                
        return False

    def on_start(self):
        if not self.register_and_login():
            logging.error("Failed to register and login after multiple attempts")

    @task(3)
    def get_weather(self):
        # 랜덤 도시 목록
        cities = ["London", "New York", "Tokyo", "Paris", "Sydney", "Dubai", 
                 "Singapore", "Hong Kong", "Rome", "Barcelona", "Amsterdam", 
                 "Berlin", "Seoul", "Mumbai", "Cairo", "Toronto"]
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            city = random.choice(cities)
            logging.info(f"Attempting to get weather for city: {city}")
            response = self.client.get(f"/weather/{city}", headers=headers)
            logging.info(f"Weather response status: {response.status_code}")
            logging.info(f"Weather response body: {response.text}")
        except Exception as e:
            logging.error(f"Weather request error: {str(e)}") 