from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi_jwt_auth import AuthJWT

## Query API ####################################
class Shape(BaseModel):
    id: int
    name: str

class Generic(BaseModel):
    logic: int
    parameter: int
    rangeMode: int
    showRange: bool
    rangeStart: Optional[float]
    rangeEnd: Optional[float]
    value: Optional[float]
    dispSwitch: int
    selectedMaterial: Optional[int]
    isInvert: bool

class Freq(BaseModel):
    logic: int
    parameter: int
    rangeMode: int
    showRange: bool
    rangeStart: Optional[float]
    rangeEnd: Optional[float]
    value: Optional[float]
    dispSwitch: int
    selectedSparam: Optional[int]
    isInvert: bool

class queryRequest(BaseModel):
    shapeSet: List[Shape]
    genericSet: List[Generic]
    freqSet: List[Freq]


## User API ####################################
class userCreate(BaseModel): # User registration
    username: str
    email: EmailStr
    password: str

class userLogin(BaseModel): # User login
    email: EmailStr
    password: str

class userOut(BaseModel): # User output & profile
    username: str
    email: EmailStr


##
class settings(BaseModel): # Settings of the jwt
    authjwt_secret_key: str
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_secure: bool = False # for development, set True for production
    authjwt_cookie_samesite: str = "lax"
    authjwt_access_token_expires: int = 30 * 24 * 60 * 60 # = 30 days