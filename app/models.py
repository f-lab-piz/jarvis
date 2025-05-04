from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True

class RegisterResponse(BaseModel):
    message: str
    username: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class WeatherResponse(BaseModel):
    temperature: float
    description: str
    city: str
    humidity: int
    wind_speed: float 