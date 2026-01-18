# 🌱 GreenScore - Green Finance Technology Platform 🌍

## 📋 Description
[English version](README_EN.md) | [Версия на русском](README.md)

GreenScore is a green finance technology platform that analyzes users' banking transactions and classifies them as "green" or "non-green" based on predefined rules and Merchant Category Codes (MCC). The application awards "eco-points" for green transactions and displays statistics and progress on a personal dashboard. This solution promotes green banking by allowing banks and their customers to track and encourage environmentally responsible purchases.

## 🎯 Purpose and Meaning of Use

- **🌱🏦 For Green Banking:** Enables banks and fintech to track and incentivize environmentally responsible actions by their customers, promoting the transition to sustainable financial practices. The recommendation system suggests environmentally-oriented banking products and services to customers based on their spending habits.
- **🌿 For Customers:** Provides the ability to track their environmental footprint through financial transactions and earn rewards for environmentally conscious lifestyle choices.
- **🌎 For Sustainability Development:** Promotes conscious consumer behavior and supports the transition to a more sustainable economy.

## 🚀 How to Run the Application

**Local Launch:**

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure `transactions.csv` and `mcc_new.csv` files are in the project root
3. Run the application: `streamlit run app.py`

**Online Version:**
You can access the application online at: https://greenscoreforgreenfintech.streamlit.app/

## 🌐 Application Link

https://greenscoreforgreenfintech.streamlit.app/

## 🏗️ Architecture

The application consists of four main Python modules:

1. **app.py**: Main Streamlit application with employee and client interfaces
2. **data_loader.py**: Handles data loading, merging transactions with MCC codes, and filtering
3. **analysis.py**: Contains functions for calculating GreenScore, eco-points, user rankings, and recommendations
4. **plotting.py**: Creates visualizations using Plotly for dashboards

## 🏆 User Statuses

Users receive status based on their GreenScore:
- **🥇 Eco-Leader (Эко-лидер)**: Top-5 green users
- **🌟 Active green program participant (Активный участник green-программы)**: 20%+ green transactions
- **🌱 Developing green habits (Осваивает зелёные привычки)**: 10-20% green transactions
- **🌿 Beginner in sustainability (Новичок в устойчивости)**: less than 10% green transactions

## 📁 Requirements for Uploaded Files

**Transaction file (transactions.csv) must contain the following columns:**
- `user_id`: User identifier (integer) 👤
- `date`: Transaction date (in YYYY-MM-DD format or other format recognizable by pandas) 📅
- `amount`: Transaction amount (number) 💰
- `merchant`: Merchant name (string) 🏪
- `category`: Transaction category (string) 📦
- `mcc`: Merchant Category Code (MCC code, integer) 🏷️

**MCC codes file (mcc_new.csv) must contain the following columns:**
- `mcc_code`: Merchant Category Code (MCC code, integer) 🏷️
- `status`: Green status (string, possible values: "green" or "not green") 🟢🔴
- `name`: Category name (optional, string) 📝
- `description`: Category description (optional, string) ℹ️

**Alternative column names accepted:**
- For MCC status: `green_status`, `is_green`, or `color` (instead of `status`) 🏷️
- For MCC code: `mcc` or `mcc_cd` (instead of `mcc_code`) 🏷️

## GitHub Actions CI/CD Setup

This project includes a GitHub Actions workflow that automatically runs tests and builds/pushes the Docker image to Docker Hub when tests pass.

## 🧪 Testing

The project includes a comprehensive test suite for the analysis module:
- **test_analysis.py**: Contains unit tests for all functions in analysis.py
- Run tests with: `python -m pytest test_analysis.py -v`

## 📊 Key Features

- **Transaction Analysis**: Analyzes user transactions and classifies them as green or non-green
- **Classification System**: Uses predefined lists of green categories and MCC codes for classification
- **Eco-Point System**: Awards 1 eco-point per 1 ruble spent in green categories, with bonuses for repeat purchases from green vendors
- **Dashboard Visualization**: Displays charts showing green transaction trends, top green categories, and user GreenScore
- **Personal Recommendations**: Provides personalized eco-friendly recommendations based on user spending patterns
- **User Profiles**: Creates user profiles with GreenScore ratings and status levels

## 🏗️ Building and Running

1. Install dependencies: `pip install streamlit pandas plotly numpy`
2. Ensure `transactions.csv` and `mcc_new.csv` are in the project root
3. Run the application: `streamlit run app.py`

## 🖥️ User Interface

The application provides two interfaces:
- **Employee Interface**: Comprehensive dashboard with overall analytics, KPIs, and client analysis
- **Client Interface**: Personal dashboard showing individual GreenScore, transaction history, and recommendations

## 📈 Key Visualizations

- Pie chart showing green vs non-green transaction proportions
- Line chart showing green transaction trends over time
- Bar charts for top green categories and users
- Personal GreenScore trends for individual users

## 🛠️ Development Notes

- The application uses Streamlit for the web interface
- Plotly is used for interactive visualizations
- Pandas is used for data manipulation and analysis
- The project includes synthetic data generation notebook (GreenFinTech.ipynb) for testing purposes
- Caching is implemented for data loading functions to improve performance
- Comprehensive unit tests are provided for the analysis module

## 🐳 Docker Support

The application can be run using Docker:
```
docker build -t greenscore .
docker run -p 8501:8501 greenscore
```

## 📚 Dependencies

The application requires the following Python packages:
- streamlit>=1.24.0
- pandas>=1.5.0
- plotly>=5.14.0
- numpy>=1.21.0

## 🎓 Academic Background

This project was developed as part of a master's thesis on "Improving processes of managing green financial technologies (green fintech) using platform IT solutions in the banking sector."