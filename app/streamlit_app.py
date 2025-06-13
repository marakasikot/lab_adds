import streamlit as st
import pandas as pd
import os

from ad_boredom_analyzer import data_generator, metrics, model, visualization, config

st.set_page_config(layout="wide", page_title="Ad Boredom")


def run_analysis_pipeline(df_raw: pd.DataFrame, saturation_pt: int, boredom_thresh: float):
    if df_raw.empty:
        st.warning("Неможливо провести аналіз на порожніх даних.")
        return "empty_input", pd.DataFrame()

    # Перевірка необхідних колонок
    required_cols = ['user_id', 'ad_id', 'ad_type', 'view_time', 'clicked', 'view_count', 'date']
    if not all(col in df_raw.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df_raw.columns]
        st.error(f"Помилка: Вхідний CSV файл не містить необхідні колонки: {', '.join(missing)}")
        st.info(f"Очікувані колонки: {', '.join(required_cols)}")
        return "missing_columns", pd.DataFrame()

    try:
        df_agg = metrics.calculate_aggregated_metrics(df_raw)
        df_boredom = metrics.calculate_boredom_score(df_agg, saturation_point=saturation_pt)
        df_recs = model.get_recommendations(df_boredom, threshold=boredom_thresh)
        return "success", df_recs
    except ValueError as e:
        st.error(f"Помилка під час обробки даних: {e}")
        return "processing_error", pd.DataFrame()
    except Exception as e:
        st.error(f"Неочікувана помилка під час аналізу: {e}")
        return "unexpected_error", pd.DataFrame()


if 'raw_data' not in st.session_state: st.session_state.raw_data = pd.DataFrame()
if 'analyzed_data' not in st.session_state: st.session_state.analyzed_data = pd.DataFrame()
if 'analysis_status' not in st.session_state: st.session_state.analysis_status = None
if 'selected_ad_type_for_display' not in st.session_state: st.session_state.selected_ad_type_for_display = None

st.title("🎯Набридання Реклами")
st.markdown("Інструмент для аналізу набридання реклами, отримання рекомендацій та візуалізації.")

# --- Sidebar ---
st.sidebar.header("⚙️ Налаштування та Керування")

st.sidebar.subheader("1. Вхідні Дані")
input_method = st.sidebar.radio("Оберіть джерело даних:", ("Згенерувати Демо-Дані", "Завантажити CSV"))

