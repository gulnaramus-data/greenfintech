import pandas as pd
import streamlit as st
from typing import Tuple, Optional


@st.cache_data
def load_transactions_data(file_path: str) -> pd.DataFrame:
    """
    Load transactions data from CSV file with caching.

    Args:
        file_path: Path to the transactions CSV file

    Returns:
        DataFrame with transactions data
    """
    df = pd.read_csv(file_path)
    # Convert date column to datetime if it exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df


@st.cache_data
def load_mcc_data(file_path: str) -> pd.DataFrame:
    """
    Load MCC codes data from CSV file with caching.

    Args:
        file_path: Path to the MCC codes CSV file

    Returns:
        DataFrame with MCC codes and their green status
    """
    df = pd.read_csv(file_path)
    return df


def merge_transaction_with_mcc(transactions_df: pd.DataFrame,
                              mcc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge transactions data with MCC codes to determine green status.

    Args:
        transactions_df: DataFrame with transaction data
        mcc_df: DataFrame with MCC codes and their green status

    Returns:
        Merged DataFrame with added status column
    """
    # Check if transactions already have a status column
    if 'status' in transactions_df.columns:
        # If status column already exists, return the dataframe as is
        return transactions_df

    # Check if the expected columns exist in mcc_df
    if 'status' not in mcc_df.columns:
        # If 'status' column doesn't exist, try to find it by other common names
        if 'green_status' in mcc_df.columns:
            mcc_df = mcc_df.rename(columns={'green_status': 'status'})
        elif 'is_green' in mcc_df.columns:
            # Convert boolean to string status
            mcc_df = mcc_df.rename(columns={'is_green': 'status'})
            mcc_df['status'] = mcc_df['status'].map({True: 'green', False: 'not green'})
        elif 'color' in mcc_df.columns:
            mcc_df = mcc_df.rename(columns={'color': 'status'})
        else:
            # If no status column exists, assume all are not green
            mcc_df = mcc_df.copy()
            mcc_df['status'] = 'not green'

    # Make sure mcc_code column exists in mcc_df
    if 'mcc_code' not in mcc_df.columns:
        if 'mcc' in mcc_df.columns:
            mcc_df = mcc_df.rename(columns={'mcc': 'mcc_code'})
        elif 'mcc_cd' in mcc_df.columns:
            mcc_df = mcc_df.rename(columns={'mcc_cd': 'mcc_code'})
        else:
            raise ValueError("MCC data must contain an 'mcc_code' column")

    # Merge transactions with MCC data to get the status
    merged_df = pd.merge(
        transactions_df,
        mcc_df[['mcc_code', 'status']],
        left_on='mcc',
        right_on='mcc_code',
        how='left'
    )

    # Fill missing status as 'not green'
    merged_df['status'] = merged_df['status'].fillna('not green')

    return merged_df


def filter_data_by_date(df: pd.DataFrame,
                       start_date: pd.Timestamp,
                       end_date: pd.Timestamp) -> pd.DataFrame:
    """
    Filter dataframe by date range.

    Args:
        df: Input dataframe with date column
        start_date: Start date for filtering
        end_date: End date for filtering

    Returns:
        Filtered dataframe
    """
    if 'date' in df.columns:
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        return df.loc[mask].copy()
    else:
        return df


def load_demo_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load demo transactions and MCC data.

    Returns:
        Tuple of (transactions_df, mcc_df)
    """
    # Load demo transactions
    transactions_df = load_transactions_data('transactions.csv')

    # Load demo MCC data
    mcc_df = load_mcc_data('mcc_new.csv')

    # The mcc_new.csv already has the correct column names: mcc_code, name, description, status
    # So no renaming is needed

    return transactions_df, mcc_df