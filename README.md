# TDS Virtual Teaching Assistant

A Retrieval-Augmented Question Answering (RAG) API built for the IIT Madras Tools in Data Science (TDS) course. The system answers student queries using course content and Discourse discussion data through semantic search and vector retrieval.

## Overview

Students often need quick access to relevant course material and discussion threads. This project provides a Virtual Teaching Assistant that retrieves the most relevant information from indexed TDS course resources and Discourse posts.

The API also supports image-based questions by extracting text from uploaded screenshots using Optical Character Recognition (OCR).

## Features

* Semantic search using Sentence Transformers
* Vector similarity search with FAISS
* FastAPI-based REST API
* OCR support for screenshot-based questions
* Retrieval of relevant Discourse references
* Serverless deployment using Mangum and Vercel
* External storage of vector index and chunked data

## Tech Stack

| Component        | Technology       |
| ---------------- | ---------------- |
| API Framework    | FastAPI          |
| Vector Search    | FAISS            |
| Embeddings       | all-MiniLM-L6-v2 |
| OCR              | Tesseract OCR    |
| Image Processing | Pillow           |
| Deployment       | Vercel + Mangum  |
| Language         | Python           |

## Project Architecture

```text
User Question
      │
      ▼
FastAPI Endpoint
      │
      ▼
OCR (Optional)
      │
      ▼
Sentence Transformer
      │
      ▼
Query Embedding
      │
      ▼
FAISS Vector Search
      │
      ▼
Top Relevant Chunks
      │
      ▼
Answer + Discussion Links
```

## How It Works

### 1. Knowledge Base Creation

Course content and Discourse discussions are collected and divided into smaller text chunks.

### 2. Embedding Generation

Each chunk is converted into a dense vector representation using:

```python
all-MiniLM-L6-v2
```

### 3. Vector Indexing

The embeddings are stored inside a FAISS vector index for efficient similarity search.

### 4. Query Processing

When a student submits a question:

* The question is embedded
* Similar chunks are retrieved from FAISS
* The most relevant chunk is returned as the answer
* Related Discourse links are included when available

### 5. Screenshot Support

If a screenshot is uploaded:

* Text is extracted using Tesseract OCR
* Extracted text is appended to the user's query
* Retrieval proceeds normally

## API Endpoint

### POST `/api/`

Request:

```json
{
  "question": "What is cosine similarity?",
  "image": null
}
```

Response:

```json
{
  "answer": "...",
  "links": [
    {
      "url": "...",
      "text": "..."
    }
  ]
}
```

### GET `/api/`

Health Check:

```json
{
  "message": "TDS Virtual TA is live!"
}
```

## Deployment

The project is deployed using:

* FastAPI
* Mangum
* Vercel Serverless Functions

Large artifacts such as the FAISS index and chunk database are hosted externally and downloaded at runtime.

## Repository Structure

```text
.
├── main.py
├── index.py
├── requirements.txt
├── vector.index
├── chunks.json
└── README.md
```

## Skills Demonstrated

* Retrieval-Augmented Generation (RAG) concepts
* Semantic Search
* Vector Databases
* Information Retrieval
* OCR Integration
* REST API Development
* FastAPI
* Serverless Deployment
* Data Processing

## Future Improvements

* Hybrid keyword + semantic retrieval
* Cross-encoder reranking
* Response generation using LLMs
* Conversation memory
* Confidence scoring
* Automated index update pipeline

## Author

Kriti Srivastava

Built as part of the IIT Madras Online Degree Program – Tools in Data Science Project.
(scraped from: https://discourse.onlinedegree.iitm.ac.in/search?q=%23courses%3Atds-kb&page=1)
