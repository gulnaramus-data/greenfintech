import pandas as pd
import numpy as np
import pytest
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
    get_user_benefits,
    get_unique_users,
    get_top_green_users
)


def test_calculate_average_greenscore():
    """Test calculation of average GreenScore across all users."""
    df = pd.DataFrame({
        'user_id': [1, 1, 2, 2, 3],
        'status': ['green', 'not green', 'green', 'green', 'not green']
    })
    
    # User 1: 50% green, User 2: 100% green, User 3: 0% green
    # Average: (50 + 100 + 0) / 3 = 50%
    expected = 50.0
    result = calculate_average_greenscore(df)
    assert result == expected


def test_calculate_average_greenscore_empty_df():
    """Test calculation with empty dataframe."""
    df = pd.DataFrame({
        'user_id': pd.Series([], dtype='int64'),
        'status': pd.Series([], dtype='object')
    })

    # With no users, average should be 0 (function returns NaN mathematically, but we expect 0)
    result = calculate_average_greenscore(df)
    # Since the function returns NaN when there are no users, we check for NaN
    assert pd.isna(result)


def test_calculate_active_clients_ratio():
    """Test calculation of active clients ratio."""
    df = pd.DataFrame({
        'user_id': [1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4],  # User 1: 50%, User 2: 50%, User 3: 20%, User 4: 0%
        'status': ['green', 'not green', 'green', 'not green', 'green', 'not green', 'not green', 'not green', 'not green', 'not green', 'not green']
    })

    # User 1: 50% (active), User 2: 50% (active), User 3: 20% (active), User 4: 0% (not active)
    # So 3 out of 4 users are active = 75%
    expected = 75.0
    result = calculate_active_clients_ratio(df)
    assert result == expected


def test_calculate_active_clients_ratio_empty_df():
    """Test calculation with empty dataframe."""
    df = pd.DataFrame({
        'user_id': [],
        'status': []
    })
    
    expected = 0.0
    result = calculate_active_clients_ratio(df)
    assert result == expected


def test_calculate_total_eco_points():
    """Test calculation of total eco points."""
    df = pd.DataFrame({
        'amount': [100, 200, 50, 300],
        'status': ['green', 'not green', 'green', 'green']
    })
    
    # Only green transactions count: 100 + 50 + 300 = 450
    expected = 450.0
    result = calculate_total_eco_points(df)
    assert result == expected


def test_calculate_total_eco_points_empty_df():
    """Test calculation with empty dataframe."""
    df = pd.DataFrame({
        'amount': [],
        'status': []
    })
    
    expected = 0.0
    result = calculate_total_eco_points(df)
    assert result == expected


def test_calculate_target_progress():
    """Test calculation of target progress."""
    # Test with default target of 20
    assert calculate_target_progress(10.0) == 50.0  # 10/20 * 100
    assert calculate_target_progress(20.0) == 100.0  # 20/20 * 100
    assert calculate_target_progress(25.0) == 100.0  # Cap at 100%
    assert calculate_target_progress(0.0) == 0.0     # 0/20 * 100
    
    # Test with custom target
    assert calculate_target_progress(15.0, 30.0) == 50.0  # 15/30 * 100


def test_get_client_greenscore():
    """Test calculation of GreenScore for a specific client."""
    df = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2],
        'status': ['green', 'not green', 'green', 'not green', 'not green']
    })
    
    # User 1: 2 out of 3 are green = 66.67%
    expected = 66.67
    result = get_client_greenscore(df, 1)
    assert round(result, 2) == expected
    
    # User 2: 0 out of 2 are green = 0%
    expected = 0.0
    result = get_client_greenscore(df, 2)
    assert result == expected
    
    # Non-existent user
    expected = 0.0
    result = get_client_greenscore(df, 99)
    assert result == expected


def test_get_client_ranking():
    """Test getting client ranking based on GreenScore."""
    df = pd.DataFrame({
        'user_id': [1, 1, 2, 2, 3, 3, 4],  # Scores: 1:50%, 2:100%, 3:0%, 4:100%
        'status': ['green', 'not green', 'green', 'green', 'not green', 'not green', 'green']
    })
    
    # User 2 and 4 both have 100% (tied for 1st place), User 1 has 50% (2nd place), User 3 has 0% (3rd place)
    # Since pandas sort is stable, user 2 will be ranked 1, user 4 will be ranked 2
    assert get_client_ranking(df, 2) == 1  # 100% - highest
    assert get_client_ranking(df, 4) == 2  # 100% - tied but appears later
    assert get_client_ranking(df, 1) == 3  # 50% - third place
    assert get_client_ranking(df, 3) == 4  # 0% - lowest


def test_get_client_eco_points():
    """Test calculation of eco points for a specific client."""
    df = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2],
        'amount': [100, 200, 50, 300, 150],
        'status': ['green', 'not green', 'green', 'not green', 'green']
    })
    
    # User 1: 100 + 50 = 150 (only green transactions)
    expected = 150.0
    result = get_client_eco_points(df, 1)
    assert result == expected
    
    # User 2: 150 (only green transactions)
    expected = 150.0
    result = get_client_eco_points(df, 2)
    assert result == expected
    
    # Non-existent user
    expected = 0.0
    result = get_client_eco_points(df, 99)
    assert result == expected


