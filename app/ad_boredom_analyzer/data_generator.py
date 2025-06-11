# ad_boredom_analyzer/data_generator.py
"""
Generates sample ad interaction data.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from . import config


def generate_ad_data(num_records: int = config.NUM_RECORDS_TO_GENERATE,
                     num_users: int = config.NUM_USERS,
                     num_ads: int = config.NUM_ADS,
                     ad_types: list = config.AD_TYPES,  # New parameter
                     output_dir: str = config.INPUT_DATA_DIR,
                     filename: str = config.DEFAULT_INPUT_FILENAME) -> str:
    """
    Generates sample ad interaction data and saves it to a CSV file.

    Args:
        num_records (int): The number of interaction records to generate.
        num_users (int): The number of unique users.
        num_ads (int): The number of unique ads.
        ad_types (list): List of possible ad types.
        output_dir (str): Directory to save the generated CSV.
        filename (str): Name of the CSV file.

    Returns:
        str: The full path to the generated CSV file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, filename)

    user_ids = [f"user_{i:03}" for i in range(1, num_users + 1)]
    # Create unique ad_ids and assign a type to each ad_id consistently
    ad_details = {}
    for i in range(1, num_ads + 1):
        ad_id = f"ad_{i:03}"
        ad_details[ad_id] = np.random.choice(ad_types)

    ad_ids_list = list(ad_details.keys())

    data = []
    start_date = datetime(2025, 4, 1)

    user_ad_view_counts = {}

    for _ in range(num_records):
        user_id = np.random.choice(user_ids)
        ad_id = np.random.choice(ad_ids_list)  # Use the generated list
        ad_type = ad_details[ad_id]  # Get assigned ad_type

        current_view_count = user_ad_view_counts.get((user_id, ad_id), 0) + 1
        user_ad_view_counts[(user_id, ad_id)] = current_view_count

        view_time = round(np.random.uniform(0.5, 120.0), 1)
        if ad_type == "video":  # Videos tend to have longer view times
            view_time = round(np.random.uniform(5.0, 300.0), 1)
        elif ad_type == "banner":  # Banners might have shorter interaction
            view_time = round(np.random.uniform(0.5, 30.0), 1)

        click_probability = 0.05
        if current_view_count <= 3:
            click_probability += 0.25
        if view_time < 2.0:
            click_probability *= 0.1

        # Adjust click probability slightly by ad type (example)
        if ad_type == "banner":
            click_probability *= 1.2  # Slightly higher for banners
        elif ad_type == "video":
            click_probability *= 0.8  # Slightly lower for non-skippable videos during view

        clicked = 1 if np.random.rand() < click_probability else 0

        if view_time < 1.0 and clicked == 1:
            clicked = 0

        date = (start_date + timedelta(days=np.random.randint(0, 89))).strftime('%Y-%m-%d')

        data.append({
            "user_id": user_id,
            "ad_id": ad_id,
            "ad_type": ad_type,  # New field
            "view_time": view_time,
            "clicked": clicked,
            "view_count": current_view_count,
            "date": date
        })

    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by=['user_id', 'ad_id', 'date', 'view_count']).reset_index(drop=True)
        df['view_count'] = df.groupby(['user_id', 'ad_id']).cumcount() + 1
    else:
        # Create empty DataFrame with correct columns if no records generated
        df = pd.DataFrame(columns=['user_id', 'ad_id', 'ad_type', 'view_time', 'clicked', 'view_count', 'date'])

    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records into {output_path}")
    return output_path


if __name__ == '__main__':
    generate_ad_data(num_records=500)