if input_method == "Згенерувати Демо-Дані":
    st.sidebar.markdown("---")
    gen_ad_types = st.sidebar.multiselect("Оберіть типи реклами для генерації:", options=config.AD_TYPES,
                                          default=config.AD_TYPES)
    num_users_gen = st.sidebar.slider("Кількість користувачів:", 100, config.NUM_USERS, config.NUM_USERS, 100)
    approx_recs_total = config.NUM_RECORDS_TO_GENERATE
    if gen_ad_types:  # Розрахунок на тип, тільки якщо типи обрані
        num_records_gen_per_type = st.sidebar.slider(
            f"Приблизна к-сть записів на тип реклами (всього ~{approx_recs_total}):",
            100, (approx_recs_total // len(gen_ad_types) if gen_ad_types else approx_recs_total) * 2,
            (approx_recs_total // len(gen_ad_types) if gen_ad_types else approx_recs_total),
            100
        )
    else:
        st.sidebar.warning("Оберіть типи реклами для налаштування кількості записів.")
        num_records_gen_per_type = approx_recs_total // len(config.AD_TYPES)

    if st.sidebar.button("Згенерувати Дані", key="generate_data_btn"):
        if not gen_ad_types:
            st.sidebar.error("Оберіть хоча б один тип реклами для генерації.")
        else:
            with st.spinner("Генерація даних..."):
                gen_file_path = data_generator.generate_ad_data(
                    num_records_approx_per_type=num_records_gen_per_type,
                    num_users=num_users_gen,
                    num_ads_per_type=config.NUM_ADS_PER_TYPE,
                    ad_types=gen_ad_types,
                    filename=f"generated_views_{'_'.join(gen_ad_types)}.csv"  # Унікальне ім'я файлу
                )
                st.session_state.raw_data = pd.read_csv(gen_file_path)
                st.session_state.analyzed_data = pd.DataFrame()
                st.session_state.analysis_status = None
                st.sidebar.success(f"Згенеровано {len(st.session_state.raw_data)} записів.")
elif input_method == "Завантажити CSV":
    st.sidebar.markdown("---")
    uploaded_file = st.sidebar.file_uploader("Завантажте ваш ad_views.csv", type=["csv"])
    if uploaded_file is not None:
        try:
            st.session_state.raw_data = pd.read_csv(uploaded_file)
            st.session_state.analyzed_data = pd.DataFrame()
            st.session_state.analysis_status = None
            st.sidebar.success("CSV файл успішно завантажено!")
        except Exception as e:
            st.sidebar.error(f"Помилка читання CSV: {e}")
            st.session_state.raw_data = pd.DataFrame()

st.sidebar.markdown("---")
st.sidebar.subheader("2. Параметри Аналізу")
saturation_point = st.sidebar.slider("К-сть переглядів для насичення:", 3, 50, config.SATURATION_VIEW_COUNT, 1)
boredom_threshold_input = st.sidebar.slider("Поріг набридання для 'hide':", 0.1, 1.0, config.BOREDOM_THRESHOLD, 0.05)

# --- Основна Частина ---
if not st.session_state.raw_data.empty:
    st.subheader("📋 Попередній перегляд необроблених даних")
    st.dataframe(st.session_state.raw_data.head())
    st.markdown(f"*Загалом завантажено записів: {len(st.session_state.raw_data)}*")

    # Перевірка наявності колонки ad_type
    if 'ad_type' not in st.session_state.raw_data.columns:
        st.error("У завантажених даних відсутній обов'язковий стовпець 'ad_type'. Будь ласка, перевірте файл.")
        st.stop()  # Зупиняємо виконання, якщо критичної колонки немає

    available_types_in_data = sorted(list(st.session_state.raw_data['ad_type'].unique()))

    if not available_types_in_data:
        st.warning("У завантажених даних стовпець 'ad_type' порожній. Аналіз за типами неможливий.")
    else:
        # Обираємо тип для відображення після аналізу
        st.session_state.selected_ad_type_for_display = st.selectbox(
            "Оберіть тип реклами для детального перегляду результатів та візуалізації:",
            options=available_types_in_data,
            index=0 if available_types_in_data else -1,  # Уникнення помилки, якщо список порожній
            key="type_display_selector"
        )

        if st.button("🚀 Провести Повний Аналіз (для всіх завантажених типів)", key="run_analysis_all_btn"):
            with st.spinner("Аналіз даних... Це може зайняти деякий час для великих датасетів."):
                status, result_df = run_analysis_pipeline(
                    st.session_state.raw_data,
                    saturation_point,
                    boredom_threshold_input
                )
                st.session_state.analysis_status = status
                st.session_state.analyzed_data = result_df

            if st.session_state.analysis_status == "success" and not st.session_state.analyzed_data.empty:
                st.success("Аналіз успішно завершено для всіх типів реклами в датасеті!")
            elif st.session_state.analysis_status == "success" and st.session_state.analyzed_data.empty:
                st.warning("Аналіз завершено, але результати порожні. Перевірте дані.")
            # Повідомлення про помилки вже виводяться в run_analysis_pipeline

if st.session_state.analysis_status == "success" and not st.session_state.analyzed_data.empty:

    selected_type = st.session_state.selected_ad_type_for_display  # Тип, обраний користувачем

    st.subheader(f"📊 Результати Аналізу та Рекомендації (Тип: {selected_type or 'Не обрано'})")

    if selected_type:
        df_display = st.session_state.analyzed_data[st.session_state.analyzed_data['ad_type'] == selected_type]
    else:  # Якщо тип не обраний (не мало б статися, але про всяк випадок)
        df_display = st.session_state.analyzed_data
        st.info("Тип реклами для детального перегляду не обрано. Показуються агреговані дані або дані першого типу.")

    if df_display.empty and selected_type:
        st.info(
            f"Немає проаналізованих даних для типу '{selected_type}'. Можливо, цей тип не був у вихідних даних або аналіз ще не проведено.")
    elif not df_display.empty:
        hidden_ads_count = df_display[df_display['recommendation'] == 'hide'].shape[0]
        total_analyzed_pairs_for_type = len(df_display)

        if total_analyzed_pairs_for_type > 0:  # Щоб уникнути ділення на нуль
            percentage_hidden = hidden_ads_count / total_analyzed_pairs_for_type * 100
            if hidden_ads_count > 0:
                st.warning(f"""
                **🚨 Увага! Набридання Реклами!**
                Для типу реклами **'{selected_type}'**:
                - **{hidden_ads_count} з {total_analyzed_pairs_for_type}** ({percentage_hidden:.1f}%) пар користувач-реклама перетнули поріг набридання ({boredom_threshold_input:.2f}).

                **Пропозиції щодо вирішення:**
                1.  **Зменшити частоту показів** для користувачів та реклам, що набридли (див. таблицю).
                2.  **Тимчасово призупинити** ці оголошення для відповідних користувачів.
                3.  **Замінити креативи** для реклам з низьким CTR та високим набриданням.
                4.  **Розглянути зміну типу реклами** для користувачів, які ігнорують поточний тип.
                5.  **Переглянути націлювання (таргетинг)**.
                """)
            else:
                st.success(f"""
                👍 **Добре!** Для типу реклами '{selected_type}' всі {total_analyzed_pairs_for_type} проаналізовані пари користувач-реклама 
                знаходяться нижче порогу набридання.
                """)
        else:
            st.info(f"Для типу реклами '{selected_type}' немає даних для відображення сповіщень.")

        st.dataframe(df_display)

        col1, col2 = st.columns(2)
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        col1.download_button(label="📥 Завантажити CSV (для обраного типу)", data=csv_data,
                             file_name=f"recs_{selected_type}.csv", mime='text/csv')
        json_data = df_display.to_json(orient="records", indent=4).encode('utf-8')
        col2.download_button(label="📥 Завантажити JSON (для обраного типу)", data=json_data,
                             file_name=f"recs_{selected_type}.json", mime='application/json')

        st.markdown("---")
        st.subheader(f"📈 Візуалізації для типу: {selected_type}")

        tab1, tab2, tab3 = st.tabs(
            ["Набридання vs. Перегляди", "Розподіл Набридання", "Набридання Різним Користувачам"])

        with tab1:
            st.plotly_chart(
                visualization.plot_boredom_vs_views_per_ad_type(st.session_state.analyzed_data, selected_type),
                use_container_width=True)
        with tab2:
            st.plotly_chart(
                visualization.plot_boredom_distribution_per_ad_type(st.session_state.analyzed_data, selected_type),
                use_container_width=True)
        with tab3:
            st.plotly_chart(visualization.plot_user_boredom_variability(st.session_state.analyzed_data, selected_type,
                num_top_users=10),
                use_container_width=True)
            st.caption(
                f"Розподіл оцінок набридання для {10} найбільш активних користувачів (за кількістю унікальних реклам типу '{selected_type}').")
    else:
        st.info("Результати аналізу для обраного типу порожні або тип не обрано.")

# Розділ "Керування Рекламною Стратегією"
st.sidebar.markdown("---")
st.sidebar.subheader("3. Керування Рекламною Стратегією (Концепт)")
with st.sidebar.expander("Моделювання змін (спрощене)"):
    st.info("Цей розділ є концептуальним і показує, як можна було б моделювати вплив змін.")

    if st.session_state.analysis_status == "success" and not st.session_state.analyzed_data.empty and st.session_state.selected_ad_type_for_display:
        selected_type_strat = st.session_state.selected_ad_type_for_display
        current_type_data_strat = st.session_state.analyzed_data[
            st.session_state.analyzed_data['ad_type'] == selected_type_strat]

        if not current_type_data_strat.empty:
            avg_ctr_current = current_type_data_strat['ctr'].mean()
            avg_boredom_current = current_type_data_strat['boredom_score'].mean()
            st.write(f"**Поточний тип: {selected_type_strat}**")
            st.write(f"- Середній CTR: {avg_ctr_current:.3f}")
            st.write(f"- Середнє набридання: {avg_boredom_current:.3f}")

            change_impressions = st.slider("Змінити кількість показів (у %):", -50, 50, 0, 5,
                                           key=f"slider_impressions_{selected_type_strat}")

            sim_ctr_change = 0
            sim_boredom_change = 0
            if change_impressions < 0:
                sim_ctr_change = abs(change_impressions) * 0.001
                sim_boredom_change = change_impressions * 0.002
            elif change_impressions > 0:
                sim_ctr_change = - (change_impressions * 0.0005)
                sim_boredom_change = change_impressions * 0.003

            simulated_ctr = avg_ctr_current + sim_ctr_change
            simulated_boredom = avg_boredom_current + sim_boredom_change

            st.metric(label="Симульований середній CTR", value=f"{simulated_ctr:.3f}",
                      delta=f"{sim_ctr_change:.3f} vs поточний")
            st.metric(label="Симульоване середнє набридання", value=f"{simulated_boredom:.3f}",
                      delta=f"{sim_boredom_change:.3f} vs поточне")

            other_types_strat = [t for t in config.AD_TYPES if t != selected_type_strat]
            if other_types_strat:
                replace_with_type = st.selectbox("Порівняти з ефективністю (якщо замінити на):",
                                                 options=other_types_strat, key=f"select_replace_{selected_type_strat}")
                if replace_with_type:
                    replacement_type_data_strat = st.session_state.analyzed_data[
                        st.session_state.analyzed_data['ad_type'] == replace_with_type]
                    if not replacement_type_data_strat.empty:
                        avg_ctr_replacement = replacement_type_data_strat['ctr'].mean()
                        avg_boredom_replacement = replacement_type_data_strat['boredom_score'].mean()
                        st.write(f"**Якщо замінити на: {replace_with_type}**")
                        st.write(f"- Середній CTR: {avg_ctr_replacement:.3f}")
                        st.write(f"- Середнє набридання: {avg_boredom_replacement:.3f}")
                    else:
                        st.write(f"Немає даних для аналізу типу '{replace_with_type}'.")
        else:
            st.write(f"Немає проаналізованих даних для типу '{selected_type_strat}', щоб моделювати стратегію.")
    else:
        st.write("Проведіть аналіз, щоб побачити опції моделювання.")

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Як Користуватися")
with st.sidebar.expander("Інструкція"):
    st.markdown("""
    1.  **Оберіть Джерело Даних:** Згенеруйте демо-дані або завантажте свій CSV.
        *   **Генерація:** Оберіть типи реклами, к-сть користувачів та записів, натисніть "Згенерувати".
        *   **Завантаження:** Ваш CSV має містити колонки: `user_id, ad_id, ad_type, view_time, clicked, view_count, date`.
    2.  **Налаштуйте Параметри Аналізу** (за бажанням).
    3.  **Оберіть Тип Реклами для Детального Перегляду** у головній частині (після завантаження/генерації даних).
    4.  **Натисніть "Провести Повний Аналіз"**. Аналіз проводиться для всіх даних, але результати та графіки будуть деталізовані для обраного типу.
    5.  **Перегляньте Результати:** Сповіщення, таблицю з рекомендаціями та інтерактивні візуалізації.
    6.  **Моделювання Стратегії (Концепт):** У бічній панелі можна спробувати змоделювати вплив зміни показів або порівняти з іншими типами реклами.
    """)

