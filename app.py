import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Tuple, Optional

# Import custom modules
from data_loader import load_transactions_data, load_mcc_data, merge_transaction_with_mcc, filter_data_by_date, load_demo_data
from plotting import (
    create_pie_chart_green_vs_not_green,
    create_line_chart_green_trend,
    create_bar_chart_top_green_categories,
    create_bar_chart_top_green_users,
    create_user_green_score_trend,
    create_user_top_green_categories,
    create_user_top_non_green_categories
)
from analysis import (
    calculate_average_greenscore,
    calculate_active_clients_ratio,
    calculate_total_eco_points,
    calculate_target_progress,
    get_client_greenscore,
    get_client_ranking,
    get_client_eco_points,
    get_client_activity_period,
    get_client_status,
    get_personalized_recommendations,
    get_unique_users,
    get_top_green_users
)


def main():
    # Set page config
    st.set_page_config(
        page_title="🌱 Мониторинг и управление устойчивыми транзакциями GreenScore",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title
    st.title("🌱 Мониторинг и управление устойчивыми транзакциями GreenScore")

    # Sidebar
    st.sidebar.header("⚙️ Настройки")

    # Date range selection
    today = date.today()
    start_date = st.sidebar.date_input("📅 Начальная дата", value=date(today.year - 1, 1, 1))
    end_date = st.sidebar.date_input("📅 Конечная дата", value=today)

    # Time period filter for green transactions dynamics
    time_period = st.sidebar.selectbox("🕐 Период для анализа динамики", ["Дни", "Недели", "Месяцы"])

    # View mode selection
    view_mode = st.sidebar.selectbox("👥 Режим просмотра", ["Сотрудник", "Клиент"])

    # Data loading options
    data_source = st.sidebar.radio("📂 Источник данных", ["Демо-данные", "Загрузка данных"])

    # Initialize data
    transactions_df = None
    mcc_df = None

    if data_source == "Демо-данные":
        try:
            transactions_df, mcc_df = load_demo_data()
        except FileNotFoundError:
            st.error("Файл данных не найден. Убедитесь, что файлы transactions.csv и mcc_new.csv находятся в корне проекта.")
            st.stop()
    else:
        uploaded_transactions = st.sidebar.file_uploader("📥 Загрузите файл транзакций (CSV)", type=["csv"])
        uploaded_mcc = st.sidebar.file_uploader("📥 Загрузите файл MCC-кодов (CSV)", type=["csv"])

        if uploaded_transactions and uploaded_mcc:
            transactions_df = load_transactions_data(uploaded_transactions)
            mcc_df = load_mcc_data(uploaded_mcc)
        else:
            st.info("Пожалуйста, загрузите оба файла для продолжения работы")
            st.stop()

    # Merge data to add status column
    if transactions_df is not None and mcc_df is not None:
        # Rename columns in mcc_df to match expected schema
        mcc_df_renamed = mcc_df.rename(columns={'mcc': 'mcc_code'} if 'mcc' in mcc_df.columns else {})

        # Merge datasets
        merged_df = merge_transaction_with_mcc(transactions_df, mcc_df_renamed)

        # Filter by date range
        filtered_df = filter_data_by_date(merged_df, pd.Timestamp(start_date), pd.Timestamp(end_date))

        # Main panel based on view mode
        if view_mode == "Сотрудник":
            employee_interface(filtered_df, time_period)
        else:
            client_interface(filtered_df, time_period)


def employee_interface(df: pd.DataFrame, time_period: str = "Дни"):
    """Display the employee interface with dashboard and client analysis."""
    st.header("💼 Интерфейс сотрудника")

    # Tabs for different views
    tab1, tab2 = st.tabs(["📊 Общий дашборд", "👤 Анализ по клиенту"])

    with tab1:
        display_dashboard(df, time_period)

    with tab2:
        display_client_analysis(df, time_period)


def display_dashboard(df: pd.DataFrame, time_period: str = "Дни"):
    """Display the main dashboard with KPI cards and charts."""
    st.subheader("📊 Общий дашборд")

    # Calculate KPIs
    avg_greenscore = calculate_average_greenscore(df)
    active_clients_ratio = calculate_active_clients_ratio(df)
    total_eco_points = calculate_total_eco_points(df)
    target_progress = calculate_target_progress(avg_greenscore)

    # Display KPI cards with deltas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="📈 Средний GreenScore", value=f"{avg_greenscore:.2f}%",
                  delta=f"{avg_greenscore - 15:.2f}% от целевого значения")

    with col2:
        st.metric(label="👥 Доля активных клиентов", value=f"{active_clients_ratio:.2f}%",
                  delta=f"{active_clients_ratio - 30:.2f}% от целевого значения")

    with col3:
        st.metric(label="🌿 Количество начисленных эко-баллов", value=f"{total_eco_points:,.0f}",
                  delta=f"{total_eco_points - 500000:.0f} от целевого значения")

    with col4:
        st.metric(label="🎯 Целевой прогресс", value=f"{target_progress:.2f}%",
                  delta=f"{avg_greenscore - 20 if avg_greenscore < 20 else 0:.2f}% до цели")

    # Charts - arrange differently
    st.plotly_chart(create_pie_chart_green_vs_not_green(df), use_container_width=True)

    # Pass the selected time period to the line chart function
    st.plotly_chart(create_line_chart_green_trend(df, time_period=time_period), use_container_width=True)

    # Top green categories and users in separate rows
    st.plotly_chart(create_bar_chart_top_green_categories(df), use_container_width=True)

    # Calculate top green users table
    user_stats = df.groupby('user_id')['status'].value_counts(normalize=True).unstack(fill_value=0)
    user_stats['green_percentage'] = user_stats.get('green', 0) * 100
    top_users = user_stats.sort_values(by='green_percentage', ascending=False).head(5).reset_index()

    # Create a table showing user IDs and their green percentages
    st.subheader("🏆 Топ-5 зелёных пользователей")
    top_users_table = top_users[['user_id', 'green_percentage']].copy()
    top_users_table.columns = ['ID пользователя', 'Процент зелёных транзакций']
    top_users_table['Процент зелёных транзакций'] = top_users_table['Процент зелёных транзакций'].round(2)

    # Display the table with enhanced styling to avoid PyArrow dependency
    st.markdown("""
    <style>
    .top-users-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .top-users-table th {
        background-color: #f0f0f0;
        padding: 12px;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
    }

    .top-users-table td {
        padding: 10px;
        text-align: center;
        border-bottom: 1px solid #ddd;
    }

    .top-users-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    .top-users-table tr:hover {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create HTML table with styling
    table_html = '<table class="top-users-table">'
    table_html += '<thead><tr><th>ID пользователя</th><th>Процент зелёных транзакций</th></tr></thead><tbody>'
    for i, (_, row) in enumerate(top_users_table.iterrows()):
        bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        table_html += f'<tr style="background-color: {bg_color};"><td>{int(row["ID пользователя"])}</td><td>{row["Процент зелёных транзакций"]:.2f}</td></tr>'
    table_html += '</tbody></table>'

    st.markdown(table_html, unsafe_allow_html=True)


def display_client_analysis(df: pd.DataFrame, time_period: str = "Дни"):
    """Display client analysis section."""
    st.subheader("👤 Анализ по клиенту")

    # Get unique users for selection
    unique_users = get_unique_users(df)

    if unique_users:
        selected_user = st.selectbox("👤 Выберите клиента", unique_users)

        if selected_user:
            # Client profile
            col1, col2, col3 = st.columns(3)

            with col1:
                greenscore = get_client_greenscore(df, selected_user)
                st.metric(label="🌱 GreenScore", value=f"{greenscore:.2f}/100")

            with col2:
                ranking = get_client_ranking(df, selected_user)
                st.metric(label="🏆 Место в общем рейтинге", value=f"#{ranking}")

            with col3:
                eco_points = get_client_eco_points(df, selected_user)
                st.metric(label="🌿 Эко-баллы", value=f"{eco_points:.2f}")

            # Additional info - arrange vertically
            start_date, end_date = get_client_activity_period(df, selected_user)
            st.write(f"**📅 Период активности:** {start_date} — {end_date}")

            # Determine if the user is in the top 5 green users
            top_users = get_top_green_users(df, 5)
            is_top_user = selected_user in top_users
            status = get_client_status(greenscore, is_top_user)

            # Display status in the same style as recommendations with colored background
            st.subheader("🏷️ Статус")

            # Define color based on status level
            if status == "Эко-лидер":
                color = "#A1D991"
            elif status == "Активный участник green-программы":
                color = "#B5F299"
            elif status == "Осваивает зелёные привычки":
                color = "#A0B4F2"
            else:  # "Новичок в устойчивости"
                color = "#91A0F2"

            # Create a colored container for the status
            st.markdown(
                f"""
                <div style="
                    background-color: {color};
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 5px solid #000000;
                ">
                    <span style="font-size: 16px; font-weight: bold;">🎯 {status}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Charts for selected user - arrange differently
            st.plotly_chart(create_user_green_score_trend(df, selected_user, time_period=time_period), use_container_width=True)
            st.plotly_chart(create_user_top_green_categories(df, selected_user), use_container_width=True)

            # Top non-green categories and recommendations in separate rows
            st.plotly_chart(create_user_top_non_green_categories(df, selected_user), use_container_width=True)

            # Personalized recommendations
            st.subheader("💡 Персонализированные рекомендации")
            recommendations = get_personalized_recommendations(df, selected_user)

            # Display recommendations with colored background
            for rec in recommendations:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #B5F299;
                        padding: 10px;
                        border-radius: 5px;
                        margin-bottom: 10px;
                    ">
                        💡 {rec}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def client_interface(df: pd.DataFrame, time_period: str = "Дни"):
    """Display the client interface."""
    st.header("👤 Интерфейс клиента")

    # Get unique users for selection
    unique_users = get_unique_users(df)

    if unique_users:
        selected_user = st.selectbox("👤 Выберите клиента", unique_users)

        if selected_user:
            # Client profile
            col1, col2, col3 = st.columns(3)

            with col1:
                greenscore = get_client_greenscore(df, selected_user)
                st.metric(label="🌱 GreenScore", value=f"{greenscore:.2f}/100")

            with col2:
                ranking = get_client_ranking(df, selected_user)
                st.metric(label="🏆 Место в общем рейтинге", value=f"#{ranking}")

            with col3:
                eco_points = get_client_eco_points(df, selected_user)
                st.metric(label="🌿 Эко-баллы", value=f"{eco_points:.2f}")

            # Additional info - arrange vertically
            start_date, end_date = get_client_activity_period(df, selected_user)
            st.write(f"**📅 Период активности:** {start_date} — {end_date}")

            # Determine if the user is in the top 5 green users
            top_users = get_top_green_users(df, 5)
            is_top_user = selected_user in top_users
            status = get_client_status(greenscore, is_top_user)

            # Display status in the same style as recommendations with colored background
            st.subheader("🏷️ Статус")

            # Define color based on status level
            if status == "Эко-лидер":
                color = "#A1D991"
            elif status == "Активный участник green-программы":
                color = "#B5F299"
            elif status == "Осваивает зелёные привычки":
                color = "#A0B4F2"
            else:  # "Новичок в устойчивости"
                color = "#91A0F2"

            # Create a colored container for the status
            st.markdown(
                f"""
                <div style="
                    background-color: {color};
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 5px solid #000000;
                ">
                    <span style="font-size: 16px; font-weight: bold;">🎯 {status}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Charts for selected user - arrange differently
            st.plotly_chart(create_user_green_score_trend(df, selected_user, time_period=time_period), use_container_width=True)
            st.plotly_chart(create_user_top_green_categories(df, selected_user), use_container_width=True)

            # Top non-green categories and recommendations in separate rows
            st.plotly_chart(create_user_top_non_green_categories(df, selected_user), use_container_width=True)

            # Personalized recommendations
            st.subheader("💡 Персонализированные рекомендации")
            recommendations = get_personalized_recommendations(df, selected_user)

            # Display recommendations with colored background
            for rec in recommendations:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #B5F299;
                        padding: 10px;
                        border-radius: 5px;
                        margin-bottom: 10px;
                    ">
                        💡 {rec}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()