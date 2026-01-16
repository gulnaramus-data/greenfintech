import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

def create_pie_chart_green_vs_not_green(df: pd.DataFrame) -> go.Figure:
    """
    Create a pie chart showing the proportion of green vs not green transactions.

    Args:
        df: DataFrame with transaction data including 'status' column

    Returns:
        Plotly figure object
    """
    # Count green vs not green transactions
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    # Map status values to Russian labels
    status_labels = {'green': 'зелёные', 'not green': 'незелёные'}
    status_counts['StatusLabel'] = status_counts['Status'].map(status_labels)

    fig = px.pie(status_counts,
                 values='Count',
                 names='StatusLabel',
                 title='Доля зелёных и незелёных транзакций')

    # Update colors explicitly
    fig.update_traces(marker=dict(colors=['#91A0F2', '#B5F299']))

    return fig

def create_line_chart_green_trend(df: pd.DataFrame, time_period: str = "Месяцы") -> go.Figure:
    """
    Create a line chart showing the trend of green transactions over time.

    Args:
        df: DataFrame with transaction data including 'date' and 'status' columns
        time_period: Time aggregation period ("Дни", "Недели", "Месяцы")

    Returns:
        Plotly figure object
    """
    # Create a copy of the dataframe
    df_time = df.copy()

    # Convert time_period to appropriate grouping
    if time_period == "Дни":
        df_time['period'] = df_time['date'].dt.date
    elif time_period == "Недели":
        df_time['period'] = df_time['date'].dt.to_period('W')
    else:  # Месяцы
        df_time['period'] = df_time['date'].dt.to_period('M')

    # Calculate green transaction percentage by period
    period_stats = df_time.groupby(['period', 'status']).size().unstack(fill_value=0)
    period_stats['total'] = period_stats.sum(axis=1)
    period_stats['green_percentage'] = (period_stats.get('green', 0) / period_stats['total']) * 100

    # Reset index and convert period back to timestamp for plotting
    period_stats = period_stats.reset_index()
    if time_period == "Дни":
        period_stats['date_for_plot'] = pd.to_datetime(period_stats['period'])
    elif time_period == "Недели":
        period_stats['date_for_plot'] = period_stats['period'].dt.start_time
    else:  # Месяцы
        period_stats['date_for_plot'] = period_stats['period'].dt.start_time

    # Adjust title and axis label based on time period
    period_label = {
        "Дни": "дням",
        "Недели": "неделям",
        "Месяцы": "месяцам"
    }.get(time_period, time_period.lower())

    fig = px.line(period_stats,
                  x='date_for_plot',
                  y='green_percentage',
                  title=f'Динамика зелёных транзакций по {period_label}',
                  labels={'date_for_plot': time_period, 'green_percentage': 'Процент зелёных транзакций'})

    fig.update_traces(line=dict(color='#B5F299'))
    fig.update_layout(yaxis_title="Процент зелёных транзакций (%)")

    return fig


