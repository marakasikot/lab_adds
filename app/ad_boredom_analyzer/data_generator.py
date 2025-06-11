# ad_boredom_analyzer/data_generator.py
"""
Generates sample ad interaction data.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from . import config


def generate_ad_data(num_records_approx_per_type: int = config.NUM_RECORDS_TO_GENERATE // len(config.AD_TYPES),
                     num_users: int = config.NUM_USERS,
                     num_ads_per_type: int = config.NUM_ADS_PER_TYPE,
                     ad_types: list = config.AD_TYPES,
                     output_dir: str = config.INPUT_DATA_DIR,
                     filename: str = config.DEFAULT_INPUT_FILENAME) -> str:
    """
    Generates sample ad interaction data for specified ad types and saves it to a CSV file.

    Args:
        num_records_approx_per_type (int): Approximate number of interaction records per ad type.
        num_users (int): The number of unique users.
        num_ads_per_type (int): The number of unique ads per type.
        ad_types (list): List of possible ad types to generate data for.
        output_dir (str): Directory to save the generated CSV.
        filename (str): Name of the CSV file.

    Returns:
        str: The full path to the generated CSV file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, filename)

    user_ids = [f"user_{i:04}" for i in range(1, num_users + 1)]

    all_data = []
    start_date = datetime(2025, 4, 1)

    for ad_type in ad_types:
        ads_for_this_type = [f"{ad_type}_ad_{i:03}" for i in range(1, num_ads_per_type + 1)]
        user_ad_view_counts_type = {}

        for _ in range(num_records_approx_per_type):
            user_id = np.random.choice(user_ids)
            ad_id = np.random.choice(ads_for_this_type)

            current_view_count = user_ad_view_counts_type.get((user_id, ad_id), 0) + 1
            user_ad_view_counts_type[(user_id, ad_id)] = current_view_count

            view_time = round(np.random.uniform(0.5, 120.0), 1)
            if ad_type == "video":
                view_time = round(np.random.uniform(5.0, 300.0), 1)
            elif ad_type == "banner":
                view_time = round(np.random.uniform(0.5, 30.0), 1)
            elif ad_type == "native":
                view_time = round(np.random.uniform(1.0, 60.0), 1)
            elif ad_type == "interstitial":
                view_time = round(np.random.uniform(2.0, 45.0), 1)

            click_probability = 0.05
            if current_view_count <= 3: click_probability += 0.25
            if view_time < 2.0: click_probability *= 0.1

            if ad_type == "banner":
                click_probability *= 1.2
            elif ad_type == "video":
                click_probability *= 0.8
            elif ad_type == "native":
                click_probability *= 1.1
            elif ad_type == "interstitial":
                click_probability *= 0.9

            clicked = 1 if np.random.rand() < click_probability else 0

            if view_time < 1.0 and clicked == 1: clicked = 0

            date = (start_date + timedelta(days=np.random.randint(0, 89))).strftime('%Y-%m-%d')

            all_data.append({
                "user_id": user_id,
                "ad_id": ad_id,
                "ad_type": ad_type,
                "view_time": view_time,
                "clicked": clicked,
                "view_count_raw": current_view_count,
                "date": date
            })

    df = pd.DataFrame(all_data)

    if not df.empty:
        df = df.sort_values(by=['user_id', 'ad_id', 'date', 'view_count_raw']).reset_index(drop=True)
        df['view_count'] = df.groupby(['user_id', 'ad_id']).cumcount() + 1
        df = df.drop(columns=['view_count_raw'])
    else:
        df = pd.DataFrame(columns=['user_id', 'ad_id', 'ad_type', 'view_time', 'clicked', 'view_count', 'date'])

    df.to_csv(output_path, index=False)
    print(f"Згенеровано {len(df)} записів для типів {', '.join(ad_types)} у файл {output_path}")
    return output_path


if __name__ == '__main__':
    generate_ad_data()