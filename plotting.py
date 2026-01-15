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

    fig = px.pie(status_counts,
                 values='Count',
                 names='Status',
                 title='Доля зелёных и не зелёных транзакций',
                 color_discrete_map={'green': '#B5F299', 'not green': '#A0B4F2'})

    return fig

def create_line_chart_green_trend(df: pd.DataFrame) -> go.Figure:
    """
    Create a line chart showing the trend of green transactions over months.

    Args:
        df: DataFrame with transaction data including 'date' and 'status' columns

    Returns:
        Plotly figure object
    """
    # Extract month-year from date
    df_monthly = df.copy()
    df_monthly['month_year'] = df_monthly['date'].dt.to_period('M')

    # Calculate monthly green transaction percentage
    monthly_stats = df_monthly.groupby(['month_year', 'status']).size().unstack(fill_value=0)
    monthly_stats['total'] = monthly_stats.sum(axis=1)
    monthly_stats['green_percentage'] = (monthly_stats.get('green', 0) / monthly_stats['total']) * 100

    # Reset index and convert period back to timestamp for plotting
    monthly_stats = monthly_stats.reset_index()
    monthly_stats['date'] = monthly_stats['month_year'].dt.start_time

    fig = px.line(monthly_stats,
                  x='date',
                  y='green_percentage',
                  title='Динамика зелёных транзакций по месяцам',
                  labels={'date': 'Месяц', 'green_percentage': 'Процент зелёных транзакций'})

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

def c11(df: pd.DataFrame) -> go.Figure:
    """
    Create a BAR chart showing top 5 users by percentage of green transactions.
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

def create_user_green_score_trend(df: pd.DataFrame, user_id: int) -> go.Figure:
    """
    Create a line chart showing the personal green score trend for a specific user.

    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze

    Returns:
        Plotly figure object
    """
    # Filter data for the specific user
    user_df = df[df['user_id'] == user_id].copy()

    # Group by date and calculate green score for each day
    user_df['date_only'] = user_df['date'].dt.date
    daily_stats = user_df.groupby('date_only').agg({
        'status': lambda x: (x == 'green').sum() / len(x) * 100,  # Green percentage
        'amount': 'sum'  # Total amount
    }).reset_index()

    daily_stats.columns = ['date', 'green_percentage', 'total_amount']

    # Calculate rolling average for smoother trend
    daily_stats['rolling_avg'] = daily_stats['green_percentage'].rolling(window=7, min_periods=1).mean()

    fig = px.line(daily_stats,
                  x='date',
                  y='rolling_avg',
                  title=f'Личная динамика GreenScore пользователя {user_id}',
                  labels={'rolling_avg': 'GreenScore (%)', 'date': 'Дата'})

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