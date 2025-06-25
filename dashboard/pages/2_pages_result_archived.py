import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page title
st.set_page_config(page_title="📄 Page-Level Extraction Results", layout="wide")

@st.cache_data
def load_data():
    """Load the page-level evaluation results data"""
    try:
        # Load the page-level evaluation data
        # data_path = Path("output/page_scores_lt15_en.csv") # Old path
        # metadata_path = Path("output/metadata_openalex(silver).pkl") # Old path

        page_scores_path = Path(st.session_state.page_scores_csv)
        metadata_path = Path(st.session_state.metadata_pkl)

        if page_scores_path.exists() and metadata_path.exists(): # Check both paths
            df = pd.read_csv(page_scores_path)
            metadata = pd.read_pickle(metadata_path)
            metadata['filename'] = metadata['id_gotriple'].apply(lambda x: 'extracted_'+ x.replace('/', '_').replace(':', '_').replace('.', '_'))
            df = df.merge(metadata, on=['filename', 'discipline'], how='left')
            # Clean up column names for better display
            df.columns = [col.replace('_', ' ').title() for col in df.columns]
            return df
        else:
            error_messages = []
            if not page_scores_path.exists():
                error_messages.append(f"Page scores data file not found: {page_scores_path}")
            if not metadata_path.exists():
                error_messages.append(f"Metadata file not found: {metadata_path}")
            st.error("\n".join(error_messages))
            return pd.DataFrame()
    except KeyError as e:
        st.error(f"Path key not found in session state: {e}. Ensure paths are initialized in app.py.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data
df = load_data()

if df.empty:
    st.warning("No data available to display.")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Discipline filter
if 'Discipline' in df.columns:
    disciplines = ['All'] + sorted(df['Discipline'].unique().tolist())
    selected_discipline = st.sidebar.selectbox("Select Discipline:", disciplines)
    if selected_discipline != 'All':
        df = df[df['Discipline'] == selected_discipline]

# Page number filter
if 'Page Number' in df.columns or 'Page Num' in df.columns:
    page_col = 'Page Number' if 'Page Number' in df.columns else 'Page Num'
    max_page = int(df[page_col].max()) if not df[page_col].isna().all() else 1
    min_page = int(df[page_col].min()) if not df[page_col].isna().all() else 1
    
    page_range = st.sidebar.slider(
        "Page Number Range:",
        min_value=min_page,
        max_value=max_page,
        value=(min_page, max_page),
        step=1
    )
    df = df[(df[page_col] >= page_range[0]) & (df[page_col] <= page_range[1])]

# Metric thresholds
st.sidebar.subheader("📊 Score Filters")

# Extract numeric columns for filtering
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
score_cols = [col for col in numeric_cols if 'Score' in col or 'score' in col.lower()]

# Overall score filter
overall_score_cols = [col for col in score_cols if 'Overall' in col or 'overall' in col.lower()]
if overall_score_cols:
    min_score = st.sidebar.slider(
        "Minimum Overall Score:",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05
    )
    # Filter by any overall score column
    mask = False
    for col in overall_score_cols:
        mask |= (df[col] >= min_score)
    df = df[mask]

# Word count filter
word_count_cols = [col for col in numeric_cols if 'Word Count' in col or 'word count' in col.lower()]
if word_count_cols:
    min_words = st.sidebar.number_input("Minimum Word Count:", min_value=0, value=0, step=100)
    mask = False
    for col in word_count_cols:
        mask |= (df[col] >= min_words)
    if min_words > 0:
        df = df[mask]

# Search functionality
st.sidebar.subheader("🔎 Search")
search_term = st.sidebar.text_input("Search in filename:")
if search_term:
    if 'Filename' in df.columns:
        df = df[df['Filename'].str.contains(search_term, case=False, na=False)]

# Main content area
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.metric("Total Pages", len(df))
with col2:
    if overall_score_cols:
        avg_score = df[overall_score_cols[0]].mean()
        st.metric("Average Overall Score", f"{avg_score:.3f}")
with col3:
    if 'Filename' in df.columns:
        unique_docs = df['Filename'].nunique()
        st.metric("Unique Documents", unique_docs)

# Display options
st.subheader("📋 Page Results Table")
col1, col2 = st.columns([3, 1])
with col1:
    # Define default columns to show (most important ones)
    default_cols = []
    available_cols = df.columns.tolist()
    
    # Priority columns to show by default
    priority_cols = [
        'Filename', 'Page Number', 'Page Num', 'Discipline',
        'Overall Score', 'Word Count', 'Title', 'Abstract'
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
    total_rows = len(df)
    total_pages = (total_rows - 1) // rows_per_page + 1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page_num = st.selectbox(
            f"Page (1-{total_pages}):",
            range(1, total_pages + 1),
            key="page_selector"
        )
    
    # Calculate row range for current page
    start_idx = (page_num - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)
    
    # Display subset of data
    page_df = df[show_columns].iloc[start_idx:end_idx].reset_index(drop=True)
    
    # Create interactive table with click functionality
    st.write(f"Showing rows {start_idx + 1}-{end_idx} of {total_rows}")
    
    # Add a button column for navigation
    display_df = page_df.copy()
    
    # Display the table with selection enabled
    selected_rows = st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True
    )
    
    # Row selection for PDF viewer
    if total_rows > 0:
        # Check if any row is selected
        if selected_rows.selection.rows:
            selected_table_idx = selected_rows.selection.rows[0]
            actual_row_idx = start_idx + selected_table_idx
            selected_filename = df.iloc[actual_row_idx].get('Filename', f'Row {actual_row_idx + 1}')
            selected_page = df.iloc[actual_row_idx].get('Page Number', df.iloc[actual_row_idx].get('Page Num', 'N/A'))
            
            st.info(f"Selected: {selected_filename} - Page {selected_page}")
            
            if st.button("🔍 View PDF & Markdown", type="primary"):
                # Store selected data in session state
                selected_row = df.iloc[actual_row_idx]
                st.session_state.selected_row_data = selected_row.to_dict()
                st.session_state.selected_file = selected_row.get('Filename', '')
                st.session_state.selected_page = selected_page
                # Directly navigate to the PDF viewer page
                st.switch_page("pages/3_pdf_vis.py")
        else:
            st.info("👆 Click on a row in the table above to select it, then click the button to view PDF & Markdown")

