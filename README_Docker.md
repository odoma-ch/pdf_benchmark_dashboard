# Dockerized Streamlit Dashboard

This directory contains the dockerized version of the PDF Extraction Benchmark Dashboard.

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the dashboard:**
   Open your browser and go to `http://localhost:8501`

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -f src/dashboard/Dockerfile -t pdf-dashboard .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 \
     -v $(pwd)/resources/gotriple_pdfs:/data/pdfs:ro \
     -v $(pwd)/resources/extracted:/data/extracted:ro \
     -v $(pwd)/output:/data/output:ro \
     pdf-dashboard
   ```

## Configuration

### Environment Variables

The following environment variables can be used to configure the application:

- `PDF_DIR`: Path to the directory containing PDF files (default: `/data/pdfs`)
- `MARKDOWN_DIR`: Path to the directory containing extracted markdown files (default: `/data/extracted`)
- `PAGE_SCORES_CSV`: Path to the page scores CSV file (default: `/data/output/page_scores_full.csv`)
- `METADATA_PKL`: Path to the metadata pickle file (default: `/data/output/metadata_openalex(silver).pkl`)

### Custom Configuration

To use custom paths, you can:

1. **Modify docker-compose.yml:**
   ```yaml
   environment:
     - PDF_DIR=/custom/path/to/pdfs
     - MARKDOWN_DIR=/custom/path/to/extracted
     - PAGE_SCORES_CSV=/custom/path/to/scores.csv
     - METADATA_PKL=/custom/path/to/metadata.pkl
   ```

2. **Use environment file:**
   Create a `.env` file:
   ```
   PDF_DIR=/custom/path/to/pdfs
   MARKDOWN_DIR=/custom/path/to/extracted
   PAGE_SCORES_CSV=/custom/path/to/scores.csv
   METADATA_PKL=/custom/path/to/metadata.pkl
   ```

## Data Directory Structure

The application expects the following directory structure:

```
project_root/
├── resources/
│   ├── gotriple_pdfs/     # PDF files
│   └── extracted/         # Extracted markdown files
├── output/
│   ├── page_scores_full.csv
│   └── metadata_openalex(silver).pkl
└── src/dashboard/
    ├── app.py
    └── pages/
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change the port in docker-compose.yml
   ports:
     - "8502:8501"  # Use port 8502 instead
   ```

2. **Permission denied on mounted volumes:**
   ```bash
   # Ensure the directories exist and have proper permissions
   mkdir -p resources/gotriple_pdfs resources/extracted output
   chmod 755 resources/gotriple_pdfs resources/extracted output
   ```

3. **Data files not found:**
   - Check that the data files exist in the expected locations
   - Verify the environment variables are set correctly
   - Ensure the volume mounts are working properly

### Logs

To view application logs:
```bash
docker-compose logs -f streamlit-dashboard
```

### Health Check

The application includes a health check that can be monitored:
```bash
docker-compose ps
```

## Development

### Building for Development

1. **Build with development dependencies:**
   ```bash
   docker build -f src/dashboard/Dockerfile -t pdf-dashboard:dev .
   ```

2. **Run with volume mounts for live code changes:**
   ```bash
   docker run -p 8501:8501 \
     -v $(pwd)/src/dashboard:/app/dashboard \
     -v $(pwd)/resources/gotriple_pdfs:/data/pdfs:ro \
     -v $(pwd)/resources/extracted:/data/extracted:ro \
     -v $(pwd)/output:/data/output:ro \
     pdf-dashboard:dev
   ```

### Adding New Dependencies

1. Update `requirements.txt` in the project root
2. Rebuild the Docker image:
   ```bash
   docker-compose build --no-cache
   ```

## Production Deployment

For production deployment, consider:

1. **Using a reverse proxy (nginx)**
2. **Setting up SSL/TLS certificates**
3. **Implementing proper logging**
4. **Using Docker secrets for sensitive data**
5. **Setting up monitoring and alerting**

Example production docker-compose.yml:
```yaml
version: '3.8'

services:
  streamlit-dashboard:
    build:
      context: .
      dockerfile: src/dashboard/Dockerfile
    ports:
      - "8501:8501"
    volumes:
      - ./resources/gotriple_pdfs:/data/pdfs:ro
      - ./resources/extracted:/data/extracted:ro
      - ./output:/data/output:ro
    environment:
      - PDF_DIR=/data/pdfs
      - MARKDOWN_DIR=/data/extracted
      - PAGE_SCORES_CSV=/data/output/page_scores_full.csv
      - METADATA_PKL=/data/output/metadata_openalex(silver).pkl
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
``` 