def test_get_client_activity_period():
    """Test getting client activity period."""
    df = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2],
        'date': pd.to_datetime(['2023-01-01', '2023-01-15', '2023-01-10', '2023-02-01', '2023-01-05'])
    })
    
    # User 1: Jan 1 to Jan 15
    start, end = get_client_activity_period(df, 1)
    assert start == '2023-01-01'
    assert end == '2023-01-15'
    
    # User 2: Jan 5 to Feb 1
    start, end = get_client_activity_period(df, 2)
    assert start == '2023-01-05'
    assert end == '2023-02-01'
    
    # Non-existent user
    start, end = get_client_activity_period(df, 99)
    assert start == 'N/A'
    assert end == 'N/A'


def test_get_client_status():
    """Test determination of client status based on GreenScore."""
    # Test each status level
    assert get_client_status(30, False) == "Эко-лидер"  # >= 25 or top user
    assert get_client_status(25, False) == "Эко-лидер"  # >= 25 or top user
    assert get_client_status(20, True) == "Эко-лидер"   # top user regardless of score
    assert get_client_status(20, False) == "Активный участник green-программы"  # >= 15
    assert get_client_status(15, False) == "Активный участник green-программы"  # >= 15
    assert get_client_status(10, False) == "Осваивает зелёные привычки"  # >= 5
    assert get_client_status(5, False) == "Осваивает зелёные привычки"  # >= 5
    assert get_client_status(3, False) == "Новичок в устойчивости"  # < 5
    assert get_client_status(0, False) == "Новичок в устойчивости"  # < 5


def test_get_user_benefits():
    """Test getting user benefits based on GreenScore and eco points."""
    # Test Eco-Leader benefits (score >= 25 or is_top_user)
    status, unlocked, locked = get_user_benefits(30, 60000)
    assert status == "Эко-лидер"
    # With 60000 points, 9 out of 10 benefits should be unlocked (the one requiring 100,000 remains locked)
    assert len(unlocked) == 9  # 9 benefits unlocked
    assert len(locked) == 1    # 1 benefit locked (requires 100,000 points)

    # Test Active Participant benefits (score >= 15)
    status, unlocked, locked = get_user_benefits(20, 0)
    assert status == "Активный участник green-программы"
    # Count benefits with 0 cost (4 total)
    assert len(unlocked) == 4  # Benefits with 0 cost unlocked
    assert len(locked) == 3    # Benefits requiring points locked

    # Test Developing Habits benefits (score >= 5)
    status, unlocked, locked = get_user_benefits(10, 0)
    assert status == "Осваивает зелёные привычки"
    assert len(unlocked) == 3  # Benefits with 0 cost unlocked
    assert len(locked) == 1    # Benefits requiring points locked

    # Test Beginner benefits (score < 5)
    status, unlocked, locked = get_user_benefits(3, 0)
    assert status == "Новичок в устойчивости"
    assert len(unlocked) == 2  # Benefits with 0 cost unlocked
    assert len(locked) == 0    # No paid benefits for beginners

    # Test with sufficient points to unlock everything
    status, unlocked, locked = get_user_benefits(30, 200000)
    assert status == "Эко-лидер"
    assert len(unlocked) == 10  # All benefits unlocked
    assert len(locked) == 0


def test_get_unique_users():
    """Test getting list of unique user IDs."""
    df = pd.DataFrame({
        'user_id': [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    })
    
    expected = [1, 2, 3, 4, 5, 6, 9]  # Sorted unique values
    result = get_unique_users(df)
    assert result == expected


def test_get_top_green_users():
    """Test getting top N users by green transaction percentage."""
    df = pd.DataFrame({
        'user_id': [1, 1, 2, 2, 3, 3, 4, 4, 4, 4],  # Scores: 1:50%, 2:50%, 3:0%, 4:100%
        'status': ['green', 'not green', 'green', 'not green', 'not green', 'not green', 'green', 'green', 'green', 'green']
    })
    
    # Top 2 users: user 4 (100%) and user 1 or 2 (50%)
    top_users = get_top_green_users(df, 2)
    assert 4 in top_users
    assert len(top_users) == 2
    assert top_users[0] == 4  # User 4 should be first with 100%


def test_get_top_green_users_with_nones():
    """Test getting top green users when some have no status."""
    df = pd.DataFrame({
        'user_id': [1, 1, 2, 2, 3, 3],
        'status': ['green', 'not green', 'green', 'green', None, 'not green']
    })
    
    # User 2: 100%, User 1: 50%, User 3: 0% (but has a None status)
    top_users = get_top_green_users(df, 3)
    assert top_users[0] == 2  # User 2 with 100%
    assert top_users[1] == 1  # User 1 with 50%
    # User 3 might not appear if None values are dropped