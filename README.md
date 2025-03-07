# Research Paper Processor for RAG Pipeline

This application helps you process research paper PDFs for a Retrieval-Augmented Generation (RAG) pipeline by:

1. Extracting text from PDF files
2. Using GPT-4o-mini to identify paper metadata (title, authors, abstract, etc.)
3. Chunking content into appropriate segments
4. Generating embeddings using OpenAI's embedding model
5. Storing both text and embeddings in MongoDB Atlas for later retrieval

## Features

- Upload and process multiple PDF files at once
- Extract metadata from research papers (title, authors, publication year, etc.)
- Structure content into meaningful sections
- Generate text embeddings for vector search
- Store processed data in MongoDB Atlas vector database

## Setup

1. **Clone this repository**

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   MONGO_USERNAME=your_mongodb_username
   MONGO_PASSWORD=your_mongodb_password
   MONGO_URI=your_mongodb_connection_string
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the application**
   ```
   python app.py
   ```
   The application will run on http://localhost:5000/

## Usage

1. Open your browser and go to http://localhost:5000/
2. Upload one or more PDF files using the file upload form
3. The application will process each PDF file:
   - Extract text content
   - Identify metadata
   - Split into chunks
   - Generate embeddings
   - Store in MongoDB
4. View the processing results

## Project Structure

```
.
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── main.js
│   ├── templates/
│   │   └── index.html
│   └── utils/
│       ├── mongo_utils.py
│       ├── pdf_processor.py
│       └── text_extractor.py
├── uploads/
├── .env
├── app.py
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.7+
- MongoDB Atlas account
- OpenAI API key

## License

MIT
