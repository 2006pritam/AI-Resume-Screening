import uvicorn
import os

if __name__ == "__main__":
    # Ensure initial data exists
    data_gen_path = os.path.join(os.path.dirname(__file__), "data_generator.py")
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "data", "resumes.json")):
        os.system(f"python3 {data_gen_path}")

    print("=" * 65)
    print("🚀 Starting AI Resume Screening & Candidate Clustering Server")
    print("📍 Dashboard UI: http://localhost:8000")
    print("📖 API Swagger Docs: http://localhost:8000/docs")
    print("=" * 65)
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
