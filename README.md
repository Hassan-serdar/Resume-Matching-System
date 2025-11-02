# Resume-Matching-System

# CV-JD Matcher: Job Description to Resume Similarity Analyzer

##  Project Overview

This project is a Flask web application designed to help recruiters and hiring managers automate the initial screening of resumes.

The application takes one **Job Description (JD)** and a batch of **Resumes (CVs)** (in `.pdf`, `.docx`, or `.txt` format) and ranks them based on their relevance to the JD. It calculates a similarity score for each resume, allowing recruiters to instantly identify the most promising candidates.

## Core Logic & Methodology

The matching logic is built on a classic NLP information retrieval technique:

1.  **File Upload & Text Extraction:**
    * A **Flask** server provides a web interface (index.html) to accept a job description (text) and multiple resume file uploads.
    * Uploaded files are temporarily saved to an `/uploads` folder.
    * Text is extracted from different file types using:
        * `PyMuPDF (fitz)` for `.pdf` files.
        * `docx2txt` for `.docx` files.
        * Standard Python I/O for `.txt` files.

2.  **Text Vectorization (TF-IDF):**
    * The job description and all resume texts are placed into a single corpus.
    * `sklearn.feature_extraction.text.TfidfVectorizer` is used to convert this corpus into a matrix of TF-IDF features, effectively turning each document into a numerical vector.
    * This method gives higher weight to terms that are important to the specific document (like "Flask", "API") and lower weight to common words (like "the", "and", "experience").

3.  **Similarity Calculation (Cosine Similarity):**
    * `sklearn.metrics.pairwise.cosine_similarity` is used to calculate the similarity (the cosine of the angle) between the job description's vector and every resume vector.
    * A score of `1.0` means a perfect match, while a score of `0.0` means no similarity.

4.  **Ranking & Display:**
    * The application sorts the resumes by their similarity score in descending order.
    * The results (filename and score) are passed back to the `index.html` template and displayed to the user.
    * The uploaded resume files are deleted from the server after processing to save space.

##  Technologies & Libraries Used

* **Language:** Python
* **Web Framework:** Flask
* **NLP/ML:** Scikit-learn
    * `TfidfVectorizer`
    * `cosine_similarity`
* **Text Extraction:**
    * `PyMuPDF (fitz)`
    * `docx2txt`
* **Standard Libraries:** `os`, `werkzeug`

##  How to Run

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPO_LINK]
    cd [YOUR_REPO_NAME]
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required libraries:**
    *You must create a `requirements.txt` file for this.*
    ```bash
    pip install Flask PyMuPDF docx2txt scikit-learn
    pip freeze > requirements.txt
    ```

4.  **Create the Frontend:**
    * This project requires an `index.html` file inside a folder named `templates`.
    * Create a `templates/` folder and place your `index.html` file inside it. (The HTML should contain a form with `method="POST"`, a `textarea` with `name="job_description"`, and a file input with `name="resumes" multiple`).

5.  **Run the application:**
    ```bash
    python main.py
    ```
    Open your browser and go to `http://127.0.0.1:5000/`.
