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



RUN git clone https://github.com/streamlit/streamlit-example.git .



# Expose Streamlit port
EXPOSE 8501

# Set environment variables with defaults
ENV PDF_DIR=/data/pdfs
ENV MARKDOWN_DIR=/data/extracted
ENV PAGE_SCORES_CSV=/data/output/page_scores_full.csv
ENV METADATA_PKL=/data/output/metadata_openalex\(silver\).pkl

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"] 