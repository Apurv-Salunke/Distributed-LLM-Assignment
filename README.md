# Distributed LLM Assignment

This project implements a distributed system for interacting with large language models (LLMs). It consists of two main components:

1. **Python Service**: A service that interacts with Llama2 and Mistral models, maintains conversation history, and provides responses to user queries.
2. **Node.js Service**: A service that forwards queries to the Python service, retrieves conversation history, and provides endpoints for model selection and querying.

## Project Structure

```
distributed-llm/
│
├── python-service/
│   ├── app.py
│   ├── Dockerfile
│   ├── .env
│   ├── requirements.txt
│   └── README.md
│
├── node-service/
│   ├── src/
│   │   ├── routes/
│   │   │   └── api.ts
│   │   └── index.ts
│   ├── .env
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
└── docker-compose.yml
```

## Python Service

### Features

1. **Model Selection**: Allows selecting between Llama2 and Mistral models.
2. **Query Processing**: Sends user queries to the selected model and maintains conversation context.
3. **Conversation History**: Stores and provides access to conversation history.

### Setup

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` File:**

   Add your Hugging Face API key to the `.env` file:

   ```
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   ```

3. **Run the Service:**

   ```bash
   python app.py
   ```

4. **Dockerize the Service:**

   ```bash
   docker build -t python-service .
   ```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### `requirements.txt`

```
fastapi
pydantic
langchain_huggingface
python-dotenv
uvicorn
```

## Node.js Service

### Features

1. **Model Selection**: Forwards model selection requests to the Python service.
2. **Query Forwarding**: Sends queries to the Python service and retrieves responses.
3. **Conversation History**: Retrieves and lists conversation history from the Python service.

### Setup

1. **Install Dependencies:**

   ```bash
   npm install
   ```

2. **Create `.env` File:**

   Add the Python service URL to the `.env` file:

   ```
   PYTHON_SERVICE_URL=http://localhost:8000
   PORT=3000
   ```

3. **Run the Service:**

   ```bash
   npm start
   ```

4. **Dockerize the Service:**

   ```bash
   docker build -t node-service .
   ```

### Dockerfile

```dockerfile
FROM node:16

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
```

### `package.json`

```json
{
  "name": "node-service",
  "version": "1.0.0",
  "main": "src/index.ts",
  "scripts": {
    "start": "ts-node src/index.ts"
  },
  "dependencies": {
    "axios": "^0.21.1",
    "express": "^4.17.1"
  },
  "devDependencies": {
    "@types/express": "^4.17.11",
    "@types/node": "^14.14.31",
    "typescript": "^4.1.2",
    "ts-node": "^9.1.1"
  }
}
```

## Docker Compose

To run both services together, use Docker Compose.

### `docker-compose.yml`

```yaml
version: '3'

services:
  python-service:
    build:
      context: ./python-service
    ports:
      - "8000:8000"

  node-service:
    build:
      context: ./node-service
    ports:
      - "3000:3000"
    depends_on:
      - python-service
```

### Running with Docker Compose

```bash
docker-compose up --build
```

## Endpoints

### Python Service

- **Select Model**: `POST /select_model`
  - Body: `{ "model": "meta-llama/Llama-2-7b-chat-hf" }`
  - Description: Selects the model to use.

- **Query**: `POST /query`
  - Body: `{ "prompt": "Who won the Cricket World Cup in 2011?" }`
  - Description: Sends a query to the selected model and returns the response.

- **Conversation History**: `GET /conversation_history`
  - Description: Retrieves the conversation history.

### Node.js Service

- **Select Model**: `POST /api/select_model`
  - Body: `{ "model": "meta-llama/Llama-2-7b-chat-hf" }`
  - Description: Forwards model selection request to the Python service.

- **Query**: `POST /api/query`
  - Body: `{ "prompt": "Who won the Cricket World Cup in 2011?" }`
  - Description: Forwards query to the Python service and retrieves the response.

- **Conversation History**: `GET /api/conversation_history`
  - Description: Retrieves conversation history from the Python service.

## Testing

Use `curl` commands to test the endpoints:

1. **Select Model:**

   ```bash
   curl -X POST http://localhost:3000/api/select_model \
        -H "Content-Type: application/json" \
        -d '{"model": "meta-llama/Llama-2-7b-chat-hf"}'
   ```

2. **Send Query:**

   ```bash
   curl -X POST http://localhost:3000/api/query \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Who won the Cricket World Cup in the year 2011?"}'
   ```

3. **Get Conversation History:**

   ```bash
   curl -X GET http://localhost:3000/api/conversation_history
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

This `README.md` provides a comprehensive overview of the project, including setup instructions, Docker configuration, and API usage. Adjust paths and other details as needed for your specific setup.