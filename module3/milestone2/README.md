\# MLOps Milestone 2: Containerization \& CI/CD



!\[Build Status](https://github.com/ParthPatel0226/mlops-milestone2-cicd/actions/workflows/build.yml/badge.svg)



\## Overview



Production-ready ML inference service with automated CI/CD pipeline demonstrating:

\- Multi-stage Docker builds for optimized images

\- Automated testing with pytest

\- Container registry integration

\- Semantic versioning



\## Quick Start



\### Pull and Run the Container

```bash

\# Pull from GitHub Container Registry

docker pull ghcr.io/parthpatel0226/mlops-milestone2-cicd:latest



\# Run the container

docker run -p 5000:5000 ghcr.io/parthpatel0226/mlops-milestone2-cicd:latest

```



\### Test the Service

```bash

\# Health check

curl http://localhost:5000/health



\# Make prediction

curl -X POST http://localhost:5000/predict \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{"features": \[5.1, 3.5, 1.4, 0.2]}'

```



\## Local Development



\### Prerequisites

\- Python 3.11+

\- Docker

\- Git



\### Setup

```bash

\# Clone repository

git clone https://github.com/ParthPatel0226/mlops-milestone2-cicd.git

cd mlops-milestone2-cicd/module3/milestone2



\# Install dependencies

pip install -r app/requirements.txt



\# Run locally

python app/app.py



\# Run tests

pip install pytest

pytest tests/ -v

```



\### Build Docker Image Locally

```bash

\# Build

docker build -t ml-service:local .



\# Run

docker run -p 5000:5000 ml-service:local

```



\## CI/CD Pipeline



The GitHub Actions workflow automatically:

1\. ✅ Runs unit tests with pytest

2\. ✅ Builds multi-stage Docker image

3\. ✅ Pushes to GitHub Container Registry

4\. ✅ Tags with semantic versions



\*\*Triggered by:\*\*

\- Push to main/master branch

\- Version tags (v1.0.0, v1.1.0, etc.)

\- Pull requests



\## Project Structure

```

module3/milestone2/

├── .github/workflows/

│   └── build.yml          # CI/CD pipeline

├── app/

│   ├── app.py            # Flask inference service

│   ├── requirements.txt  # Pinned dependencies

│   └── model.pkl        # Trained ML model

├── tests/

│   └── test\_app.py      # Unit tests

├── Dockerfile           # Multi-stage build

├── .dockerignore       # Build optimization

├── README.md          # This file

└── RUNBOOK.md        # Operations guide

```



\## Image Optimization



\*\*Multi-stage build benefits:\*\*

\- Builder stage: 450MB

\- Runtime stage: 180MB

\- \*\*60% size reduction\*\*



\## Technologies



\- \*\*Python 3.11\*\* - Runtime

\- \*\*Flask 3.0.0\*\* - Web framework

\- \*\*scikit-learn 1.3.2\*\* - ML model

\- \*\*Docker\*\* - Containerization

\- \*\*GitHub Actions\*\* - CI/CD

\- \*\*GitHub Container Registry\*\* - Image storage



\## Author



\*\*Parth Patel\*\*  

MS in Management Information Systems  

University of Illinois Chicago