# Visualization section
if len(df) > 0 and overall_score_cols:
    st.subheader("📊 Score Distribution")
    
    # Score comparison chart
    fig_scores = go.Figure()
    
    for i, col in enumerate(overall_score_cols[:3]):  # Limit to first 3 score columns
        fig_scores.add_trace(go.Histogram(
            x=df[col],
            name=col.replace(' Overall Score', ''),
            opacity=0.7,
            nbinsx=20
        ))
    
    fig_scores.update_layout(
        title="Distribution of Overall Scores by Extraction Method (Page Level)",
        xaxis_title="Score",
        yaxis_title="Count",
        barmode='overlay',
        height=400
    )
    
    st.plotly_chart(fig_scores, use_container_width=True)
    
    # Performance comparison by discipline
    if 'Discipline' in df.columns and len(df['Discipline'].unique()) > 1:
        st.subheader("📈 Performance by Discipline (Page Level)")
        
        # Calculate average scores by discipline
        discipline_scores = df.groupby('Discipline')[overall_score_cols[0]].agg(['mean', 'count']).reset_index()
        discipline_scores.columns = ['Discipline', 'Average Score', 'Count']
        
        fig_discipline = px.bar(
            discipline_scores,
            x='Discipline',
            y='Average Score',
            title=f"Average {overall_score_cols[0]} by Discipline (Page Level)",
            text='Count',
            height=400
        )
        
        fig_discipline.update_traces(texttemplate='%{text} pages', textposition='outside')
        fig_discipline.update_layout(yaxis=dict(range=[0, 1]))
        
        st.plotly_chart(fig_discipline, use_container_width=True)
    
    # Page number vs performance analysis
    page_col = 'Page Number' if 'Page Number' in df.columns else ('Page Num' if 'Page Num' in df.columns else None)
    if page_col:
        st.subheader("📄 Performance by Page Number")
        
        # Calculate average scores by page number
        page_scores = df.groupby(page_col)[overall_score_cols[0]].agg(['mean', 'count']).reset_index()
        page_scores.columns = ['Page Number', 'Average Score', 'Count']
        
        # Only show pages with at least 5 samples
        page_scores = page_scores[page_scores['Count'] >= 5]
        
        if len(page_scores) > 0:
            fig_page = px.scatter(
                page_scores,
                x='Page Number',
                y='Average Score',
                size='Count',
                title=f"Average {overall_score_cols[0]} by Page Number",
                hover_data=['Count'],
                height=400
            )
            
            fig_page.update_layout(yaxis=dict(range=[0, 1]))
            
            st.plotly_chart(fig_page, use_container_width=True)
            
            st.caption("Only showing page numbers with at least 5 samples. Bubble size indicates number of pages.")

# Export functionality
st.subheader("💾 Export Data")
if st.button("📁 Download Filtered Results as CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"filtered_page_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
