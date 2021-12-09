from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List, Dict

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class ChatLog(BaseModel):
    timestamp: str
    responses: Dict = {}

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "timestamp": "jdoe@example.com",
                "responses": "{}",
            }
        }

class UserModel(BaseModel):
    id: str = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(...)
    fname: str
    lname: str
    password:str
    age: str = ''
    image: str = ''
    bdi: List = []
    chatlog: ChatLog = {
        "timestamp": "",
        "responses": "{}",
    }

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id":"612276184b9add2e0452e721",
                "fname": "Jane",
                "lname": "Doe",
                "email": "jdoe@example.com",
                "password": "test123",
            }
        }

class RegisterUserModel(BaseModel):
    email: EmailStr = Field(...)
    fname: str
    lname: str
    password:str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "fname": "Jane",
                "lname": "Doe",
                "email": "jdoe@example.com",
                "password": "test123",
            }
        }

class UpdateUserModel(BaseModel):
    fname: Optional[str]
    lname: Optional[str]
    email: Optional[EmailStr]
    image: Optional[str]
    password: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "fname": "Jane",
                "lname": "Doe"
            }
        }

class LoginUserModel(BaseModel):
    email: EmailStr = Field(...)
    password:str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "jdoe@example.com",
                "password": "test123",
            }
        }

class BdiModel(BaseModel):
    # id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    score: int
    timestamp: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "score": 15,
                "timestamp":"Mon, 13 Sep 2021 19:48:27 GMT"
            }
        }

class ChatQuestionModel(BaseModel):
    no: int
    text: str
    format:str
    options:List = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "no": 3,
                "text":"What are your hobbies/interests? [MCQ - Music, Sports, Politics, Others(text box)]",
                "format":"text",
                "options":[]
            }
        }

class ChatResponseModel(BaseModel):
    # id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    respNo: int
    response: str
    questionFormat:str
    timestamp: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "repNo": 3,
                "response":"All the time",
                "questionFormat":"mcq",
            }
        }

class ChatResultModel(BaseModel):
    mcq: Dict = {}
    speech: Optional[int]
    text: Optional[int]
    speechText: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "mcq": {},
                "speech":0,
                "text":0,
                "speechText":0,
            }
        }

class FeedbackModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    message: str
    name: Optional[str]
    email: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "message": "Thank you",
                "name":"Jane Doe",
                "email":"janedoe@gmail.com"
            }
        }

class FileUploadModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    image: Dict

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id":"612276184b9add2e0452e721",
                "image": {}
            }
        }
