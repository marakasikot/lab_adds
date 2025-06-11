# ad_boredom_analyzer/metrics.py
"""
Calculates various metrics from ad interaction data, including boredom score.
"""
import pandas as pd
import numpy as np
import os
from . import config

def calculate_aggregated_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates raw interaction data to calculate metrics per user-ad-ad_type pair.

    Args:
        df (pd.DataFrame): DataFrame with raw ad interaction data.
                           Expected columns: user_id, ad_id, ad_type, view_time, clicked, view_count.

    Returns:
        pd.DataFrame: DataFrame with aggregated metrics.
    """
    required_cols = ['user_id', 'ad_id', 'ad_type', 'view_time', 'clicked', 'view_count']
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"Input DataFrame is missing required columns: {', '.join(missing)}.")

    # Group by user_id, ad_id, and ad_type
    aggregated_df = df.groupby(['user_id', 'ad_id', 'ad_type']).agg(
        total_views=('date', 'count'),
        total_clicks=('clicked', 'sum'),
        avg_view_time=('view_time', 'mean'),
        latest_view_count=('view_count', 'max')
    ).reset_index()

    aggregated_df['ctr'] = np.where(
        aggregated_df['total_views'] > 0,
        aggregated_df['total_clicks'] / aggregated_df['total_views'],
        0
    )
    aggregated_df['avg_view_time'] = aggregated_df['avg_view_time'].round(2)
    return aggregated_df

def calculate_boredom_score(metrics_df: pd.DataFrame,
                            saturation_point: int = config.SATURATION_VIEW_COUNT) -> pd.DataFrame:
    """
    Calculates the boredom score for each user-ad-ad_type pair.
    The core logic currently does not differentiate by ad_type, but ad_type is preserved.

    Args:
        metrics_df (pd.DataFrame): DataFrame with aggregated metrics.
        saturation_point (int): The number of views for saturation.

    Returns:
        pd.DataFrame: The input DataFrame with an added 'boredom_score' column.
    """
    required_cols = ['user_id', 'ad_id', 'ad_type', 'total_views', 'ctr', 'latest_view_count']
    if not all(col in metrics_df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in metrics_df.columns]
        raise ValueError(f"Input metrics_df is missing required columns: {', '.join(missing)}.")

    df = metrics_df.copy()
    df['view_factor'] = (df['latest_view_count'] / saturation_point).clip(upper=1.0)
    df['boredom_score'] = (1 - df['ctr']) * df['view_factor']
    df.loc[df['total_views'] == 0, 'boredom_score'] = 0.0
    df['boredom_score'] = df['boredom_score'].round(4)
    return df

if __name__ == '__main__':
    sample_input_path = os.path.join(config.INPUT_DATA_DIR, config.DEFAULT_INPUT_FILENAME)
    if not os.path.exists(sample_input_path):
        print(f"Sample data not found. Generating it now.")
        from .data_generator import generate_ad_data
        generate_ad_data()
    else:
        print(f"Using existing sample data from {sample_input_path}")

    raw_df = pd.read_csv(sample_input_path)
    print("\nRaw data sample:")
    print(raw_df.head())

    agg_metrics = calculate_aggregated_metrics(raw_df)
    print("\nAggregated Metrics:")
    print(agg_metrics.head())

    boredom_data = calculate_boredom_score(agg_metrics)
    print("\nData with Boredom Score:")
    print(boredom_data.head())