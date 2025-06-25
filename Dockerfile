# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Define build arguments with defaults
ARG PDF_DIR=/workspace/data/pdfs
ARG MARKDOWN_DIR=/workspace/data/extracted
ARG PAGE_SCORES_CSV=/workspace/data/page_scores_full.csv
ARG METADATA_PKL=/workspace/data/metadata_openalex\(silver\).pkl

RUN git clone https://github.com/odoma-ch/pdf_benchmark_dashboard.git .

RUN pip3 install -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Set environment variables from build args (can be overridden at runtime)
ENV PDF_DIR=${PDF_DIR}
ENV MARKDOWN_DIR=${MARKDOWN_DIR}
ENV PAGE_SCORES_CSV=${PAGE_SCORES_CSV}
ENV METADATA_PKL=${METADATA_PKL}

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
# add server.enableCORS=false and server.enableXsrfProtection=false to disable CORS and CSRF protection
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"] 