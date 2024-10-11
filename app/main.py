from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from app.db import get_db_connection
from app.units import get_shapeInfo


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
    shapeInfo = get_shapeInfo(conn)
    sql = [["" for _ in range(3)] for _ in range(shapeInfo.__len__())]
    for shape in request.shapeSet:

        # generate the SQL header (referance to the shape table)
        sql[shape.id] = f"SELECT {shapeInfo[0]['colnames'][0]}.*, " \
                               f"{shapeInfo[shape.id]['colnames'][0]}.*, " \
                               f"{shapeInfo[shape.id]['colnames'][1]}.*\n"
        sql[shape.id] += f"FROM {shapeInfo[0]['colnames'][0]}\n"
        sql[shape.id] += f"JOIN {shapeInfo[shape.id]['colnames'][0]} " \
                           f"ON {shapeInfo[shape.id]['colnames'][0]}.gup_id = {shapeInfo[0]['colnames'][0]}.id\n"

        print(sql[shape.id])
        for generic in request.genericSet:
            # print(f"Generic: {generic.parameter}, {generic.value}")
            pass
        for freq in request.freqSet:
            # print(f"Freq: {freq.parameter}, {freq.value}")
            pass

