from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from app.db import get_db_connection
from app.db import query_generic_gen
from app.db import query_freq_gen
from app.db import query_cat
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
        generic_table = shapeInfo[0]['colnames'][0]
        shape_tables = shapeInfo[shape.id]['colnames']

        sql_pt_generic = query_generic_gen(request.genericSet)
        sql_pt_freq = query_freq_gen(request.freqSet, shape_tables[1]+"_nir")
        print(query_cat(sql_pt_generic, sql_pt_freq, generic_table, shape_tables[0], shape_tables[1]+"_nir"))
        print("\n")
        for generic in request.genericSet:
            # print(f"Generic: {generic.parameter}, {generic.value}")
            pass
        for freq in request.freqSet:
            # print(f"Freq: {freq.parameter}, {freq.value}")
            pass

    return {"message": "OK"}

