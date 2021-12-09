print('----------------------------------------------------------------------')
import os
import shutil
from fastapi import FastAPI, Body, HTTPException, status
from fastapi import File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from model import *
from questions import questionList
from answers import questionAnswerList

import bson
from typing import Dict
from pymongo import MongoClient
import motor.motor_asyncio

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from python_speech_features import mfcc
import python_speech_features
import tensorflow
from statistics import mean
import pickle
import sklearn
import ktrain
import ffmpeg
import librosa
from tensorflow.keras.models import model_from_json

import plotly.graph_objects as go
import plotly.offline as pyo

json_file = open('D:/College/Semester_6/Capstone_Project/website/full-stack-implementation/backend/ML/Models/model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
cnn_model = model_from_json(loaded_model_json)
cnn_model.load_weights("D:/College/Semester_6/Capstone_Project/website/full-stack-implementation/backend/ML/Models/model.h5")

rf_model = pickle.load(open('D:/College/Semester_6/Capstone_Project/website/full-stack-implementation/backend/ML/Models/RF_model.sav', 'rb'));

bert_model = ktrain.load_predictor('D:/College/Semester_6/Capstone_Project/website/full-stack-implementation/backend/ML/Models/BERT')

d = {'sadness':0, 'neutral':0, 'anger':0, 'joy':0, 'fear':0}
speech = []

def phqvalues(aud):
    signal, sr = librosa.load(aud)
    mfccs = librosa.feature.mfcc(y=signal, n_mfcc=13, sr=sr)
    mfcc_mean = np.mean(mfccs.T, axis=0)
    arr = mfcc_mean.tolist()
    phq_score = rf_model.predict([arr])
    phq_binary = cnn_model.predict([arr])
    if phq_binary[0][0]>phq_binary[0][1]:
        b = 0
    else:
        b = 1
    score = phq_score[0]
    if (b==0 and score<=9) or (b==1 and score>9):
        speech.append(phq_score[0])
    return(score)

# bert_model
def textclassify(message):
    ans = bert_model.predict(message)
    print(message,'--->',ans)
    d[ans]+=1
    return ans

def textscore():
    negative = d['sadness'] + d['anger'] + d['fear']
    total = 4 #Check how many
    score = (negative/total)*24
    return int(score)


def final_score():
    text = textscore()
    voice = mean(speech)
    diff = abs(text-voice)
    if diff>=5:
        print('not')
        return voice
    else:
        print('here')
        return (round((text+voice)/2))

# print(textclassify('Stressed out and lazy but somehow managing'));

# print(phqvalues('D:\Downloads\sample377_chunk36.wav'));

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://test123:test123@cluster0.pvz0r.mongodb.net/FinanceTracker?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority")
database = client.HushMind
users_collection = database.users
feedback_collection = database.feedback

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:3000",
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/user/login",response_description="User login authentication")
async def login_user(user: LoginUserModel = Body(...)):
    document = jsonable_encoder(user)
    if (user := await users_collection.find_one(document)) is not None:
        return user
    raise HTTPException(status_code=400, detail=f"Invalid credentials entered, please try again")

@app.post("/user/register", response_description="Register a new User")
async def register_user(user: UserModel = Body(...)):
    document = jsonable_encoder(user)
    # print(document)
    try:
        new_user = await users_collection.insert_one(document)
        inserted_id = str(new_user.inserted_id)
        # print(inserted_id)

        registered_user = await users_collection.find_one({"_id":inserted_id})

        if(register_user):
            return {"message":"registration successful"}
        else:
            raise HTTPException(status_code=404, detail=f"Registration Unsuccessful");

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

@app.get("/user/get/{id}", response_description="Get a single User", response_model=UserModel)
async def show_user(id: str):
    if (user := await users_collection.find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=404, detail=f"User with id: {id} not found")


@app.put("/user/update/{id}", response_description="Update a student", response_model=UpdateUserModel)
async def update_user(id: str, user: UpdateUserModel = Body(...)):
    user = {k: v for k, v in user.dict().items() if v is not None}
    # print(user)
    try:
        if len(user) >= 1:
            update_result = await users_collection.update_one({"_id": id}, {"$set": user});

            if (existing_user := await users_collection.find_one({"_id": id})) is not None:
                return existing_user
            else:
                raise HTTPException(status_code=404, detail=f"User with id: {id} not found");
            #     return(user)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

@app.put("/user/update/image/{id}", response_description="Update a student")
async def update_user_image(id: str,image: UploadFile = File(...)):
    # filetype = image.content_type.split('/')[1]
    filename = f'{id}_{image.filename}'
    file_location = os.path.join(os.path.dirname(__file__), f'static/{filename}')
    file_location = os.path.normpath(file_location)

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(image.file, file_object)

    try:
        updated_user = await users_collection.update_one({"_id": id},{"$set":{"image":filename}});

        if (existing_user := await users_collection.find_one({"_id": id})) is not None:
            return existing_user
            # return {"image":filename}
        else:
            raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

    # return({"message":"success"})

@app.delete("/user/delete/{id}", response_description="Delete a user")
async def delete_student(id: str):
    delete_result = await users_collection.delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

# @app.get("", response_description="Return a chat question")
@app.put("/user/chat/question/{id}",response_model=ChatQuestionModel)
async def chat_question(id: str,qno: str, chatResponse: ChatResponseModel = Body(...)):
    chatResponse = jsonable_encoder(chatResponse)
    nextQuestionNumber = "#" + qno
    existing_user = None
    updated_user = None

    try:
        if (existing_user := await users_collection.find_one({"_id": id})) is not None:
            pass
        else:
            raise HTTPException(status_code=404, detail=f"User with id: {id} not found");
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

    if str(chatResponse["respNo"]) == '0':
        existing_user["chatlog"]["timestamp"] = chatResponse["timestamp"]
        existing_user["chatlog"]["responses"] = {
                "mcq":{
                        "0":0,"1":0,"2":0,"3":0,"4":0,
                        "5":0,"6":0,"7":0,"8":0,"9":0,
                    },
                "text":[],
                "speech":[]
            }

    elif str(chatResponse["respNo"]) == '3':
        existing_user["age"]= chatResponse["response"]

    else:
        questionInfo = questionAnswerList[('#' + str(chatResponse["respNo"]))]
        questionConsiderationStatus = questionInfo['consider']
        if questionConsiderationStatus == True:
            if questionInfo["type"] == "mcq":
                currentSymptomScore = existing_user["chatlog"]["responses"]["mcq"][str(questionInfo["symptomCode"])]
                existing_user["chatlog"]["responses"]["mcq"][str(questionInfo["symptomCode"])] = currentSymptomScore + int(chatResponse["response"])

            elif questionInfo["type"] == "text":
                existing_user["chatlog"]["responses"]["text"].append(chatResponse["response"])

            elif questionInfo["type"] == "speech" and len(chatResponse["response"]):
                existing_user["chatlog"]["responses"]["speech"].append(chatResponse["response"])

    try:
        await users_collection.update_one({"_id": id}, {"$set": existing_user});

        if (updated_user := await users_collection.find_one({"_id": id})) is not None:
            pass
            # print(updated_user)
        else:
            raise HTTPException(status_code=404, detail=f"Something went wrong, please try later");
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

    if (q := questionAnswerList[nextQuestionNumber]) is not None:
        return({"no":qno,"text":q["questionLabel"],"options":q["responseValue"],"format":q["type"]});
    raise HTTPException(status_code=404, detail=f"Question number {qno} not found")

@app.put("/user/chat/audio/{id}")
async def chat_audio_submit(id: str,qno: str, audio: UploadFile = File(...)):
    # filetype = image.content_type.split('/')[1]
    filename = audio.filename
    file_location = os.path.join(os.path.dirname(__file__), f'static/audio/{filename}')
    file_location = os.path.normpath(file_location)

    print('hi')
    with open(file_location, "wb+") as file_object:
        print('hi')
        shutil.copyfileobj(audio.file, file_object)
    print('hi')
    return({"message":"success","filename":filename})

@app.get("/user/chat/result/{id}",response_model=ChatResultModel)
async def chat_result(id: str):
    existing_user = None
    updated_user = None
    thetaList = [i * 36 for i in range(0,10)]
    widthList = [36] * 10
    # rList = [3.5, 1.5, 2.5, 4.5, 4.5, 4, 3,2,3.5,3]
    colorList = ["#2E1D1D","#4A2121","#800F2F","#A4133C","#C9184A","#FF4D6D","#FF758F","#FF8FA3","#F2B7C1","#FFCCD5"]
    labelList = ['value'] * 10
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    try:
        if (existing_user := await users_collection.find_one({"_id": id})) is not None:
            pass
            # print('>>existing user',existing_user,'\n')
        else:
            raise HTTPException(status_code=404, detail=f"User with id: {id} not found");
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

    if existing_user is not None:

        print(existing_user["chatlog"]["responses"]["text"])
        print(existing_user["chatlog"]["responses"]["speech"])

        for text in existing_user["chatlog"]["responses"]["text"]:
            textclassify(text)

        print(d)

        for audioName in existing_user["chatlog"]["responses"]["speech"]:
            audioPath = os.path.join(os.path.dirname(__file__), f'static/audio/{audioName}')
            audioPath = os.path.normpath(audioPath)
            # print(audioPath)
            currAudioResult = phqvalues(audioPath)
            speech.append(currAudioResult)

        textScoreValue = textscore()
        speechScoreValue = mean(speech)
        finalScoreValue = final_score()
        # textScoreValue = textscore()
        # speechScoreValue = 10
        # finalScoreValue = 20

#       Generate charts

        # Polar Area Chart
        rList =  [ existing_user["chatlog"]["responses"]["mcq"][symptomCode] for symptomCode in existing_user["chatlog"]["responses"]["mcq"]]
        print('rList: ',rList)

        figPolar = go.Figure(go.Barpolar(r=rList,theta=thetaList,width=widthList,marker_color=colorList,marker_line_color="black",
                                        marker_line_width=1,opacity=0.8),layout=layout)

        figPolar.update_layout(
            template=None,
            polar = dict(
                radialaxis = dict(range=[0, 5], showticklabels=False, ticks=''),
                angularaxis = dict(showticklabels=False, ticks='')
            )
        )

        polarChart_filepath = os.path.join(os.path.dirname(__file__), f'static/charts/{id}_polarChart.svg')
        figPolar.write_image(polarChart_filepath)

        # Population pie chart
        popColours = ['#ffadad', '#fc6681', '#593434']
        markersDict = dict(colors=popColours)
        ageGroupLabels = ['17 - 25 Years','26 - 40 Years','41 - 50 Years']
        popValues = [91,35,31]
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        figPie = go.Figure(data=[go.Pie(labels=ageGroupLabels,values=popValues)],layout=layout)
        figPie.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                          marker=markersDict)

        pieChart_filepath = os.path.join(os.path.dirname(__file__), f'static/charts/{id}_pieChart.svg')
        figPie.write_image(pieChart_filepath)

        # print({"mcq": {},"speech":0,"text":textScoreValue,"speechText":finalScoreValue});
        return({"mcq":existing_user["chatlog"]["responses"]["mcq"],"speech":speechScoreValue,"text":textScoreValue,"speechText":finalScoreValue});

    raise HTTPException(status_code=404, detail=f"Question number {qno} not found")

@app.put("/user/bdi/{id}", response_description="update and return BDI score")
async def update_bdi_Score(id: str, bdiResult: BdiModel = Body(...)):
    bdiResult = jsonable_encoder(bdiResult)
    try:
        if (existing_user := await users_collection.find_one({"_id": id})) is not None:
            (existing_user)["bdi"].append(bdiResult)

            await users_collection.update_one({"_id": id}, {"$set": existing_user});

            if (updated_user := await users_collection.find_one({"_id": id})) is not None:
                return updated_user
            else:
                raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

        else:
            raise HTTPException(status_code=404, detail=f"User with id: {id} not found");

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User with id: {id} not found")

@app.post("/feedback",response_description="Send feedback email")
async def feedback(feedback: FeedbackModel = Body(...)):
    document = jsonable_encoder(feedback)
    # print(document)
    try:
        new_feedback = await feedback_collection.insert_one(document)
        inserted_id = str(new_feedback.inserted_id)
        # print(inserted_id)

        inserted_feedback = await feedback_collection.find_one({"_id":inserted_id})

        if(inserted_feedback):
            return {"message":"feedback successfully sent"}
        else:
            raise HTTPException(status_code=404, detail=f"Unsuccessful");

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Something went wrong, please try again later");
