# streamlit_app.py
import streamlit as st
import pandas as pd
import os

# Import modules from the package
from ad_boredom_analyzer import data_generator
from ad_boredom_analyzer import metrics
from ad_boredom_analyzer import model
from ad_boredom_analyzer import visualization
from ad_boredom_analyzer import config  # For default paths and parameters

# Page configuration
st.set_page_config(layout="wide", page_title="Ad Boredom Analyzer")


def run_analysis_pipeline(df_raw: pd.DataFrame, saturation_pt: int, boredom_thresh: float):
    """Helper function to run the core analysis steps."""
    if df_raw.empty:
        st.warning("Cannot run analysis on empty data.")
        return None
    try:
        df_agg = metrics.calculate_aggregated_metrics(df_raw)
        df_boredom = metrics.calculate_boredom_score(df_agg, saturation_point=saturation_pt)
        df_recs = model.get_recommendations(df_boredom, threshold=boredom_thresh)
        return df_recs
    except ValueError as e:
        st.error(f"Error during analysis: {e}")
        st.info(
            "Please ensure your uploaded CSV has the correct columns: user_id, ad_id, ad_type, view_time, clicked, view_count, date.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during analysis: {e}")
        return None


# --- Main App ---
st.title("🎯 Ad Boredom Analyzer & Recommendation Tool")

st.markdown("""
Welcome to the Ad Boredom Analyzer! This tool helps you:
1.  **Generate** sample ad interaction data.
2.  **Upload** your own ad interaction data (CSV format).
3.  **Analyze** the data to calculate a 'boredom score' for each user-ad pair.
4.  **Receive recommendations** on whether to continue showing or hide an ad.
5.  **Visualize** the results.
""")

# --- Sidebar for Controls ---
st.sidebar.header("⚙️ Controls & Settings")

st.sidebar.subheader("1. Data Input")
input_method = st.sidebar.radio("Choose data input method:", ("Generate Sample Data", "Upload CSV File"))

# Session state to store data
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = pd.DataFrame()
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = pd.DataFrame()

if input_method == "Generate Sample Data":
    st.sidebar.markdown("---")
    num_records = st.sidebar.slider("Number of Records", 100, 5000, config.NUM_RECORDS_TO_GENERATE, 100)
    num_users = st.sidebar.slider("Number of Users", 10, 500, config.NUM_USERS, 10)
    num_ads = st.sidebar.slider("Number of Ads", 5, 100, config.NUM_ADS, 5)

    if st.sidebar.button("Generate Data", key="generate_data_btn"):
        with st.spinner("Generating data..."):
            gen_file_path = data_generator.generate_ad_data(
                num_records=num_records,
                num_users=num_users,
                num_ads=num_ads,
                ad_types=config.AD_TYPES,  # Uses types from config
                output_dir=config.INPUT_DATA_DIR,
                filename="generated_ad_views.csv"
            )
            st.session_state.raw_data = pd.read_csv(gen_file_path)
            st.session_state.analyzed_data = pd.DataFrame()  # Clear previous analysis
            st.sidebar.success(f"Generated {len(st.session_state.raw_data)} records.")
            st.sidebar.info(f"Data saved to: {gen_file_path}")

elif input_method == "Upload CSV File":
    st.sidebar.markdown("---")
    uploaded_file = st.sidebar.file_uploader("Upload your ad_views.csv file", type=["csv"])
    if uploaded_file is not None:
        try:
            st.session_state.raw_data = pd.read_csv(uploaded_file)
            st.session_state.analyzed_data = pd.DataFrame()  # Clear previous analysis
            st.sidebar.success("CSV file uploaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")
            st.session_state.raw_data = pd.DataFrame()

st.sidebar.markdown("---")
st.sidebar.subheader("2. Analysis Parameters")
saturation_point = st.sidebar.slider(
    "Saturation View Count (for boredom calc)",
    min_value=3, max_value=50, value=config.SATURATION_VIEW_COUNT, step=1,
    help="Number of views at which an ad is considered to have reached saturation for boredom calculation."
)
boredom_threshold_input = st.sidebar.slider(
    "Boredom Threshold (for 'hide' rec)",
    min_value=0.1, max_value=1.0, value=config.BOREDOM_THRESHOLD, step=0.05,
    help="Boredom score above which an ad is recommended to be hidden."
)

# --- Main Display Area ---
if not st.session_state.raw_data.empty:
    st.subheader("📋 Raw Interaction Data (Preview)")
    st.dataframe(st.session_state.raw_data.head())
    st.markdown(f"*Total records loaded: {len(st.session_state.raw_data)}*")

    if st.button("🚀 Run Full Analysis", key="run_analysis_btn"):
        with st.spinner("Analyzing data... Please wait."):
            st.session_state.analyzed_data = run_analysis_pipeline(
                st.session_state.raw_data,
                saturation_point,
                boredom_threshold_input
            )
        if st.session_state.analyzed_data is not None and not st.session_state.analyzed_data.empty:
            st.success("Analysis Complete!")
        elif st.session_state.analyzed_data is None:
            st.error("Analysis could not be completed due to an error.")
        else:
            st.warning("Analysis completed, but the resulting dataset is empty. Check your input data or parameters.")

