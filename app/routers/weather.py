from fastapi import APIRouter, HTTPException, Depends
from ..schemas.weather import WeatherResponse
from .auth import get_current_user
import random
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{city}", response_model=WeatherResponse)
def get_weather(city: str, current_user: dict = Depends(get_current_user)):
    logger.debug(f"Received weather request for city: {city}")
    # 임의의 날씨 데이터 생성
    weather_data = WeatherResponse(
        temperature=round(random.uniform(15, 30), 1),  # 15~30도 사이의 온도
        description=random.choice(["Sunny", "Cloudy", "Rainy", "Snowy", "Thunderstorm", "Foggy", "Windy"]),
        city=city,
        humidity=random.randint(30, 90),  # 30~90% 사이의 습도
        wind_speed=round(random.uniform(0, 10), 1)  # 0~10 m/s 사이의 풍속
    )
    
    logger.debug(f"Weather data requested for {city}: {weather_data.dict()}")
    
    return weather_data 