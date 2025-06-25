import streamlit as st
import pandas as pd
import os
from pathlib import Path

# --- Global Path Configuration ---
# Get the absolute path of the current script
PROJECT_ROOT = Path(__file__).resolve().parent

# Get paths from environment variables with fallbacks to defaults
PDF_DIR_DEFAULT = os.getenv('PDF_DIR', str('/Users/alex/docs/code/Odoma/pdf_extract_benchmark/resources/gotriple_pdfs'))
MARKDOWN_DIR_DEFAULT = os.getenv('MARKDOWN_DIR', str('/Users/alex/docs/code/Odoma/pdf_extract_benchmark/resources/extracted'))
PAGE_SCORES_CSV_DEFAULT = os.getenv('PAGE_SCORES_CSV', str(PROJECT_ROOT / "data" / "page_scores_full.csv"))
METADATA_PKL_DEFAULT = os.getenv('METADATA_PKL', str(PROJECT_ROOT / "data" / "metadata_openalex(silver).pkl"))

# Initialize session state for paths if not already set
# if 'overall_scores_csv' not in st.session_state:
#     st.session_state.overall_scores_csv = str(OVERALL_SCORES_CSV_DEFAULT)
if 'page_scores_csv' not in st.session_state:
    st.session_state.page_scores_csv = PAGE_SCORES_CSV_DEFAULT
if 'metadata_pkl' not in st.session_state:
    st.session_state.metadata_pkl = METADATA_PKL_DEFAULT
if 'pdf_dir' not in st.session_state: # Renamed from pdf_path to pdf_dir for clarity
    st.session_state.pdf_dir = PDF_DIR_DEFAULT
if 'markdown_dir' not in st.session_state:
    st.session_state.markdown_dir = MARKDOWN_DIR_DEFAULT


# Set page config
st.set_page_config(
    page_title="PDF Extraction Benchmark Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .intro-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
        border-left: 5px solid #1f77b4;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #666;
        text-align: center;
        padding: 10px;
        font-size: 0.9rem;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Main title and introduction
st.markdown('<div class="main-header">📊 PDF Extraction Benchmark Dashboard</div>', unsafe_allow_html=True)



# Introduction section
st.markdown("""
<div class="intro-section">
    <h2>🔍 About This Benchmark</h2>
    <p>
        Welcome to the PDF Extraction Benchmark Dashboard! This tool provides comprehensive analysis and comparison 
        of different PDF text extraction methods across various academic disciplines and document types.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📋 What You Can Do:")
st.markdown("""
- **📈 Overall Results:** View performance metrics and compare extraction methods across all documents
- **📄 PDF Viewer:** Examine individual PDFs and their extracted markdown content side-by-side  
- **🔍 Filter & Search:** Filter results by discipline, score thresholds, and search specific documents
- **📊 Visualizations:** Interactive charts showing score distributions and performance by discipline
""")

st.markdown("### 📊 Understanding the Quality Scores:")
st.markdown("""
Each extracted text is evaluated using an LLM judge across five key criteria, each scored from 0 to 1:

- **Line Continuity (0-1):** How well sentences flow without inappropriate breaks or hyphenation issues
- **Paragraph Integrity (0-1):** Clear paragraph boundaries with proper spacing between paragraphs  
- **Content Sequencing (0-1):** Text follows logical reading order (especially important for multi-column documents)
- **Layout Separation (0-1):** Headers/footers properly separated from main content (not mixed into body text)
- **Text Completeness (0-1):** No missing content, truncated sentences, or information gaps

**Overall Score:** The average of all five criteria. Higher scores indicate better extraction quality, with 1.0 being perfect and 0.0 indicating severe extraction issues.

Use the sidebar navigation to explore different sections of the dashboard. Click on any row in the results table to view the original PDF and its extracted content.
""")

# Initialize session state
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None
if 'selected_row_data' not in st.session_state: 
    st.session_state.selected_row_data = None


# --- Path Configuration UI ---
st.markdown("### 📁 Path Configuration")
st.write("Review and update the default paths for data files and directories.")

# PDF Directory Path
new_pdf_dir = st.text_input(
    "PDF Directory Path",
    value=st.session_state.pdf_dir,
    help="Absolute path to the root directory containing PDF files (e.g., .../resources/gotriple_pdfs)."
)
if new_pdf_dir != st.session_state.pdf_dir:
    st.session_state.pdf_dir = new_pdf_dir
    st.success(f"PDF directory path updated to: {new_pdf_dir}")

# Markdown Directory Path
new_markdown_dir = st.text_input(
    "Markdown Directory Path",
    value=st.session_state.markdown_dir,
    help="Absolute path to the root directory containing extracted Markdown files (e.g., .../resources/extracted)."
)
if new_markdown_dir != st.session_state.markdown_dir:
    st.session_state.markdown_dir = new_markdown_dir
    st.success(f"Markdown directory path updated to: {new_markdown_dir}")

st.markdown("##### CSV and Pickle File Paths")

# Overall Scores CSV Path
# new_overall_scores_csv = st.text_input(
#     "Overall Scores CSV Path",
#     value=st.session_state.overall_scores_csv,
#     help="Absolute path to the overall scores CSV file (e.g., .../output/pdf_scores_lt15_en.csv)."
# )
# if new_overall_scores_csv != st.session_state.overall_scores_csv:
#     st.session_state.overall_scores_csv = new_overall_scores_csv
#     st.success(f"Overall scores CSV path updated to: {new_overall_scores_csv}")

# Page Scores CSV Path
new_page_scores_csv = st.text_input(
    "Page Scores CSV Path",
    value=st.session_state.page_scores_csv,
    help="Absolute path to the page scores CSV file (e.g., .../output/page_scores_lt15_en.csv)."
)
if new_page_scores_csv != st.session_state.page_scores_csv:
    st.session_state.page_scores_csv = new_page_scores_csv
    st.success(f"Page scores CSV path updated to: {new_page_scores_csv}")

# Metadata PKL Path
new_metadata_pkl = st.text_input(
    "Metadata PKL Path",
    value=st.session_state.metadata_pkl,
    help="Absolute path to the metadata PKL file (e.g., .../output/metadata_openalex(silver).pkl)."
)
if new_metadata_pkl != st.session_state.metadata_pkl:
    st.session_state.metadata_pkl = new_metadata_pkl
    st.success(f"Metadata PKL path updated to: {new_metadata_pkl}")

st.markdown("---") # Visual separator