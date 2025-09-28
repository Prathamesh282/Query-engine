````markdown
# Synapse: AI Natural Language Query Engine

An intelligent, full-stack application that allows users to query a SQL database and unstructured documents using plain English. This project dynamically adapts to any database schema without hard-coding, leveraging a hybrid AI engine for comprehensive data retrieval.

### Live Demo

[Link to your 5-7 minute Loom video demonstration]

---

## Core Features

* **⚡ Dynamic Schema Discovery:** Automatically connects to any SQL database (PostgreSQL, MySQL, SQLite) and discovers its schema, including tables, columns, and relationships, without any prior configuration.
* **🧠 Hybrid AI Query Engine:** Utilizes a powerful local LLM (Ollama/Llama 3) for advanced Text-to-SQL generation and query classification ('SQL', 'DOCUMENT', or 'HYBRID').
* **📄 Document Search:** Ingests and indexes various document formats (PDF, DOCX, TXT) into a vector store for efficient semantic search.
* **🚀 Performance Optimized:** Implements an in-memory caching layer to provide sub-second responses for repeated queries, meeting the < 2s performance requirement.
* **🖥️ Interactive UI:** A clean, single-page web interface for connecting to data sources, uploading documents, and querying data in real-time.

## Tech Stack

* **Backend:** Python, FastAPI, SQLAlchemy, Uvicorn
* **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
* **AI / ML:** LiteLLM, Ollama (Llama 3), Sentence-Transformers, Faiss
* **Database:** SQLite (supports PostgreSQL, MySQL)

---

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Prerequisites

* **Git:** To clone the repository.
* **Python 3.8+:** For the backend server.
* **Ollama:** The project uses a local LLM. Please [download and install Ollama](https://ollama.com) and pull the required model:
    ```bash
    ollama pull llama3:8b
    ```

### 2. Clone the Repository

```bash
git clone <your-github-repository-url>
cd project
````

### 3\. Backend Setup

Set up the Python virtual environment and install dependencies.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r backend/requirements.txt
```

### 4\. Run the Backend Server

Make sure your **Ollama application is running** in the background. Then, start the FastAPI server from the root `project/` directory:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 5\. Frontend Setup

The frontend is a simple static file. No build step is required.

1.  Navigate to the `frontend/public/` directory.
2.  Open the `index.html` file in your web browser.

-----

## How to Use

1.  **Connect to Database:** In the UI, enter the database connection string (e.g., `sqlite:///company.db`) and click "Connect & Analyze". The discovered schema will appear.
2.  **Upload Documents:** Select or drag-and-drop `.pdf`, `.docx`, or `.txt` files into the upload area and click "Upload & Index".
3.  **Ask a Question:** Type a question in plain English into the query box and click "Process Query". The results from the database and/or documents will be displayed below, along with performance metrics.

## Known Limitations

  * **Text-to-SQL Complexity:** The LLM is highly capable but may struggle with extremely complex, multi-level JOIN queries.
  * **In-Memory Store:** The document vector store (FAISS) and query cache are stored in memory. They will be reset if the backend server restarts.
  * **UI Scalability:** The frontend is designed as a functional demo and does not include production features like user authentication or full pagination for extremely large result sets.
