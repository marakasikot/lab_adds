# ad_boredom_analyzer/visualization.py
"""
Generates visualizations related to ad boredom using Plotly.
"""
import plotly.express as px
import pandas as pd
import numpy as np
import os
from . import config


def plot_boredom_vs_views_plotly(analyzed_df: pd.DataFrame,
                                 selected_ad_types: list = None):
    """
    Creates an interactive scatter plot of boredom score vs. total views using Plotly.
    Can be filtered by ad_type.

    Args:
        analyzed_df (pd.DataFrame): DataFrame with 'latest_view_count', 'boredom_score',
                                    'recommendation', and 'ad_type' columns.
        selected_ad_types (list, optional): List of ad types to include in the plot.
                                            If None, all ad types are included.

    Returns:
        plotly.graph_objects.Figure: The Plotly figure object.
    """
    if not all(
            col in analyzed_df.columns for col in ['latest_view_count', 'boredom_score', 'recommendation', 'ad_type']):
        # Create an empty figure or raise error if critical columns are missing
        fig = px.scatter(title='Boredom Score vs. Total Views (Insufficient Data)')
        fig.update_layout(xaxis_title='Total Views (Latest View Count)', yaxis_title='Boredom Score')
        return fig

    plot_df = analyzed_df.copy()
    if selected_ad_types and len(selected_ad_types) > 0:
        plot_df = plot_df[plot_df['ad_type'].isin(selected_ad_types)]

    if plot_df.empty:
        fig = px.scatter(title=f'Boredom Score vs. Total Views (No data for selected types: {selected_ad_types})')
        fig.update_layout(xaxis_title='Total Views (Latest View Count)', yaxis_title='Boredom Score')
        return fig

    fig = px.scatter(
        plot_df,
        x='latest_view_count',
        y='boredom_score',
        color='recommendation',
        symbol='ad_type',  # Use symbol for ad_type
        hover_data=['user_id', 'ad_id', 'ctr', 'total_views'],
        color_discrete_map={'show': 'green', 'hide': 'red'},
        title='Boredom Score vs. Total Views per User-Ad Pair'
    )
    fig.add_hline(y=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="gray",
                  annotation_text=f'Threshold ({config.BOREDOM_THRESHOLD})', annotation_position="bottom right")
    fig.update_layout(xaxis_title='Total Views (Latest View Count)', yaxis_title='Boredom Score')
    return fig


def plot_boredom_distribution_plotly(analyzed_df: pd.DataFrame,
                                     selected_ad_types: list = None):
    """
    Creates an interactive histogram/KDE plot of boredom scores using Plotly.
    Can be filtered by ad_type.

    Args:
        analyzed_df (pd.DataFrame): DataFrame with 'boredom_score', 'recommendation', 'ad_type'.
        selected_ad_types (list, optional): List of ad types to include. If None, all.

    Returns:
        plotly.graph_objects.Figure: The Plotly figure object.
    """
    if not all(col in analyzed_df.columns for col in ['boredom_score', 'recommendation', 'ad_type']):
        fig = px.histogram(title='Distribution of Boredom Scores (Insufficient Data)')
        fig.update_layout(xaxis_title='Boredom Score', yaxis_title='Frequency')
        return fig

    plot_df = analyzed_df.copy()
    if selected_ad_types and len(selected_ad_types) > 0:
        plot_df = plot_df[plot_df['ad_type'].isin(selected_ad_types)]

    if plot_df.empty:
        fig = px.histogram(title=f'Distribution of Boredom Scores (No data for selected types: {selected_ad_types})')
        fig.update_layout(xaxis_title='Boredom Score', yaxis_title='Frequency')
        return fig

    fig = px.histogram(
        plot_df,
        x='boredom_score',
        color='recommendation',
        facet_col='ad_type' if len(plot_df['ad_type'].unique()) > 1 and len(plot_df['ad_type'].unique()) < 5 else None,
        # Facet if useful
        marginal="rug",  # or "box", "violin"
        hover_data=analyzed_df.columns,
        color_discrete_map={'show': 'green', 'hide': 'red'},
        title='Distribution of Boredom Scores'
    )
    fig.add_vline(x=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="gray",
                  annotation_text=f'Threshold ({config.BOREDOM_THRESHOLD})', annotation_position="top left")
    fig.update_layout(xaxis_title='Boredom Score', yaxis_title='Frequency')
    return fig


if __name__ == '__main__':
    # Create dummy analyzed data for Plotly
    n_samples = 200
    user_ids = [f'user_{i % 20:03}' for i in range(n_samples)]
    ad_ids = [f'ad_{i % 10:03}' for i in range(n_samples)]
    ad_types_sample = np.random.choice(config.AD_TYPES, n_samples)

    sample_analyzed_data = {
        'user_id': user_ids,
        'ad_id': ad_ids,
        'ad_type': ad_types_sample,
        'latest_view_count': np.random.randint(1, config.SATURATION_VIEW_COUNT + 5, n_samples),
        'total_views': np.random.randint(1, config.SATURATION_VIEW_COUNT + 10, n_samples),
        'total_clicks': np.random.randint(0, 5, n_samples),
        'ctr': np.random.rand(n_samples) * 0.5,  # More realistic CTRs
        'boredom_score': np.random.rand(n_samples),
    }
    test_analyzed_df = pd.DataFrame(sample_analyzed_data)
    test_analyzed_df['recommendation'] = np.where(test_analyzed_df['boredom_score'] > config.BOREDOM_THRESHOLD, 'hide',
                                                  'show')
    # Ensure ctr calculation is consistent if total_views is present
    test_analyzed_df['ctr'] = np.where(test_analyzed_df['total_views'] > 0,
                                       test_analyzed_df['total_clicks'] / test_analyzed_df['total_views'], 0).round(3)
    # Recalculate boredom score for consistency in test
    test_analyzed_df['view_factor'] = (test_analyzed_df['latest_view_count'] / config.SATURATION_VIEW_COUNT).clip(
        upper=1.0)
    test_analyzed_df['boredom_score'] = ((1 - test_analyzed_df['ctr']) * test_analyzed_df['view_factor']).round(4)
    test_analyzed_df['recommendation'] = np.where(test_analyzed_df['boredom_score'] > config.BOREDOM_THRESHOLD, 'hide',
                                                  'show')

    print("\nTest Analyzed Data for Plotly:")
    print(test_analyzed_df.head())

    fig1 = plot_boredom_vs_views_plotly(test_analyzed_df)
    # fig1.show() # In a script, this would open in a browser

    fig2 = plot_boredom_distribution_plotly(test_analyzed_df)
    # fig2.show()

    # Test filtering by ad type
    fig3 = plot_boredom_vs_views_plotly(test_analyzed_df, selected_ad_types=['video', 'banner'])
    # fig3.show()

    print("\nPlotly figures created. Run this script directly to test figure generation (requires Plotly).")
    print("In Streamlit, these figures will be displayed using st.plotly_chart().")