import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


def calculate_average_greenscore(df: pd.DataFrame) -> float:
    """
    Calculate the average GreenScore across all users.
    
    Args:
        df: DataFrame with transaction data including 'user_id' and 'status' columns
        
    Returns:
        Average GreenScore as a percentage
    """
    # Calculate green percentage for each user
    user_stats = df.groupby('user_id')['status'].apply(
        lambda x: (x == 'green').sum() / len(x) * 100
    ).reset_index()
    user_stats.columns = ['user_id', 'green_percentage']
    
    # Return average of all user percentages
    return user_stats['green_percentage'].mean()


def calculate_active_clients_ratio(df: pd.DataFrame) -> float:
    """
    Calculate the ratio of active clients (with >= 20% green transactions).
    
    Args:
        df: DataFrame with transaction data including 'user_id' and 'status' columns
        
    Returns:
        Ratio of active clients as a percentage
    """
    # Calculate green percentage for each user
    user_stats = df.groupby('user_id')['status'].apply(
        lambda x: (x == 'green').sum() / len(x) * 100
    ).reset_index()
    user_stats.columns = ['user_id', 'green_percentage']
    
    # Count users with >= 20% green transactions
    active_users = user_stats[user_stats['green_percentage'] >= 20]
    
    # Return ratio as percentage
    return (len(active_users) / len(user_stats)) * 100 if len(user_stats) > 0 else 0


def calculate_total_eco_points(df: pd.DataFrame) -> float:
    """
    Calculate the total eco points awarded for green transactions.
    
    Args:
        df: DataFrame with transaction data including 'amount' and 'status' columns
        
    Returns:
        Total eco points
    """
    # Filter for green transactions only
    green_transactions = df[df['status'] == 'green']
    
    # Sum the amounts for green transactions (1 eco-point per 1 ruble)
    total_eco_points = green_transactions['amount'].sum()
    
    return total_eco_points


def calculate_target_progress(current_greenscore: float, target_greenscore: float = 20.0) -> float:
    """
    Calculate the progress toward the strategic target GreenScore.
    
    Args:
        current_greenscore: Current average GreenScore
        target_greenscore: Target GreenScore (default 20)
        
    Returns:
        Progress toward target as a percentage
    """
    return min((current_greenscore / target_greenscore) * 100, 100)


def get_client_greenscore(df: pd.DataFrame, user_id: int) -> float:
    """
    Calculate GreenScore for a specific client.
    
    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze
        
    Returns:
        GreenScore as a percentage (0-100)
    """
    user_transactions = df[df['user_id'] == user_id]
    
    if len(user_transactions) == 0:
        return 0.0
    
    green_count = (user_transactions['status'] == 'green').sum()
    total_count = len(user_transactions)
    
    return (green_count / total_count) * 100


def get_client_ranking(df: pd.DataFrame, user_id: int) -> int:
    """
    Get the ranking of a specific client based on GreenScore.
    
    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze
        
    Returns:
        Ranking position (1 being the highest)
    """
    # Calculate GreenScore for all users
    user_scores = df.groupby('user_id')['status'].apply(
        lambda x: (x == 'green').sum() / len(x) * 100
    ).reset_index()
    user_scores.columns = ['user_id', 'greenscore']
    
    # Sort by GreenScore in descending order
    user_scores = user_scores.sort_values(by='greenscore', ascending=False).reset_index(drop=True)
    
    # Find the rank of the specified user
    try:
        user_rank = user_scores[user_scores['user_id'] == user_id].index[0] + 1
        return user_rank
    except IndexError:
        # If user not found, return a default rank
        return len(user_scores) + 1


def get_client_eco_points(df: pd.DataFrame, user_id: int) -> float:
    """
    Calculate eco points for a specific client.
    
    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze
        
    Returns:
        Total eco points for the client
    """
    user_transactions = df[(df['user_id'] == user_id) & (df['status'] == 'green')]
    return user_transactions['amount'].sum()


def get_client_activity_period(df: pd.DataFrame, user_id: int) -> Tuple[str, str]:
    """
    Get the activity period (first and last transaction dates) for a specific client.
    
    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze
        
    Returns:
        Tuple of (first_date, last_date) as strings
    """
    user_transactions = df[df['user_id'] == user_id]
    
    if len(user_transactions) == 0:
        return ("N/A", "N/A")
    
    first_date = user_transactions['date'].min().strftime('%Y-%m-%d')
    last_date = user_transactions['date'].max().strftime('%Y-%m-%d')
    
    return (first_date, last_date)