if st.session_state.analyzed_data is not None and not st.session_state.analyzed_data.empty:
    st.subheader("📊 Analysis Results & Recommendations")

    # Information on Threshold Crossing
    hidden_ads_count = st.session_state.analyzed_data[st.session_state.analyzed_data['recommendation'] == 'hide'].shape[
        0]
    total_analyzed_pairs = len(st.session_state.analyzed_data)

    if hidden_ads_count > 0:
        st.warning(f"""
        **Threshold Alert:** {hidden_ads_count} out of {total_analyzed_pairs} user-ad pairs have crossed 
        the boredom threshold of {boredom_threshold_input:.2f} and are recommended to be hidden.
        Review the table below for details.
        """)
    else:
        st.success(f"""
        All {total_analyzed_pairs} analyzed user-ad pairs are below the boredom threshold 
        of {boredom_threshold_input:.2f}. No ads currently recommended to hide based on boredom.
        """)

    # Filtering options for results
    st.markdown("---")
    st.markdown("#### Filter Results")

    # Ad type filter
    available_ad_types = ['All'] + sorted(list(st.session_state.analyzed_data['ad_type'].unique()))
    selected_ad_types_filter = st.multiselect("Filter by Ad Type(s):", available_ad_types, default=['All'])

    # Recommendation filter
    rec_filter_options = ['All', 'show', 'hide']
    selected_rec_filter = st.selectbox("Filter by Recommendation:", rec_filter_options, index=0)

    # Apply filters
    filtered_results_df = st.session_state.analyzed_data.copy()
    if 'All' not in selected_ad_types_filter and selected_ad_types_filter:
        filtered_results_df = filtered_results_df[filtered_results_df['ad_type'].isin(selected_ad_types_filter)]

    if selected_rec_filter != 'All':
        filtered_results_df = filtered_results_df[filtered_results_df['recommendation'] == selected_rec_filter]

    st.dataframe(filtered_results_df)

    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        csv_data = filtered_results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Results as CSV",
            data=csv_data,
            file_name=config.RECOMMENDATIONS_CSV_FILENAME,
            mime='text/csv',
        )
    with col2:
        json_data = filtered_results_df.to_json(orient="records", indent=4).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Results as JSON",
            data=json_data,
            file_name=config.RECOMMENDATIONS_JSON_FILENAME,
            mime='application/json',
        )

    st.markdown("---")
    st.subheader("📈 Visualizations")

    # Determine which ad types to use for plotting based on filter (or all if 'All' is selected)
    plot_ad_types = selected_ad_types_filter if 'All' not in selected_ad_types_filter and selected_ad_types_filter else None

    if not filtered_results_df.empty:
        tab1, tab2 = st.tabs(["Boredom vs. Views", "Boredom Score Distribution"])
        with tab1:
            st.plotly_chart(
                visualization.plot_boredom_vs_views_plotly(filtered_results_df, selected_ad_types=plot_ad_types),
                use_container_width=True
            )
            st.caption(
                "This scatter plot shows the relationship between the total number of times a user has seen an ad (Latest View Count) and the calculated boredom score. Points are colored by recommendation and shaped by ad type.")
        with tab2:
            st.plotly_chart(
                visualization.plot_boredom_distribution_plotly(filtered_results_df, selected_ad_types=plot_ad_types),
                use_container_width=True
            )
            st.caption(
                "This histogram shows the distribution of boredom scores. It can be faceted by ad type if multiple types are present and selected. The vertical dashed line indicates the current boredom threshold.")
    else:
        st.info("No data to display in plots based on current filters.")

else:
    st.info("Please generate or upload data and run the analysis to see results and visualizations.")

# --- User Guidance / How to Use ---
st.sidebar.markdown("---")
st.sidebar.subheader("💡 How to Use This Tool")
with st.sidebar.expander("Click here for instructions"):
    st.markdown("""
    1.  **Choose Data Input:**
        *   **Generate Sample Data:** Adjust sliders for records, users, ads, then click "Generate Data".
        *   **Upload CSV File:** Click "Browse files" and select your CSV. The CSV must have columns: `user_id, ad_id, ad_type, view_time, clicked, view_count, date`.
    2.  **Adjust Analysis Parameters (Optional):**
        *   **Saturation View Count:** Influences how quickly boredom increases with views.
        *   **Boredom Threshold:** Score above which an ad is marked "hide".
    3.  **Run Analysis:**
        *   Click the "🚀 Run Full Analysis" button in the main panel after data is loaded/generated.
    4.  **Review Results:**
        *   A summary of threshold crossings will appear.
        *   The table shows detailed scores and recommendations. You can filter this table.
        *   Download results as CSV or JSON.
    5.  **Explore Visualizations:**
        *   Interactive plots help understand boredom patterns. They will also update based on the 'Filter by Ad Type(s)' selection applied to the results table.
    """)
st.sidebar.markdown("---")
st.sidebar.markdown("Developed with ❤️ using Streamlit & Plotly.")