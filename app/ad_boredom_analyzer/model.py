import pandas as pd
import numpy as np
from . import config


def get_recommendations(df_with_boredom: pd.DataFrame,
                        threshold: float = config.BOREDOM_THRESHOLD) -> pd.DataFrame:
    """
    Generates recommendations (show/hide) based on the boredom score.
    """
    required_cols = ['user_id', 'ad_id', 'ad_type', 'boredom_score']
    if not all(col in df_with_boredom.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df_with_boredom.columns]
        raise ValueError(f"Input DataFrame is missing required columns: {', '.join(missing)}.")

    df = df_with_boredom.copy()
    df['recommendation'] = np.where(df['boredom_score'] > threshold, 'hide', 'show')

    output_columns_ordered = [
        'user_id', 'ad_id', 'ad_type',
        'total_views', 'total_clicks', 'ctr', 'latest_view_count', 'avg_view_time',
        'boredom_score', 'recommendation'
    ]
    final_columns = [col for col in output_columns_ordered if col in df.columns]
    return df[final_columns]


if __name__ == '__main__':
    sample_data = {
        'user_id': ['user_001', 'user_001', 'user_002'],
        'ad_id': ['ad_001', 'ad_002', 'ad_001'],
        'ad_type': ['banner', 'video', 'banner'],
        'boredom_score': [0.9, 0.2, 0.75],
        'total_views': [10, 2, 8],
        'total_clicks': [1, 1, 2],
        'ctr': [0.1, 0.5, 0.25],
        'latest_view_count': [10, 2, 8],
        'avg_view_time': [10.0, 15.5, 5.2]
    }
    test_boredom_df = pd.DataFrame(sample_data)
    recommendations = get_recommendations(test_boredom_df)
    print("\nRecommendations:")
    print(recommendations)