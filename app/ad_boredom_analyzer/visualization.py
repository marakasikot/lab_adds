# ad_boredom_analyzer/visualization.py
import plotly.express as px
import pandas as pd
from . import config


def plot_boredom_vs_views_per_ad_type(analyzed_df: pd.DataFrame, ad_type_to_plot: str):
    """
    Створює інтерактивний scatter plot набридання vs. перегляди для КОНКРЕТНОГО типу реклами.
    """
    # Фільтруємо дані перед тим, як щось робити
    plot_df = analyzed_df[analyzed_df['ad_type'] == ad_type_to_plot]

    if plot_df.empty:
        fig = px.scatter(title=f'Набридання vs. Перегляди для {ad_type_to_plot} (Немає даних)')
        fig.update_layout(xaxis_title='Останній номер перегляду', yaxis_title='Оцінка набридання')
        return fig

    fig = px.scatter(
        plot_df,
        x='latest_view_count',
        y='boredom_score',
        color='recommendation',
        hover_data=['user_id', 'ad_id', 'ctr', 'total_views'],
        color_discrete_map={'show': 'green', 'hide': 'red'},
        title=f'Набридання vs. Перегляди для типу реклами: {ad_type_to_plot}'
    )
    fig.add_hline(y=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="gray",
                  annotation_text=f'Поріг ({config.BOREDOM_THRESHOLD})', annotation_position="bottom right")
    fig.update_layout(xaxis_title='Останній номер перегляду', yaxis_title='Оцінка набридання')
    return fig


def plot_boredom_distribution_per_ad_type(analyzed_df: pd.DataFrame, ad_type_to_plot: str):
    """
    Створює інтерактивний histogram/KDE набридання для КОНКРЕТНОГО типу реклами.
    """
    plot_df = analyzed_df[analyzed_df['ad_type'] == ad_type_to_plot]

    if plot_df.empty:
        fig = px.histogram(title=f'Розподіл набридання для {ad_type_to_plot} (Немає даних)')
        fig.update_layout(xaxis_title='Оцінка набридання', yaxis_title='Частота')
        return fig

    fig = px.histogram(
        plot_df,
        x='boredom_score',
        color='recommendation',
        marginal="rug",
        hover_data=plot_df.columns,
        color_discrete_map={'show': 'green', 'hide': 'red'},
        title=f'Розподіл набридання для типу реклами: {ad_type_to_plot}'
    )
    fig.add_vline(x=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="gray",
                  annotation_text=f'Поріг ({config.BOREDOM_THRESHOLD})', annotation_position="top left")
    fig.update_layout(xaxis_title='Оцінка набридання', yaxis_title='Частота')
    return fig


def plot_user_boredom_variability(analyzed_df: pd.DataFrame, ad_type_to_plot: str, num_top_users: int = 20):
    """
    Показує варіативність набридання для різних користувачів (для конкретного типу реклами).
    Відображає box plot оцінок набридання для N найбільш активних користувачів.
    """
    plot_df_type = analyzed_df[analyzed_df['ad_type'] == ad_type_to_plot]

    if plot_df_type.empty:
        fig = px.box(title=f'Варіативність набридання користувачам ({ad_type_to_plot}) - Немає даних')
        return fig

    user_activity = plot_df_type.groupby('user_id')['ad_id'].nunique().nlargest(num_top_users).index
    plot_df_filtered_users = plot_df_type[plot_df_type['user_id'].isin(user_activity)]

    if plot_df_filtered_users.empty:
        fig = px.box(title=f'Варіативність набридання ({ad_type_to_plot}) - Немає даних для топ-користувачів')
        return fig

    fig = px.box(
        plot_df_filtered_users,
        x='user_id',
        y='boredom_score',
        color='user_id',
        points="all",
        title=f'Варіативність набридання для Топ-{num_top_users} активних користувачів (Тип: {ad_type_to_plot})'
    )
    fig.add_hline(y=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="gray",
                  annotation_text=f'Поріг ({config.BOREDOM_THRESHOLD})', annotation_position="bottom right")
    fig.update_layout(xaxis_title='ID Користувача (відсортовано за медіанним набриданням)',
                      yaxis_title='Оцінка набридання', showlegend=False)
    # Сортування по медіані, щоб візуально бачити "найбільш набридливих" користувачів
    # Для цього потрібно розрахувати медіани та передати їх у categoryorder
    median_boredom_per_user = plot_df_filtered_users.groupby('user_id')['boredom_score'].median().sort_values(
        ascending=False).index
    fig.update_xaxes(categoryorder='array', categoryarray=median_boredom_per_user)
    return fig


if __name__ == '__main__':
    print("Запустіть streamlit_app.py для перегляду оновлених візуалізацій.")