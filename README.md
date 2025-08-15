# TrustLens – Demo (Frontend/Backend/API)

Quick demo for the applied project.
- Streamlit UI (`app_streamlit.py`)
- FastAPI backend (`backend_api.py`) + `openapi.yaml`
- Sample data (`data/adult_tiny.csv`)
- Simple PDF report builder (`report_utils.py`)

## Frontend
pip install -r requirements.txt

streamlit run app_streamlit.py

## Backend (optional)
pip install -r requirements.txt

uvicorn backend_api:app --reload --port 8000
