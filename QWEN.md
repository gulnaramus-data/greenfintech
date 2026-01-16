# GreenFinTech Project Overview

## Project Description
GreenFinTech is a green fintech web application called GreenScore that analyzes user transactions and classifies them as "green" or "not green" based on predefined rules, categories, and MCC (Merchant Category Codes). The application awards "eco-points" for green transactions and displays statistics and progress in a personal dashboard. This project was developed as part of a master's thesis on "Improving processes of managing green financial technologies (green fintech) using platform IT solutions in the banking sector."

## Key Features
- **Transaction Analysis**: Analyzes user transactions and classifies them as green or non-green
- **Classification System**: Uses predefined lists of green categories and MCC codes for classification
- **Eco-Point System**: Awards 1 eco-point per 1 ruble spent in green categories, with bonuses for repeat purchases from green vendors
- **Dashboard Visualization**: Displays charts showing green transaction trends, top green categories, and user GreenScore
- **Personal Recommendations**: Provides personalized eco-friendly recommendations based on user spending patterns
- **User Profiles**: Creates user profiles with GreenScore ratings and status levels

## Architecture
The application consists of four main Python modules:

1. **app.py**: Main Streamlit application with employee and client interfaces
2. **data_loader.py**: Handles data loading, merging transactions with MCC codes, and filtering
3. **analysis.py**: Contains functions for calculating GreenScore, eco-points, user rankings, and recommendations
4. **plotting.py**: Creates visualizations using Plotly for dashboards

## Data Structure
The application expects two CSV files:
- **transactions.csv**: Contains transaction data with columns: user_id, date, amount, merchant, category, mcc
- **mcc_new.csv**: Contains MCC codes with their green status (green/not green)

## Building and Running
1. Install dependencies: `pip install streamlit pandas plotly`
2. Ensure `transactions.csv` and `mcc_new.csv` are in the project root
3. Run the application: `streamlit run app.py`

## Testing
The project includes a comprehensive test suite for the analysis module:
- **test_analysis.py**: Contains unit tests for all functions in analysis.py
- Run tests with: `python -m pytest test_analysis.py -v`

## User Interface
The application provides two interfaces:
- **Employee Interface**: Comprehensive dashboard with overall analytics, KPIs, and client analysis
- **Client Interface**: Personal dashboard showing individual GreenScore, transaction history, and recommendations

## Key Visualizations
- Pie chart showing green vs non-green transaction proportions
- Line chart showing green transaction trends over time
- Bar charts for top green categories and users
- Personal GreenScore trends for individual users

## Status Levels
Users receive status based on their GreenScore:
- **Эко-лидер** (Eco-Leader): Top 5 green users
- **Активный участник green-программы** (Active green program participant): 20%+ green transactions
- **Осваивает зелёные привычки** (Developing green habits): 10-20% green transactions
- **Новичок в устойчивости** (Beginner in sustainability): Less than 10% green transactions

## Development Notes
- The application uses Streamlit for the web interface
- Plotly is used for interactive visualizations
- Pandas is used for data manipulation and analysis
- The project includes synthetic data generation notebook (GreenFinTech.ipynb) for testing purposes
- Caching is implemented for data loading functions to improve performance
- Comprehensive unit tests are provided for the analysis module