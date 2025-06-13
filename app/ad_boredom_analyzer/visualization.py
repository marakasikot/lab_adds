import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from . import config


def plot_boredom_vs_views_per_ad_type(analyzed_df: pd.DataFrame, ad_type_to_plot: str):
    """
    графік: Лінія середнього набридання залежно від кількості переглядів
    """
    plot_df = analyzed_df[analyzed_df['ad_type'] == ad_type_to_plot].copy()

    if plot_df.empty or 'latest_view_count' not in plot_df or 'boredom_score' not in plot_df:
        fig = go.Figure()
        fig.update_layout(
            title_text=f'Середнє набридання vs. Перегляди ({ad_type_to_plot}) - Немає даних',
            xaxis_title='Кількість переглядів',
            yaxis_title='Середня оцінка набридання'
        )
        return fig

    # Групуємо за кількістю переглядів і розраховуємо середнє, мін, макс набридання
    # Також рахуємо кількість спостережень (size) для можливого зважування або фільтрації
    agg_by_views = plot_df.groupby('latest_view_count')['boredom_score'].agg(
        mean_boredom='mean',
        min_boredom='min',
        max_boredom='max',
        count='size'  # Кількість спостережень для кожної кількості переглядів
    ).reset_index()

    # Фільтруємо ті точки, де дуже мало спостережень, щоб лінія була стабільнішою
    # Наприклад, якщо для якоїсь кількості переглядів було лише 1-2 записи
    agg_by_views_filtered = agg_by_views[agg_by_views['count'] >= 3]  # Можна налаштувати цей поріг

    if agg_by_views_filtered.empty:  # Якщо після фільтрації нічого не лишилося
        fig = go.Figure()
        fig.update_layout(
            title_text=f'Середнє набридання vs. Перегляди ({ad_type_to_plot}) - Недостатньо даних для побудови лінії',
            xaxis_title='Кількість переглядів',
            yaxis_title='Середня оцінка набридання'
        )
        return fig

    fig = go.Figure()

    #середнього набридання
    fig.add_trace(go.Scatter(
        x=agg_by_views_filtered['latest_view_count'],
        y=agg_by_views_filtered['mean_boredom'],
        mode='lines+markers',
        name='Середнє набридання',
        line=dict(color='royalblue', width=3),
        marker=dict(size=8)
    ))

    # Додаємо затінену область між min та max (як діапазон розкиду)
    fig.add_trace(go.Scatter(
        x=agg_by_views_filtered['latest_view_count'],
        y=agg_by_views_filtered['max_boredom'],
        mode='lines',
        line=dict(width=0),  # Невидима лінія для верхньої межі
        hoverinfo='skip',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=agg_by_views_filtered['latest_view_count'],
        y=agg_by_views_filtered['min_boredom'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0,100,255,0.2)',
        hoverinfo='skip',
        showlegend=False,
        name='Діапазон (мін-макс)'  # Ця назва не в легенді, але для розуміння
    ))

    fig_final = go.Figure()

    # Спочатку мін (з невидимою лінією)
    fig_final.add_trace(go.Scatter(
        x=agg_by_views_filtered['latest_view_count'],
        y=agg_by_views_filtered['min_boredom'],
        mode='lines',
        line=dict(width=0.5, color='rgba(0,100,255,0.3)'),
        hoverinfo='skip',
        showlegend=False,
        name='Мін. набридання'
    ))
    # Потім макс (з невидимою лінією і заповненням до попередньої)
    fig_final.add_trace(go.Scatter(
        x=agg_by_views_filtered['latest_view_count'],
        y=agg_by_views_filtered['max_boredom'],
        mode='lines',
        line=dict(width=0.5, color='rgba(0,100,255,0.3)'),
        fill='tonexty',
        fillcolor='rgba(0,100,255,0.15)',
        hoverinfo='skip',
        showlegend=False,
        name='Макс. набридання'
    ))
    # Потім лінію середнього (поверх заповнення)
    fig_final.add_trace(go.Scatter(
        x=agg_by_views_filtered['latest_view_count'],
        y=agg_by_views_filtered['mean_boredom'],
        mode='lines+markers',
        name='Середнє набридання',
        line=dict(color='rgb(0,0,139)', width=2.5),  # Темно-синій
        marker=dict(size=6, color='rgb(0,0,139)')
    ))

    # Горизонтальна лінія порогу набридання
    fig_final.add_hline(y=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="red",
                        line_width=2,
                        annotation_text=f'Поріг набридання ({config.BOREDOM_THRESHOLD})',
                        annotation_position="bottom right",
                        annotation_font_color="red"
                        )

    fig_final.update_layout(
        title_text=f'Середнє Набридання vs. Кількість Переглядів (Тип: {ad_type_to_plot})',
        xaxis_title='Кількість переглядів оголошення',
        yaxis_title='Оцінка набридання',
        hovermode="x unified",  # Показувати підказки для всіх ліній при наведенні на точку по X
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    # Встановлюємо діапазон для осі Y від 0 до 1 (або трохи більше, якщо є викиди)
    max_y_val = agg_by_views_filtered['max_boredom'].max() if not agg_by_views_filtered.empty else 1.0
    fig_final.update_yaxes(range=[0, min(max(1.05, max_y_val * 1.05), 1.2)])  # Обмежуємо максимум, щоб не було занадто розтягнуто

    return fig_final

def plot_boredom_distribution_per_ad_type(analyzed_df: pd.DataFrame, ad_type_to_plot: str):
    plot_df = analyzed_df[analyzed_df['ad_type'] == ad_type_to_plot]
    if plot_df.empty:
        fig = px.histogram(title=f'Розподіл набридання для {ad_type_to_plot} (Немає даних)')
        fig.update_layout(xaxis_title='Оцінка набридання', yaxis_title='Кількість пар користувач-реклама')
        return fig
    fig = px.histogram(
        plot_df, x='boredom_score', color='recommendation', marginal="violin",
        hover_data=['user_id', 'ad_id', 'latest_view_count', 'ctr'],
        color_discrete_map={'show': 'green', 'hide': 'red'},
        title=f'Розподіл набридання для типу реклами: {ad_type_to_plot}', opacity=0.75
    )
    fig.add_vline(x=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="darkgray",
                  annotation_text=f'Поріг ({config.BOREDOM_THRESHOLD})', annotation_position="top left")
    fig.update_layout(xaxis_title='Оцінка набридання', yaxis_title='Кількість пар користувач-реклама', bargap=0.1)
    return fig


def plot_user_boredom_variability(analyzed_df: pd.DataFrame, ad_type_to_plot: str, num_top_users: int = 15):
    plot_df_type = analyzed_df[analyzed_df['ad_type'] == ad_type_to_plot]
    if plot_df_type.empty:
        fig = px.box(title=f'Варіативність набридання користувачам ({ad_type_to_plot}) - Немає даних')
        return fig
    user_total_views_for_type = plot_df_type.groupby('user_id')['total_views'].sum().nlargest(num_top_users).index
    plot_df_filtered_users = plot_df_type[plot_df_type['user_id'].isin(user_total_views_for_type)]
    if plot_df_filtered_users.empty:
        fig = px.box(title=f'Варіативність набридання ({ad_type_to_plot}) - Немає даних для топ-користувачів')
        return fig
    median_boredom = plot_df_filtered_users.groupby('user_id')['boredom_score'].median()
    sorted_user_ids_by_median_boredom = median_boredom.sort_values(ascending=False).index
    fig = go.Figure()
    for i, user_id_val in enumerate(sorted_user_ids_by_median_boredom):
        user_data = plot_df_filtered_users[plot_df_filtered_users['user_id'] == user_id_val]
        current_color = '#FF6347' if median_boredom.get(user_id_val, 0) > config.BOREDOM_THRESHOLD else '#32CD32'
        fig.add_trace(go.Box(
            y=user_data['boredom_score'], name=user_id_val, boxpoints=False,
            marker_color=current_color, line_color='rgb(7,40,89)'
        ))
    fig.add_hline(y=config.BOREDOM_THRESHOLD, line_dash="dash", line_color="darkgray",
                  annotation_text=f'Поріг ({config.BOREDOM_THRESHOLD})', annotation_position="bottom right")
    fig.update_layout(
        title_text=f'Варіативність набридання для Топ-{num_top_users} користувачів (Тип: {ad_type_to_plot})',
        xaxis_title='ID Користувача (відсортовано за медіанним набриданням)',
        yaxis_title='Оцінка набридання', showlegend=False,
    )
    return fig

if __name__ == '__main__':
    print("Запустіть streamlit_app.py для перегляду оновлених візуалізацій.")