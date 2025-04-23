# FinancialDataGenAIApi

This project provides a FastAPI-based application for handling data ingestion, transformation using GenAI, and API interfaces for asset and metrics analysis.

## Folder Structure

```
app/
  ├── api/            # API route definitions
  ├── core/           # Database models and configurations
  ├── services/       # GenAI and ingestion logic
  └── main.py         # FastAPI app entry point

tests/
  ├── test_*.py       # Unit tests and Integration Tests for various modules
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- `pip` (Python package installer)

### Installation

1. Clone the repository or extract the provided zip file.
2. Navigate to the project directory.

3. Set the `PYTHONPATH` environment variable:

   **For Windows (PowerShell)**:
   - $env:PYTHONPATH = "YOUR_PROJECT_PATH"

    **For Mac/Linux (PowerShell)**:
   - export PYTHONPATH="YOUR_PROJECT_PATH"

4. Create a virtual environment:

   **For Windows (PowerShell)**:
   - python -m venv venv
   - .\venv\Scripts\activate

    **For Mac/Linux (PowerShell)**:
    - python3 -m venv venv
    - source venv/bin/activate


5. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Running the API Server

```bash
uvicorn app.main:app --reload
```

Access the API documentation at: `http://127.0.0.1:8000/docs`

### Running Tests

```bash
pytest -s .\tests\
```

## APIs

The following main endpoints are available:

- `POST /assets` - Interact with asset-related data.
  ![image](https://github.com/user-attachments/assets/75e3db11-1c8c-44fa-b636-f907b5d99284)

- `POST /ingest` - Trigger data ingestion.
   ![image](https://github.com/user-attachments/assets/0777ef41-efa8-444e-b717-698ec661b514)

- `POST /compare` - Compare datasets.
  ![image](https://github.com/user-attachments/assets/9691d955-2e37-4ece-b152-4d54b0a6c1b6)

- `GET /metrics` - Retrieve performance metrics.
 ![image](https://github.com/user-attachments/assets/f7cd31e4-1273-4f04-bc86-23e4a056088e)

- `POST /summary` - Get data summaries.
  ![image](https://github.com/user-attachments/assets/533c191c-4241-4aa0-b3d4-b756a60add08)

- `DELETE /clear-db` - Clear the database records.
  ![image](https://github.com/user-attachments/assets/52bc2010-a180-4239-9c88-c1425b9b9616)


## MicroServices Architechture

![Microservices Arch](https://github.com/user-attachments/assets/24a54b0e-f61b-4bc9-a148-968a8e4bcb73)

