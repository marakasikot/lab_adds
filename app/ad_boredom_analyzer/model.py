import pandas as pd
import numpy as np
from . import config


def get_recommendations(df_with_boredom: pd.DataFrame,
                        threshold: float = config.BOREDOM_THRESHOLD) -> pd.DataFrame:

    if not all(col in df_with_boredom.columns for col in ['user_id', 'ad_id', 'boredom_score']):
        raise ValueError("Input DataFrame is missing required columns: user_id, ad_id, boredom_score.")

    df = df_with_boredom.copy()
    df['recommendation'] = np.where(df['boredom_score'] > threshold, 'hide', 'show')

    output_columns = ['user_id', 'ad_id', 'boredom_score', 'total_views', 'total_clicks', 'ctr', 'latest_view_count',
                      'recommendation']

    final_columns = [col for col in output_columns if col in df.columns]

    return df[final_columns]


if __name__ == '__main__':

    sample_data = {
        'user_id': ['user_001', 'user_001', 'user_002', 'user_003', 'user_004'],
        'ad_id': ['ad_001', 'ad_002', 'ad_001', 'ad_003', 'ad_001'],
        'boredom_score': [0.9, 0.2, 0.75, 0.8, 0.1],
        'total_views': [10, 2, 8, 9, 1],
        'total_clicks': [1, 1, 2, 0, 0],
        'ctr': [0.1, 0.5, 0.25, 0.0, 0.0],
        'latest_view_count': [10, 2, 8, 9, 1]
    }
    test_boredom_df = pd.DataFrame(sample_data)

    recommendations = get_recommendations(test_boredom_df)
    print("\nRecommendations:")
    print(recommendations)

    recommendations_custom_threshold = get_recommendations(test_boredom_df, threshold=0.5)
    print("\nRecommendations (threshold 0.5):")
    print(recommendations_custom_threshold)