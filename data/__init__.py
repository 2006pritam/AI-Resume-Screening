import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
from data_generator import generate_synthetic_dataset

def ensure_data():
    data_dir = os.path.join(os.path.dirname(__file__))
    resumes_file = os.path.join(data_dir, "resumes.json")
    jobs_file = os.path.join(data_dir, "jobs.json")
    if not os.path.exists(resumes_file) or not os.path.exists(jobs_file):
        dataset = generate_synthetic_dataset(150)
        with open(jobs_file, "w") as f:
            json.dump(dataset["jobs"], f, indent=2)
        with open(resumes_file, "w") as f:
            json.dump(dataset["resumes"], f, indent=2)

ensure_data()
