import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page title
st.set_page_config(page_title="📊 PDF Extraction Benchmark Results", layout="wide")

@st.cache_data
def load_data():
    """Load both page-level and aggregated evaluation results data"""
    try:
        # Load the page-level evaluation data
        page_scores_path = Path(st.session_state.page_scores_csv)
        metadata_path = Path(st.session_state.metadata_pkl)

        if page_scores_path.exists() and metadata_path.exists():
            # Load page-level data
            page_df = pd.read_csv(page_scores_path)
            metadata = pd.read_pickle(metadata_path)
            
            # Prepare metadata filename
            metadata['filename'] = metadata['id_gotriple'].apply(lambda x: 'extracted_'+ x.replace('/', '_').replace(':', '_').replace('.', '_'))
            
            # Merge data using both filename and discipline as keys
            page_df = page_df.merge(metadata, on=['filename', 'discipline'], how='left')
            
            # Create aggregated version
            agg_dict = {}
            cols_to_agg = [col for col in page_df.columns if col not in ['filename', 'discipline', 'page_num', 'page_number']]
            
            # For numeric columns, calculate mean
            numeric_cols = page_df[cols_to_agg].select_dtypes(include=[np.number]).columns.tolist()
            for col in numeric_cols:
                agg_dict[col] = 'mean'
            
            # For non-numeric columns, take the first value
            non_numeric_cols = page_df[cols_to_agg].select_dtypes(exclude=[np.number]).columns.tolist()
            for col in non_numeric_cols:
                agg_dict[col] = 'first'
            
            # Create aggregated dataframe
            agg_df = page_df.groupby(['filename', 'discipline']).agg(agg_dict).reset_index()
            
            # Clean up column names for better display
            agg_df.columns = [col.replace('_', ' ').title() for col in agg_df.columns]
            page_df.columns = [col.replace('_', ' ').title() for col in page_df.columns]
            
            return agg_df, page_df
        else:
            error_messages = []
            if not page_scores_path.exists():
                error_messages.append(f"Page scores data file not found: {page_scores_path}")
            if not metadata_path.exists():
                error_messages.append(f"Metadata file not found: {metadata_path}")
            st.error("\n".join(error_messages))
            return pd.DataFrame(), pd.DataFrame()
    except KeyError as e:
        st.error(f"Path key not found in session state: {e}. Ensure paths are initialized in app.py.")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

# Load data
agg_df, page_df = load_data()

if agg_df.empty:
    st.warning("No data available to display.")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Discipline filter
if 'Discipline' in agg_df.columns:
    disciplines = ['All'] + sorted(agg_df['Discipline'].unique().tolist())
    selected_discipline = st.sidebar.selectbox("Select Discipline:", disciplines)
    if selected_discipline != 'All':
        agg_df = agg_df[agg_df['Discipline'] == selected_discipline]
        page_df = page_df[page_df['Discipline'] == selected_discipline]

# Metric thresholds
st.sidebar.subheader("📊 Score Filters")

# Extract numeric columns for filtering
numeric_cols = agg_df.select_dtypes(include=[np.number]).columns.tolist()
score_cols = [col for col in numeric_cols if 'Score' in col or 'score' in col.lower()]

# Score column selection and range filter
if score_cols:
    # Find the index of 'pymupdf overall' score column
    default_index = next((i for i, col in enumerate(score_cols) if 'pymupdf' in col.lower() and 'overall' in col.lower()), 0)
    
    selected_score_col = st.sidebar.selectbox(
        "Select Score Column:",
        options=score_cols,
        help="Select the score column to filter by",
        index=default_index
    )
    
    # Get min and max values for the selected score column
    min_val = float(agg_df[selected_score_col].min())
    max_val = float(agg_df[selected_score_col].max())
    
    # Create range slider
    score_range = st.sidebar.slider(
        f"Score Range for {selected_score_col}:",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        step=0.05
    )
    
    # Filter by score range
    agg_df = agg_df[(agg_df[selected_score_col] >= score_range[0]) & 
                    (agg_df[selected_score_col] <= score_range[1])]
    page_df = page_df[page_df['Filename'].isin(agg_df['Filename'])]

# Word count filter
word_count_cols = [col for col in numeric_cols if 'Word Count' in col or 'word count' in col.lower()]
if word_count_cols:
    min_words = st.sidebar.number_input("Minimum Word Count:", min_value=0, value=0, step=100)
    mask = False
    for col in word_count_cols:
        mask |= (agg_df[col] >= min_words)
    if min_words > 0:
        agg_df = agg_df[mask]
        page_df = page_df[page_df['Filename'].isin(agg_df['Filename'])]

# Search functionality
st.sidebar.subheader("🔎 Search")
search_term = st.sidebar.text_input("Search in filename:")
if search_term:
    if 'Filename' in agg_df.columns:
        agg_df = agg_df[agg_df['Filename'].str.contains(search_term, case=False, na=False)]
        page_df = page_df[page_df['Filename'].isin(agg_df['Filename'])]

# Main content area
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.metric("Total Documents", len(agg_df))
with col2:
    if score_cols:
        avg_score = agg_df[selected_score_col].mean()
        st.metric("Average Score", f"{avg_score:.3f}")
