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
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, filename)
    user_ids = [f"user_{i:04}" for i in range(1, num_users + 1)]
    all_data = []
    start_date = datetime(2025, 4, 1)

    for ad_type in ad_types:
        if ad_type not in config.AD_TYPE_SPECIFICS:
            print(f"Warning: No specifics found for ad_type '{ad_type}' in config. Using default behavior.")
            specifics = {"base_click_prob_factor": 1.0, "view_count_ctr_decay_factor": 0.03,
                         "view_time_min": 1.0, "view_time_max": 60.0}  # Default
        else:
            specifics = config.AD_TYPE_SPECIFICS[ad_type]

        ads_for_this_type = [f"{ad_type}_ad_{i:03}" for i in range(1, num_ads_per_type + 1)]
        user_ad_view_counts_type = {}

        for _ in range(num_records_approx_per_type):
            user_id = np.random.choice(user_ids)
            ad_id = np.random.choice(ads_for_this_type)

            current_view_count = user_ad_view_counts_type.get((user_id, ad_id), 0) + 1
            user_ad_view_counts_type[(user_id, ad_id)] = current_view_count

            # Генерація часу перегляду
            view_time = round(np.random.uniform(specifics["view_time_min"], specifics["view_time_max"]), 1)

            base_click_prob = 0.1  # Базова ймовірність, якщо нічого не впливає

            # Вплив типу реклами
            type_adjusted_prob = base_click_prob * specifics["base_click_prob_factor"]

            # Вплив "свіжості" реклами (перші покази більш клікабельні)
            if current_view_count <= 10:
                freshness_boost = 0.15
            elif current_view_count <= 15:
                freshness_boost = 0.05
            else:
                freshness_boost = 0.0

            prob_after_freshness = type_adjusted_prob + freshness_boost

            # Вплив втоми від кількості показів (CTR)
            # Чим більший view_count_ctr_decay_factor, тим швидше падає ймовірність
            # Decay починається після кількох перших показів
            decay = 0.0
            if current_view_count > 2:  # Починаємо зменшувати після 2-х показів
                decay = (current_view_count - 2) * specifics["view_count_ctr_decay_factor"]

            final_click_probability = prob_after_freshness - decay

            # Вплив дуже короткого часу перегляду
            if view_time < 2.0:  # Якщо час перегляду дуже малий, сильно ріжемо ймовірність
                final_click_probability *= 0.1
            elif view_time < 5.0 and ad_type in ["video", "interstitial"]:  # Для відео/інтерстишиалів 5с - мало
                final_click_probability *= 0.3

            # Обмежуємо ймовірність знизу (наприклад, 0.005) і зверху (наприклад, 0.7)
            final_click_probability = np.clip(final_click_probability, 0.005, 0.7)

            clicked = 1 if np.random.rand() < final_click_probability else 0

            # Якщо клікнули, але час перегляду абсурдно малий (особливо для відео) - скасовуємо клік
            if clicked == 1:
                if ad_type == "video" and view_time < 3.0:
                    clicked = 0
                elif view_time < 0.8:
                    clicked = 0  # Загальне правило

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