# ATS Score Calculator and Video Analysis API
satyam
A FastAPI-based REST API that provides ATS (Applicant Tracking System) score calculation and video analysis capabilities.

## Features

- Calculate ATS scores for resumes against job descriptions
- Analyze videos for face recognition
- Detailed scoring and feedback system
- Cross-origin resource sharing (CORS) enabled
- Comprehensive logging

## Prerequisites

- Python 3.8+
- Virtual Environment
- FFmpeg (for video processing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
app/
├── main.py
├── models/
│   └── schemas.py
├── services/
│   ├── ats_calculator.py
│   └── video_analyzer.py
└── utils/
    └── logger.py
```

## Environment Variables

Create a `.env` file in the root directory and add the following variables:
```
# Add any necessary environment variables here
```

## Running the Application

1. Ensure your virtual environment is activated
2. Start the FastAPI server:
```bash
python app/main.py
```
Or using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Calculate ATS Score

```http
POST /calculate-ats-score
```

Request body:
```json
{
    "resume": "Resume text content",
    "job_description": "Job description text content"
}
```

Response:
```json
{
    "score": 85.5,
    "category_scores": {
        "skills_match": 80,
        "experience_match": 90
        // ... other category scores
    }
}
```

### Analyze Video

```http
POST /analyze/
```

Form data:
- `id`: String identifier
- `known_face_image`: Image file (.jpg)
- `video_file`: Video file (.mp4)

Response:
```json
{
    "results": {
        // Analysis results
    }
}
```

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Successful operation
- 400: Bad request
- 500: Internal server error

Error responses include a detail message explaining the error.

## Requirements

See `requirements.txt` for a full list of dependencies. Key packages include:
- fastapi
- uvicorn
- python-multipart
- face-recognition
- opencv-python

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # If you have separate dev requirements
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Support

For support, please [create an issue](repository-issues-url) or contact [your-email].
