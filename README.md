# Financial Document Entity Extractor

This project is a web application designed to extract key financial entities from uploaded documents (.pdf, .docx, .txt). It uses a FastAPI backend for document processing and a Streamlit frontend for the user interface.

## Features

- **File Upload**: Supports PDF, DOCX, and plain text documents
- **Entity Extraction**: Uses regex and other pipeline methods to extract financial data
- **Interactive UI**: A Streamlit dashboard to upload files and view extracted results
- **Q&A on PDFs**: Allows users to ask specific questions about the content of uploaded PDF documents

## Project Structure

The project is organized into a backend (`app`) and a frontend (`frontend`) directory, ensuring a clean separation of concerns.

```
.
├── app/
│   ├── api/              # FastAPI endpoint definitions
│   ├── pipelines/        # Extraction pipelines (PDF, NER, Regex)
│   └── utils/            # Utility functions (e.g., file type detection)
├── frontend/
│   └── app.py            # The Streamlit application code
├── .env                  # Environment variables (API keys, etc.) - ignored by git
├── main.py               # Main FastAPI application entry point
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/SamarthKumbar/Entity-Extractor.git
cd <your-project-directory>
```

### 2. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scriptsctivate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages from the requirements.txt file.

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a file named `.env` in the root directory of the project. This file will hold your secret keys and configurations. Add any necessary API keys or configuration variables here.

Example `.env` file:

```env
# .env
SOME_API_KEY="your_api_key_here"
```

## Usage

You need to run the backend (FastAPI) and the frontend (Streamlit) in separate terminal sessions.

### 1. Run the Backend (FastAPI)

Open a terminal, activate your virtual environment, and run the following command from the project's root directory:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Parameters explanation:**
- `main:app`: Tells uvicorn to look for an object named `app` in the `main.py` file
- `--host 0.0.0.0`: Makes the server accessible on your local network
- `--port 8001`: Runs the server on port 8001
- `--reload`: The server will automatically restart when you make changes to the code

The API will be available at http://localhost:8001. You can view the auto-generated documentation at http://localhost:8001/docs.

### 2. Run the Frontend (Streamlit)

Open a second terminal, activate the same virtual environment, and run the Streamlit app:

```bash
streamlit run frontend/app.py
```

Your web browser should automatically open a new tab with the application running. If not, you can access it at http://localhost:8501.

## API Endpoints

The FastAPI backend provides the following endpoints:

- `POST /api/upload` - Upload and process documents
- `POST /api/ask_pdf` - Ask questions about uploaded PDF documents
- `GET /docs` - Interactive API documentation