def get_client_status(green_score: float, is_top_user: bool = False) -> str:
    """
    Determine client status based on GreenScore and top user status.

    Args:
        green_score: GreenScore of the client (0-100)
        is_top_user: Whether the user is in the top 5 green users (default False)

    Returns:
        Status string
    """
    if is_top_user or green_score >= 25:
        return "Эко-лидер"
    elif green_score >= 15:
        return "Активный участник green-программы"
    elif green_score >= 5:
        return "Осваивает зелёные привычки"
    else:
        return "Новичок в устойчивости"


def get_user_benefits(green_score: float, eco_points: int, is_top_user: bool = False) -> Tuple[str, List[str], List[str]]:
    """
    Get benefits available to a user based on their GreenScore and eco points.

    Args:
        green_score: GreenScore of the user (0-100)
        eco_points: Number of eco points earned
        is_top_user: Whether the user is in the top 5 green users

    Returns:
        Tuple of (status, unlocked benefits, locked benefits)
    """
    # Determine status based on GreenScore and top user status
    if is_top_user or green_score >= 25:
        status = "Эко-лидер"
        available = [
            ("📉 -0.3% по «зелёному» автокредиту", 10_000),
            ("🧑‍💼 Персональный ESG-консультант", 50_000),
            ("🌍 Участие в закрытых экопроектах", 100_000),
            ("📈 +0.3% по «зелёному» вкладу", 5_000),
            ("🚗 Сертификат на тест-драйв ЭМ", 2_000),
            ("💳 Бесплатное обслуживание Green Card", 0),
            ("🚲 Месяц велопроката", 1_000),
            ("📊 Персональный ESG-отчёт", 0),
            ("🌱 Советы по «зелёным» покупкам", 0),
            ("🏆 Доступ к рейтингу GreenScore", 0)
        ]
    elif green_score >= 15:
        status = "Активный участник green-программы"
        available = [
            ("📈 +0.3% по «зелёному» вкладу", 5_000),
            ("🚗 Сертификат на тест-драйв ЭМ", 2_000),
            ("💳 Бесплатное обслуживание Green Card", 0),
            ("🚲 Месяц велопроката", 1_000),
            ("📊 Персональный ESG-отчёт", 0),
            ("🌱 Советы по «зелёным» покупкам", 0),
            ("🏆 Доступ к рейтингу GreenScore", 0)
        ]
    elif green_score >= 5:
        status = "Осваивает зелёные привычки"
        available = [
            ("🚲 Месяц велопроката", 1_000),
            ("📊 Персональный ESG-отчёт", 0),
            ("🌱 Советы по «зелёным» покупкам", 0),
            ("🏆 Доступ к рейтингу GreenScore", 0)
        ]
    else:
        status = "Новичок в устойчивости"
        available = [
            ("🌱 Советы по «зелёным» покупкам", 0),
            ("🏆 Доступ к рейтингу GreenScore", 0)
        ]

    # Filter benefits that the user can afford
    unlocked = [name for name, cost in available if eco_points >= cost]
    locked = [f"{name} (нужно ещё {cost - eco_points:,} баллов)"
              for name, cost in available if eco_points < cost and cost > 0]

    return status, unlocked, locked


def get_unique_users(df: pd.DataFrame) -> List[int]:
    """
    Get a list of unique user IDs.

    Args:
        df: DataFrame with transaction data

    Returns:
        List of unique user IDs
    """
    return sorted(df['user_id'].unique().astype(int).tolist())


def get_top_green_users(df: pd.DataFrame, n: int = 5) -> List[int]:
    """
    Get the top N users by percentage of green transactions.

    Args:
        df: DataFrame with transaction data
        n: Number of top users to return (default 5)

    Returns:
        List of top N user IDs sorted by green transaction percentage
    """
    # Calculate green percentage for each user
    user_stats = df.groupby('user_id')['status'].apply(
        lambda x: (x == 'green').sum() / len(x) * 100
    ).reset_index()
    user_stats.columns = ['user_id', 'green_percentage']

    # Sort by green percentage in descending order and return top N user IDs
    top_users = user_stats.nlargest(n, 'green_percentage')['user_id'].tolist()

    return top_users