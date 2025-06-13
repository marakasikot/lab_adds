import os

INPUT_DATA_DIR = "data/"
OUTPUT_DATA_DIR = "output/"
DEFAULT_INPUT_FILENAME = "ad_views_all_types.csv"
RECOMMENDATIONS_CSV_FILENAME = "ad_recommendations.csv"
RECOMMENDATIONS_JSON_FILENAME = "ad_recommendations.json"

BOREDOM_VS_VIEWS_PLOT_FILENAME = "boredom_vs_views.png"
BOREDOM_DISTRIBUTION_PLOT_FILENAME = "boredom_distribution.png"

SATURATION_VIEW_COUNT = 10
BOREDOM_THRESHOLD = 0.75

NUM_RECORDS_TO_GENERATE = 100000
NUM_USERS = 10000
NUM_ADS_PER_TYPE = 5 # Кількість унікальних реклам кожного типу
AD_TYPES = ["banner", "video", "native", "interstitial"]

if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)
if not os.path.exists(INPUT_DATA_DIR):
    os.makedirs(INPUT_DATA_DIR)

AD_TYPE_SPECIFICS = {
    "banner": {
        "base_click_prob_factor": 1.0, # Базовий множник ймовірності кліку
        "view_count_ctr_decay_factor": 0.03, # Наскільки сильно кожен показ зменшує CTR
        "view_time_min": 0.5, "view_time_max": 30.0
    },
    "video": {
        "base_click_prob_factor": 0.8,
        "view_count_ctr_decay_factor": 0.05,
        "view_time_min": 5.0, "view_time_max": 300.0
    },
    "native": {
        "base_click_prob_factor": 1.3,
        "view_count_ctr_decay_factor": 0.01,
        "view_time_min": 1.0, "view_time_max": 60.0
    },
    "interstitial": {
        "base_click_prob_factor": 0.7,
        "view_count_ctr_decay_factor": 0.06,
        "view_time_min": 2.0, "view_time_max": 45.0
    }
}