with col3:
    if 'Discipline' in agg_df.columns:
        unique_disciplines = agg_df['Discipline'].nunique()
        st.metric("Disciplines", unique_disciplines)

# Display options
st.subheader("📋 Results Table")
col1, col2 = st.columns([3, 1])
with col1:
    # Define default columns to show (most important ones)
    default_cols = []
    available_cols = agg_df.columns.tolist()
    
    # Priority columns to show by default
    priority_cols = [
        'Filename', 'Discipline', 'Overall Score', 'Word Count', 
        'Title', 'Abstract', 'Authors', 'Id Openalex'
    ]
    
    # Add priority columns that exist in the dataframe
    for col in priority_cols:
        if col in available_cols:
            default_cols.append(col)
    
    # Add any overall score columns
    for col in available_cols:
        if 'Overall' in col and 'Score' in col and col not in default_cols:
            default_cols.append(col)
    
    # Fill up to 8 columns with remaining columns if needed
    remaining_cols = [col for col in available_cols if col not in default_cols]
    while len(default_cols) < 8 and remaining_cols:
        default_cols.append(remaining_cols.pop(0))
    
    show_columns = st.multiselect(
        "Select columns to display:",
        options=available_cols,
        default=default_cols
    )
with col2:
    rows_per_page = st.selectbox("Rows per page:", [10, 25, 50, 100], index=1)

if show_columns:
    # Create pagination
    total_rows = len(agg_df)
    total_pages = (total_rows - 1) // rows_per_page + 1
    
    # Initialize page number in session state if not exists
    if 'page_num' not in st.session_state:
        st.session_state.page_num = 1
    
    # Calculate row range for current page (0-based indexing)
    start_idx = (st.session_state.page_num - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)
    
    # Display subset of data
    page_df_subset = agg_df[show_columns].iloc[start_idx:end_idx].reset_index(drop=True)
    
    # Create interactive table with click functionality
    st.write(f"Showing rows {start_idx + 1}-{end_idx} of {total_rows}")
    
    # Display the table with selection enabled
    selected_rows = st.dataframe(
        page_df_subset,
        use_container_width=True,
        height=400,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True
    )
    
    # Add pagination controls below the table
    pagination_cols = st.columns([1, 2, 1])
    with pagination_cols[0]:
        if st.button("⬅️ Previous", disabled=st.session_state.page_num <= 1):
            st.session_state.page_num = max(1, st.session_state.page_num - 1)
    with pagination_cols[1]:
        st.write(f"Page {st.session_state.page_num} of {total_pages}")
    with pagination_cols[2]:
        if st.button("Next ➡️", disabled=st.session_state.page_num >= total_pages):
            st.session_state.page_num = min(total_pages, st.session_state.page_num + 1)
    
    # Row selection for PDF viewer
    if total_rows > 0:
        # Check if any row is selected
        if selected_rows.selection.rows:
            selected_table_idx = selected_rows.selection.rows[0]
            actual_row_idx = start_idx + selected_table_idx
            selected_filename = agg_df.iloc[actual_row_idx].get('Filename', f'Row {actual_row_idx + 1}')
            
            st.info(f"Selected: {selected_filename}")
            if st.button("🔍 View PDF & Markdown", type="primary"):
                # Store selected data in session state
                selected_row = agg_df.iloc[actual_row_idx]
                st.session_state.selected_row_data = selected_row.to_dict()
                st.session_state.selected_file = selected_row.get('Filename', '')
                # Directly navigate to the PDF viewer page
                st.switch_page("pages/3_pdf_vis.py")
            
            # Show expandable page-level details
            with st.expander("📄 View Page-Level Details", expanded=True):
                # Filter page_df for the selected document
                doc_pages = page_df[page_df['Filename'] == selected_filename]
                
                # Display page-level metrics
                st.write("Page-Level Metrics:")
                # Get the actual column names for page number and scores
                page_num_col = next((col for col in doc_pages.columns if 'page' in col.lower() and ('num' in col.lower() or 'number' in col.lower())), None)
                score_cols = [col for col in doc_pages.columns if 'score' in col.lower()]
                word_count_col = next((col for col in doc_pages.columns if 'word' in col.lower() and 'count' in col.lower()), None)
                
                # Select available columns
                display_cols = []
                if page_num_col:
                    display_cols.append(page_num_col)
                if score_cols:
                    display_cols.extend(score_cols)
                if word_count_col:
                    display_cols.append(word_count_col)
                
                if display_cols:
                    page_metrics = doc_pages[display_cols]
                    st.dataframe(page_metrics, use_container_width=True)
                    
                    # Add page-level visualization if we have page numbers and scores
                    if page_num_col and score_cols:
                        fig = go.Figure()
                        for score_col in score_cols:
                            fig.add_trace(go.Scatter(
                                x=doc_pages[page_num_col],
                                y=doc_pages[score_col],
                                mode='lines+markers',
                                name=score_col
                            ))
                        fig.update_layout(
                            title="Page-Level Scores",
                            xaxis_title="Page Number",
                            yaxis_title="Score",
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No page-level metrics available for this document.")
            
            
        else:
            st.info("👆 Click on a row in the table above to view page-level details")


    
   

# Export functionality
st.subheader("💾 Export Data")
if st.button("📁 Download Filtered Results as CSV"):
    csv = agg_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"filtered_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    ) 