def create_bar_chart_top_green_categories(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing top 5 green categories by transaction amount.

    Args:
        df: DataFrame with transaction data including 'category', 'amount', and 'status' columns

    Returns:
        Plotly figure object
    """
    # Filter for green transactions only
    green_df = df[df['status'] == 'green']

    # Group by category and sum the amounts
    category_amounts = green_df.groupby('category')['amount'].sum().reset_index()
    category_amounts = category_amounts.sort_values(by='amount', ascending=False).head(5)

    fig = px.bar(category_amounts,
                 x='amount',
                 y='category',
                 orientation='h',
                 title='Топ-5 зелёных категорий по сумме транзакций',
                 labels={'amount': 'Сумма транзакций', 'category': 'Категория'},
                 color_discrete_sequence=['#B5F299'])

    # Reverse the y-axis to show highest values at the top
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    return fig

def create_bar_chart_top_green_users(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing top 5 users by percentage of green transactions.
    Users are sorted in descending order by green transaction percentage.
    Each bar represents one user (ID on x-axis, % on y-axis).
    """
    # Удаляем строки с пропущенным статусом (если есть)
    df_clean = df.dropna(subset=['status'])
    
    # Считаем долю зелёных транзакций по каждому пользователю
    user_green_ratio = (
        df_clean.groupby('user_id')['status']
        .apply(lambda x: (x == 'green').mean() * 100)
        .reset_index(name='green_percentage')
    )
    
    # Сортируем по убыванию и берём топ-5
    top_users = user_green_ratio.nlargest(5, 'green_percentage').copy()
    
    # ⭐️ Ключевое изменение: преобразуем user_id в строку, чтобы Plotly считал его категорией
    top_users['user_id'] = top_users['user_id'].astype(str)
    
    # Создаём столбчатую диаграмму
    fig = px.bar(
        top_users,
        x='user_id',  # теперь это строка → категория
        y='green_percentage',
        title='Топ-5 зелёных пользователей по доле зелёных транзакций',
        labels={'user_id': 'ID пользователя', 'green_percentage': 'Процент зелёных транзакций (%)'},
        color_discrete_sequence=['#B5F299']
    )
    
    # Явно указываем, что ось X — категориальная (на всякий случай)
    fig.update_xaxes(type='category')
    
    return fig

def create_user_green_score_trend(df: pd.DataFrame, user_id: int, time_period: str = "Дни") -> go.Figure:
    """
    Create a line chart showing the personal green score trend for a specific user.

    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze
        time_period: Time aggregation period ("Дни", "Недели", "Месяцы")

    Returns:
        Plotly figure object
    """
    # Filter data for the specific user
    user_df = df[df['user_id'] == user_id].copy()

    # Group by the selected time period and calculate green score
    if time_period == "Дни":
        user_df['period'] = user_df['date'].dt.date
    elif time_period == "Недели":
        user_df['period'] = user_df['date'].dt.to_period('W')
    else:  # Месяцы
        user_df['period'] = user_df['date'].dt.to_period('M')

    period_stats = user_df.groupby('period').agg({
        'status': lambda x: (x == 'green').sum() / len(x) * 100,  # Green percentage
        'amount': 'sum'  # Total amount
    }).reset_index()

    period_stats.columns = ['period', 'green_percentage', 'total_amount']

    # Calculate rolling average for smoother trend
    period_stats['rolling_avg'] = period_stats['green_percentage'].rolling(window=7, min_periods=1).mean()

    # Convert period back to datetime for plotting
    if time_period == "Дни":
        period_stats['date_for_plot'] = pd.to_datetime(period_stats['period'])
    elif time_period == "Недели":
        period_stats['date_for_plot'] = period_stats['period'].dt.start_time
    else:  # Месяцы
        period_stats['date_for_plot'] = period_stats['period'].dt.start_time

    # Adjust title based on time period
    period_label = {
        "Дни": "дням",
        "Недели": "неделям",
        "Месяцы": "месяцам"
    }.get(time_period, time_period.lower())

    fig = px.line(period_stats,
                  x='date_for_plot',
                  y='rolling_avg',
                  title=f'Личная динамика GreenScore пользователя {user_id} по {period_label}',
                  labels={'rolling_avg': 'GreenScore (%)', 'date_for_plot': time_period})

    fig.update_traces(line=dict(color='#B5F299'))
    fig.update_layout(yaxis_title="GreenScore (%)")

    return fig


def create_user_top_green_categories(df: pd.DataFrame, user_id: int) -> go.Figure:
    """
    Create a bar chart showing top 5 green categories for a specific user.

    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze

    Returns:
        Plotly figure object
    """
    # Filter for the specific user and green transactions only
    user_green_df = df[(df['user_id'] == user_id) & (df['status'] == 'green')]

    # Group by category and sum the amounts
    category_amounts = user_green_df.groupby('category')['amount'].sum().reset_index()
    category_amounts = category_amounts.sort_values(by='amount', ascending=False).head(5)

    fig = px.bar(category_amounts,
                 x='amount',
                 y='category',
                 orientation='h',
                 title=f'Топ-5 зелёных категорий транзакций пользователя {user_id}',
                 labels={'amount': 'Сумма транзакций', 'category': 'Категория'},
                 color_discrete_sequence=['#B5F299'])

    # Reverse the y-axis to show highest values at the top
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    return fig


def create_user_top_non_green_categories(df: pd.DataFrame, user_id: int) -> go.Figure:
    """
    Create a bar chart showing top 5 non-green categories for a specific user.

    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze

    Returns:
        Plotly figure object
    """
    # Filter for the specific user and non-green transactions only
    user_non_green_df = df[(df['user_id'] == user_id) & (df['status'] == 'not green')]

    # Group by category and sum the amounts
    category_amounts = user_non_green_df.groupby('category')['amount'].sum().reset_index()
    category_amounts = category_amounts.sort_values(by='amount', ascending=False).head(5)

    fig = px.bar(category_amounts,
                 x='amount',
                 y='category',
                 orientation='h',
                 title=f'Топ-5 незелёных категорий транзакций пользователя {user_id}',
                 labels={'amount': 'Сумма транзакций', 'category': 'Категория'},
                 color_discrete_sequence=['#A0B4F2'])

    # Reverse the y-axis to show highest values at the top
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    return fig