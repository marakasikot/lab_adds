# ad_boredom_analyzer/config.py
"""
Configuration settings for the ad boredom analyzer.
"""
import os

# Data paths
INPUT_DATA_DIR = "data/"
OUTPUT_DATA_DIR = "output/"
DEFAULT_INPUT_FILENAME = "ad_views_all_types.csv"
RECOMMENDATIONS_CSV_FILENAME = "ad_recommendations.csv"
RECOMMENDATIONS_JSON_FILENAME = "ad_recommendations.json"

# Plot paths - назви зараз не такі важливі, бо графіки інтерактивні
BOREDOM_VS_VIEWS_PLOT_FILENAME = "boredom_vs_views.png"
BOREDOM_DISTRIBUTION_PLOT_FILENAME = "boredom_distribution.png"

# Boredom calculation parameters
SATURATION_VIEW_COUNT = 10
BOREDOM_THRESHOLD = 0.75

# Data generation parameters
NUM_RECORDS_TO_GENERATE = 5000 # Приблизна загальна кількість, розподілиться між типами
NUM_USERS = 1000
NUM_ADS_PER_TYPE = 5 # Кількість унікальних реклам кожного типу
AD_TYPES = ["banner", "video", "native", "interstitial"]

# Ensure output directory exists when config is loaded
if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)
if not os.path.exists(INPUT_DATA_DIR):
    os.makedirs(INPUT_DATA_DIR)