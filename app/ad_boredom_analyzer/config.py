# ad_boredom_analyzer/config.py
"""
Configuration settings for the ad boredom analyzer.
"""
import os

# Data paths
INPUT_DATA_DIR = "data/"
OUTPUT_DATA_DIR = "output/"
DEFAULT_INPUT_FILENAME = "ad_views.csv"
RECOMMENDATIONS_CSV_FILENAME = "ad_recommendations.csv"
RECOMMENDATIONS_JSON_FILENAME = "ad_recommendations.json"

# Plot paths
BOREDOM_VS_VIEWS_PLOT_FILENAME = "boredom_vs_views.png" # Will be Plotly, extension might not matter
BOREDOM_DISTRIBUTION_PLOT_FILENAME = "boredom_distribution.png" # Will be Plotly

# Boredom calculation parameters
SATURATION_VIEW_COUNT = 10
BOREDOM_THRESHOLD = 0.75

# Data generation parameters
NUM_RECORDS_TO_GENERATE = 1000
NUM_USERS = 100
NUM_ADS = 20
AD_TYPES = ["banner", "video", "native", "interstitial"] # New: List of ad types

# Ensure output directory exists when config is loaded (useful for Streamlit)
if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)
if not os.path.exists(INPUT_DATA_DIR):
    os.makedirs(INPUT_DATA_DIR)