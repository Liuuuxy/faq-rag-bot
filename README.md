# Highrise FAQ Chatbot

A real-time streaming chatbot built with FastAPI, LangChain, and Google's Generative AI that provides answers to Highrise-related questions using vector search and RAG (Retrieval Augmented Generation).

## Overview

This chatbot application combines advanced NLP capabilities with efficient vector search to provide accurate, context-aware responses to user queries about Highrise. The system uses streaming responses for a smooth user experience and maintains conversation logs for analysis.

## Features

- **Real-time Streaming Responses**: Implements the Vercel AI SDK's Data Stream Protocol
- **Vector Search**: Uses MongoDB Atlas Vector Search for efficient information retrieval
- **RAG Architecture**: Combines retrieved context with Google's Generative AI for accurate responses
- **Conversation Logging**: Tracks user interactions and response quality
- **Web Interface**: Modern React-based UI with real-time message updates

## Data Collection

`data_extraction.py`

A Python script that automates the collection of FAQ data:

- Scrapes FAQ content from Highrise support pages
- Processes and structures the data
- Outputs formatted JSON to `faq_data.json`
- Handles rate limiting and error recovery
- Maintains data schema consistency

Usage:

```bash
python data_extraction.py
```

## Demo

### Video Recording

<iframe width="560" height="315"
src="https://www.youtube.com/embed/DzP6Z43PDPw" 
frameborder="0" 
allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
allowfullscreen></iframe>

_Demo showing local development setup with real-time streaming responses_

### Notebook

`test.ipynb`

A Jupyter notebook for testing and development:

- Tests vector store initialization
- Validates RAG chain functionality
- Demonstrates chatbot response quality
- Provides example queries and responses
- Helps tune retrieval parameters

The notebook serves as both documentation and a development tool for:

- Testing different embedding models
- Adjusting chunk sizes and overlap
- Fine-tuning prompt templates
- Validating response quality

## Known Issues

### Vercel Deployment Size Limitation

This project currently cannot be deployed to Vercel's free tier due to exceeding the 250MB unzipped function size limit:

```
Error: A Serverless Function has exceeded the unzipped maximum size of 250 MB
```

## Architecture

### System Components

1. **Frontend**

   - React.js with Next.js
   - Vercel AI SDK for streaming chat interface
   - Tailwind CSS for styling

2. **Backend**

   - FastAPI for API endpoints
   - LangChain for RAG implementation
   - Google Generative AI (Gemini) for text generation
   - MongoDB Atlas for vector storage

3. **Key Features**
   - Streaming response generation
   - Context-aware answer synthesis
   - Conversation history tracking
   - Error handling and logging

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB Atlas account
- Google Cloud Platform account with API access

## Installation

1. **Clone the Repository**

```bash
git clone <repository-url>
cd <project-directory>
```

2. **Set Environment Variables**

```bash
GOOGLE_API_KEY=your_google_api_key
MONGODB_ATLAS_CLUSTER_URI=your_mongodb_connection_string
```

3. **Install Backend Dependencies**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r [requirements.txt](http://_vscodecontentref_/1)
```

4. **Install Frontend Dependencies**

```bash
npm install
```

## Running the Application

```bash
pnmp dev
```

The application will be available at `http://localhost:3000`

## API Endpoints

- `POST /api/chat`: Main chat endpoint that handles message streaming
- `GET /logs`: Retrieve interaction logs

## Configuration

### Vector Store Setup

The system uses MongoDB Atlas Vector Search with the following configuration:

- Database: `langchain_faq_db`
- Collection: `langchain_faq_vectorstores`
- Index: `langchain-faq-index-vectorstores`

### Model Configuration

- Chat Model: `gemini-1.5-flash`
- Embeddings Model: `models/text-embedding-004`
- Temperature: 0 (for consistent, factual responses)

## Special Considerations

1. Security

- API keys should be properly secured
- CORS configuration for production

2. Performance

- Vector search is optimized for quick retrieval
- Streaming responses reduce perceived latency

## Deployment

1. Backend Deployment

   - Can be deployed on any Python-supporting platform
   - Vercel recommended
   - Ensure environment variables are properly set

2. Frontend Deployment

   - Optimized for Vercel deployment
   - Can be deployed to any static hosting service
   - Configure API endpoint URLs for production

#### Workarounds

1. **Alternative Deployment Options:**

   - Deploy backend separately on platforms like:
     - Heroku
     - Google Cloud Run
     - etc.

2. **Size Optimization (if still using Vercel):**

   - Optimize dependencies
   - Split into smaller functions
   - Use edge functions where possible

3. **Paid Solutions:**
   - Upgrade to Vercel Pro tier
   - Use dedicated server hosting

For more details on Vercel function size limits and solutions, see:

- [Vercel Discussion #4354](https://github.com/orgs/vercel/discussions/4354)
- [Vercel Serverless Functions Documentation](https://vercel.com/docs/functions/serverless-functions)
