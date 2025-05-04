from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: float
    description: str
    city: str
    humidity: int
    wind_speed: float 