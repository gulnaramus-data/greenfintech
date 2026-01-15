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


def get_client_status(green_score: float) -> str:
    """
    Determine client status based on GreenScore.
    
    Args:
        green_score: GreenScore of the client (0-100)
        
    Returns:
        Status string
    """
    if green_score >= 25:
        return "Эко-лидер"
    elif green_score >= 15:
        return "Активный участник green-программы"
    elif green_score >= 5:
        return "Осваивает зелёные привычки"
    else:
        return "Новичок в устойчивости"


def get_personalized_recommendations(df: pd.DataFrame, user_id: int) -> List[str]:
    """
    Generate personalized recommendations for a specific client.
    
    Args:
        df: DataFrame with transaction data
        user_id: ID of the user to analyze
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    user_transactions = df[df['user_id'] == user_id]
    
    if len(user_transactions) == 0:
        return ["Нет данных для формирования рекомендаций"]
    
    # Check for high spending in non-green categories
    non_green_transactions = user_transactions[user_transactions['status'] == 'not green']
    if len(non_green_transactions) > 0:
        top_non_green_categories = non_green_transactions.groupby('category')['amount'].sum().nlargest(3)
        
        for category, amount in top_non_green_categories.items():
            if 'кафе' in category.lower() or 'ресторан' in category.lower() or 'кофе' in category.lower():
                recommendations.append(
                    f"Вы часто покупаете кофе в одноразовых стаканчиках. "
                    f"Попробуйте кафе с системами многоразовой посуды — это добавляет +10 баллов!"
                )
                break  # Add only one recommendation for this pattern
            
            elif 'авто' in category.lower() or 'бензин' in category.lower() or 'автозаправка' in category.lower():
                recommendations.append(
                    f"Вы часто тратитесь на бензин. Рассмотрите возможность использования общественного "
                    f"транспорта или каршеринга — это может добавить до +15 баллов!"
                )
                break  # Add only one recommendation for this pattern
    
    # If no specific recommendations were generated, provide a general one
    if not recommendations:
        recommendations.append(
            "Продолжайте использовать зелёные сервисы! "
            "Каждая ваша транзакция в экологичных категориях помогает окружающей среде."
        )
    
    # Add recommendation if greenscore is low
    greenscore = get_client_greenscore(df, user_id)
    if greenscore < 10:
        recommendations.append(
            "Вы можете увеличить свой GreenScore, выбирая больше экологичных товаров и услуг. "
            "Начните с малого — например, используйте многоразовые сумки при покупках."
        )
    
    return recommendations


def get_unique_users(df: pd.DataFrame) -> List[int]:
    """
    Get a list of unique user IDs.
    
    Args:
        df: DataFrame with transaction data
        
    Returns:
        List of unique user IDs
    """
    return sorted(df['user_id'].unique().tolist())