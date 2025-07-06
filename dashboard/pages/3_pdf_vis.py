import streamlit as st
import pandas as pd
from pathlib import Path
import base64
import os

# Configure page to use wide layout
st.set_page_config(page_title="PDF & Markdown Viewer", layout="wide")

# Initialize session state variables
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None
if 'selected_row_data' not in st.session_state:
    st.session_state.selected_row_data = None
if 'selected_pdf_file' not in st.session_state:
    st.session_state.selected_pdf_file = None
if 'selected_markdown_file' not in st.session_state:
    st.session_state.selected_markdown_file = None

# Page title
st.markdown('<div class="main-header">📄 PDF & Markdown Viewer</div>', unsafe_allow_html=True)

def display_pdf(file_path):
    """Display PDF in Streamlit using an embedded iframe"""
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        # Embed PDF in HTML
        pdf_display = f'''
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" height="600" type="application/pdf">
        </iframe>
        '''
        return pdf_display
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")
        return None

def load_markdown_content(filename, tool, discipline):
    """Load markdown content for a specific tool"""
    try:
        # Look for markdown files in the output/test directory
        # md_path = Path(f"resources/extracted/{tool}/{discipline}/{filename}_{tool}.md") # Old path
        base_md_path = Path(st.session_state.markdown_dir)
        md_path = base_md_path / tool / discipline / f"{filename}_{tool}.md"

        if md_path.exists():
            with open(md_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # # Alternative path pattern
        # alt_path = Path(f"output/test/{filename.replace('extracted_', '')}_{tool}.md")
        # if alt_path.exists():
        #     with open(alt_path, 'r', encoding='utf-8') as f:
        #         return f.read()
        
        return None
    except KeyError as e:
        st.error(f"Path key 'markdown_dir' not found in session state: {e}. Ensure it's initialized in app.py.")
        return None
    except Exception as e:
        st.error(f"Error loading {tool} markdown: {str(e)}")
        return None

def find_pdf_file(filename, discipline):
    """Find PDF file in the examples directory"""
    try:
        # Remove 'extracted_' prefix if present
        # clean_filename = filename.replace('extracted_', '') if filename.startswith('extracted_') else filename
        
        # Look in examples directory
        # pdf_path = Path(f"resources/gotriple_pdfs/{discipline}/{filename}.pdf") # Old path
        base_pdf_path = Path(st.session_state.pdf_dir)
        pdf_path = base_pdf_path / discipline / f"{filename}.pdf"

        # print(pdf_path)
        if pdf_path.exists():
            return pdf_path
    
        
        return None
    except KeyError as e:
        st.error(f"Path key 'pdf_dir' not found in session state: {e}. Ensure it's initialized in app.py.")
        return None
    except Exception as e:
        st.error(f"Error finding PDF: {str(e)}")
        return None

# Check if a file is selected
if not st.session_state.selected_file or not st.session_state.selected_row_data:
    st.info("👆 You can select documents from the 'Results Overview' page, and select a tool to view the PDF and Markdown.")

# Display selected file information if available
if st.session_state.selected_file and st.session_state.selected_row_data:
    filename = st.session_state.selected_file
    row_data = st.session_state.selected_row_data

    st.success(f"📁 Viewing: **{filename}**")

    # Show metadata if available
    if row_data:
        st.subheader("📊 Document Metadata")
        
        # Create columns for metadata display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Discipline' in row_data:
                st.metric("Discipline", row_data['Discipline'])
            if 'Overall Score Pymupdf' in row_data:
                st.metric("PyMuPDF Score", f"{row_data['Overall Score Pymupdf']:.3f}")
        
        with col2:
            if 'Overall Score Marker' in row_data:
                st.metric("Marker Score", f"{row_data['Overall Score Marker']:.3f}")
            if 'Word Count Pymupdf' in row_data:
                st.metric("PyMuPDF Words", f"{int(row_data['Word Count Pymupdf']):,}")
        
        with col3:
            if 'Overall Score Mineru' in row_data:
                st.metric("MinerU Score", f"{row_data['Overall Score Mineru']:.3f}")
            if 'Word Count Marker' in row_data:
                st.metric("Marker Words", f"{int(row_data['Word Count Marker']):,}")
    else:
        st.subheader("📊 Document Metadata")
        st.info("ℹ️ Document metadata is not available. Please select a document from the 'Results Overview' page to view detailed metrics and scores.")


# Tool selection
extraction_tools = ['marker', 'pymupdf', 'mineru']
selected_tool = st.selectbox(
    "Select extraction tool:",
    extraction_tools,
    key="tool_selector"
)
        

# Main content area with PDF and markdown side by side
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 PDF Preview")
    
    if st.session_state.selected_file and st.session_state.selected_row_data:
        # Fallback to resources directory
        
        filename = st.session_state.selected_file
        row_data = st.session_state.selected_row_data
        
        pdf_path = find_pdf_file(filename, row_data.get('Discipline', 'Unknown'))
        if pdf_path:
            st.info(f"📁 Current file: {pdf_path}")
            pdf_html = display_pdf(pdf_path)
            if pdf_html:
                st.markdown(pdf_html, unsafe_allow_html=True)
            else:
                st.error("Failed to display PDF")
        else:
            st.warning(f"PDF file not found for: {filename}, current path: {pdf_path}")
    else:
        st.info("Please select a PDF file above or from the Results Overview page")

with col2:
    st.subheader("📝 Extracted Markdown")
    
    if st.session_state.selected_file and st.session_state.selected_row_data:
        # Fallback to extracted markdown from resources
        filename = st.session_state.selected_file
        row_data = st.session_state.selected_row_data
        
        
        # Load and display markdown content
        markdown_content = load_markdown_content(filename, selected_tool, row_data['Discipline'])
        
        if markdown_content:
            # Show current file path
            md_path = Path(f"resources/extracted/{selected_tool}/{row_data['Discipline']}/{filename}_{selected_tool}.md")
            st.info(f"📁 Current file: {md_path}")
            
            print(f"md path: {md_path}")
            
            # Display markdown content in a scrollable container
            st.markdown("**Markdown Content:**")
            st.markdown(
                f"""
                <div style="height: 500px; overflow-y: scroll; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">
                    <pre style="white-space: pre-wrap; font-size: 12px;">{markdown_content}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Show markdown statistics
            lines = markdown_content.split('\n')
            words = len(markdown_content.split())
            chars = len(markdown_content)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Lines", len(lines))
            with col_b:
                st.metric("Words", words)
            with col_c:
                st.metric("Characters", chars)

            # Download button for markdown
            st.download_button(
                label=f"📥 Download {selected_tool.title()} Markdown",
                data=markdown_content,
                file_name=f"{filename}_{selected_tool}.md",
                mime="text/markdown"
            )
        else:
            st.warning(f"Markdown file not found for {selected_tool} extraction")
    else:
        st.info("Please select a markdown file above or from the Results Overview page")

# Tool comparison section
st.subheader("⚖️ Extraction Tool Comparison")

if st.session_state.selected_row_data:
    row_data = st.session_state.selected_row_data
    
    # Create comparison metrics
    tools_data = []
    
    for tool in ['Pymupdf', 'Marker', 'Mineru']:
        tool_info = {}
        tool_info['Tool'] = tool
        # Get scores
        score_key = f'Overall Score {tool}'
        if score_key in row_data and pd.notna(row_data[score_key]):
            tool_info['Overall Score'] = round(row_data[score_key], 3)
        else:
            tool_info['Overall Score'] = 'N/A'
        # Get word count (if available)
        count_key = f'Word Count {tool}'
        if count_key in row_data and pd.notna(row_data[count_key]):
            tool_info['Word Count'] = int(row_data[count_key])
        else:
            # Try alternative: 'Pdf Page Count' or similar if needed
            tool_info['Word Count'] = 'N/A'
        # Get perplexity (if available)
        perp_key = f'Perplexity {tool}'
        if perp_key in row_data and pd.notna(row_data[perp_key]):
            tool_info['Perplexity'] = round(row_data[perp_key], 2)
        else:
            tool_info['Perplexity'] = 'N/A'
        tools_data.append(tool_info)
    
    # Display comparison table
    comparison_df = pd.DataFrame(tools_data)
    st.dataframe(comparison_df, use_container_width=True)
    
    # Detailed scores breakdown
    with st.expander("🔍 Detailed Score Breakdown"):
        score_types = ['Line Continuity', 'Paragraph Integrity', 'Content Sequencing', 
                      'Layout Separation', 'Text Completeness']
        detailed_data = []
        for tool in ['Pymupdf', 'Marker', 'Mineru']:
            tool_scores = {'Tool': tool}
            for score_type in score_types:
                score_key = f'{score_type} Score {tool}'
                if score_key in row_data and pd.notna(row_data[score_key]):
                    tool_scores[score_type] = round(row_data[score_key], 3)
                else:
                    tool_scores[score_type] = 'N/A'
            detailed_data.append(tool_scores)
        detailed_df = pd.DataFrame(detailed_data)
        st.dataframe(detailed_df, use_container_width=True)
else:
    st.info("ℹ️ Tool comparison data is not available. Please select a document from the 'Results Overview' page to view extraction tool performance metrics.")

# Navigation
st.subheader("🧭 Navigation")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔙 Back to Results Overview", type="secondary"):
        # Clear selection and go back
        st.session_state.selected_file = None
        st.session_state.selected_row_data = None
        st.info("Navigate to 'Results Overview' to select another document")

with col2:
    if st.button("🔄 Clear Selection", type="secondary"):
        st.session_state.selected_file = None
        st.session_state.selected_row_data = None
        st.rerun() 