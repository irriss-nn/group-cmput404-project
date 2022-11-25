# syntax=docker/dockerfile:1
FROM python:3.10-alpine

LABEL name="CMPUT404-Social"
LABEL description="Hosts the FastAPI backend of CMPUT404-Social"

WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy server files
COPY . .

# Run server to accept all connections on port 80
EXPOSE 80
ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host=0.0.0.0", "--port=80"]
