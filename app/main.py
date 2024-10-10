from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from app.db import get_db_connection


app = FastAPI()

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

@app.post("/query/api/")
def query_api(request: queryRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    for shape in request.shapeSet:
        # print(f"Shape: {shape.id}, {shape.name}")
        for generic in request.genericSet:
            print(f"Generic: {generic.parameter}, {generic.value}")
            pass
        for freq in request.freqSet:
            print(f"Freq: {freq.parameter}, {freq.value}")
            pass

