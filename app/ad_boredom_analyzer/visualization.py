import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import numpy as np
from . import config


def plot_boredom_vs_views(analyzed_df: pd.DataFrame, output_dir: str = config.OUTPUT_DATA_DIR,
                          filename: str = config.BOREDOM_VS_VIEWS_PLOT_FILENAME):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, filename)

    if not all(col in analyzed_df.columns for col in ['latest_view_count', 'boredom_score', 'recommendation']):
        print(
            "Warning: DataFrame for plotting is missing one of 'latest_view_count', 'boredom_score', 'recommendation'. Plotting with available data.")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=analyzed_df,
        x='latest_view_count',
        y='boredom_score',
        hue='recommendation' if 'recommendation' in analyzed_df.columns else None,
        palette={'show': 'green', 'hide': 'red'} if 'recommendation' in analyzed_df.columns else None,
        alpha=0.7
    )
    plt.title('Boredom Score vs. Total Views per User-Ad Pair')
    plt.xlabel('Total Views (Latest View Count)')
    plt.ylabel('Boredom Score')
    if 'recommendation' in analyzed_df.columns:
        plt.axhline(y=config.BOREDOM_THRESHOLD, color='gray', linestyle='--',
                    label=f'Threshold ({config.BOREDOM_THRESHOLD})')
        plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")


def plot_boredom_distribution(analyzed_df: pd.DataFrame, output_dir: str = config.OUTPUT_DATA_DIR,
                              filename: str = config.BOREDOM_DISTRIBUTION_PLOT_FILENAME):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, filename)

    if not all(col in analyzed_df.columns for col in ['boredom_score', 'recommendation']):
        print(
            "Warning: DataFrame for plotting is missing one of 'boredom_score', 'recommendation'. Plotting with available data.")

    plt.figure(figsize=(10, 6))
    sns.histplot(
        data=analyzed_df,
        x='boredom_score',
        hue='recommendation' if 'recommendation' in analyzed_df.columns else None,
        palette={'show': 'green', 'hide': 'red'} if 'recommendation' in analyzed_df.columns else None,
        kde=True,
        bins=20
    )
    plt.title('Distribution of Boredom Scores')
    plt.xlabel('Boredom Score')
    plt.ylabel('Frequency')
    if 'recommendation' in analyzed_df.columns:
        plt.axvline(x=config.BOREDOM_THRESHOLD, color='gray', linestyle='--',
                    label=f'Threshold ({config.BOREDOM_THRESHOLD})')
        plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")


if __name__ == '__main__':

    sample_analyzed_data = {
        'user_id': [f'user_{i}' for i in range(50)],
        'ad_id': [f'ad_{i % 5}' for i in range(50)],
        'latest_view_count': np.random.randint(1, 20, 50),
        'boredom_score': np.random.rand(50),
        'recommendation': np.random.choice(['show', 'hide'], 50)
    }
    test_analyzed_df = pd.DataFrame(sample_analyzed_data)
    test_analyzed_df.loc[test_analyzed_df['boredom_score'] <= config.BOREDOM_THRESHOLD, 'recommendation'] = 'show'
    test_analyzed_df.loc[test_analyzed_df['boredom_score'] > config.BOREDOM_THRESHOLD, 'recommendation'] = 'hide'

    print("\nTest Analyzed Data:")
    print(test_analyzed_df.head())

    plot_boredom_vs_views(test_analyzed_df)
    plot_boredom_distribution(test_analyzed_df)
    print("\nCheck the 'output/' directory for plots.")