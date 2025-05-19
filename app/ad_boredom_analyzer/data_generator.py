import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from . import config


def generate_ad_data(num_records: int = config.NUM_RECORDS_TO_GENERATE,
                     num_users: int = config.NUM_USERS,
                     num_ads: int = config.NUM_ADS,
                     output_dir: str = config.INPUT_DATA_DIR,
                     filename: str = config.DEFAULT_INPUT_FILENAME) -> str:

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, filename)

    user_ids = [f"user_{i:03}" for i in range(1, num_users + 1)]
    ad_ids = [f"ad_{i:03}" for i in range(1, num_ads + 1)]

    data = []
    start_date = datetime(2025, 4, 1)

    user_ad_view_counts = {}

    for _ in range(num_records):
        user_id = np.random.choice(user_ids)
        ad_id = np.random.choice(ad_ids)

        current_view_count = user_ad_view_counts.get((user_id, ad_id), 0) + 1
        user_ad_view_counts[(user_id, ad_id)] = current_view_count

        view_time = round(np.random.uniform(0.5, 120.0), 1)

        click_probability = 0.05
        if current_view_count <= 3:
            click_probability += 0.25
        if view_time < 2.0:
            click_probability *= 0.1

        clicked = 1 if np.random.rand() < click_probability else 0

        if view_time < 1.0 and clicked == 1:
            clicked = 0

        date = (start_date + timedelta(days=np.random.randint(0, 89))).strftime('%Y-%m-%d')

        data.append({
            "user_id": user_id,
            "ad_id": ad_id,
            "view_time": view_time,
            "clicked": clicked,
            "view_count": current_view_count,
            "date": date
        })

    df = pd.DataFrame(data)
    df = df.sort_values(by=['user_id', 'ad_id', 'date', 'view_count']).reset_index(drop=True)

    df['view_count'] = df.groupby(['user_id', 'ad_id']).cumcount() + 1

    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records into {output_path}")
    return output_path


if __name__ == '__main__':
    generate_ad_data(num_records=500)
