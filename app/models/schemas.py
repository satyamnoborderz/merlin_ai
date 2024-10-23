# app/models/schemas.py
from pydantic import BaseModel
from typing import Dict, List, Union, Optional

class ATSRequest(BaseModel):
    job_description: str
    resume: str
    id: str

class ATSResponse(BaseModel):
    score: float
    category_scores: Dict[str, float]
    # feedback: str
    # resume_info: Dict[str, Union[List[str], int]]
    # job_info: Dict[str, Union[List[str], int]]