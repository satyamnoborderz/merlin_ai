# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile
from app.models.schemas import ATSRequest, ATSResponse
from app.services.ats_calculator import ATSCalculator
from app.utils.logger import setup_logger
import os,shutil,tempfile
from app.services.video_analyzer import VideoAnalyzer 
from fastapi.middleware.cors import CORSMiddleware




logger = setup_logger()
app = FastAPI(title="ATS Score Calculator API")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ats_calculator = ATSCalculator()

@app.post("/calculate-ats-score", response_model=ATSResponse)
async def calculate_ats_score(request: ATSRequest):
    try:
        score, category_scores, resume_info, job_info = ats_calculator.calculate_ats_score(
            request.resume,
            request.job_description
        )
        feedback = ats_calculator.provide_feedback(score, category_scores, resume_info, job_info)
        
        return ATSResponse(
            score=score,
            category_scores=category_scores,
            # feedback=feedback,
            # resume_info=resume_info,
            # job_info=job_info
        )
    except Exception as e:
        logger.error(f"Error processing ATS score calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))







@app.post("/analyze/")
async def analyze_video(id: str, known_face_image: UploadFile = File(...), video_file: UploadFile = File(...)):
    try:
        import time
        st =time.time()
        known_face_image_path = tempfile.mktemp(suffix='.jpg')
        with open(known_face_image_path, 'wb') as f:
            shutil.copyfileobj(known_face_image.file, f)

        video_path = tempfile.mktemp(suffix='.mp4')
        with open(video_path, 'wb') as f:
            shutil.copyfileobj(video_file.file, f)

        analyzer = VideoAnalyzer(known_face_image_path)
        results = analyzer.analyze(video_path)

        os.remove(known_face_image_path)
        os.remove(video_path)
        print(time.time()-st)
        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"Error in video analysis API: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# You can add more endpoints if necessary






if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)