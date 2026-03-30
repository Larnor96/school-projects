"""
Olist E-commerce Analytics - Sales Forecasting for Assignment
==============================================================
Author: [AABLM - BID3000]
Date: November 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# 1. DATABASE CONNECTION 

def connect_to_warehouse():
    """
    Connect to PostgreSQL data warehouse
    """
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'olist',
        'user': 'postgres',
        'password': '123456'
    }
    
    connection = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    engine = create_engine(connection)
    
    print("*"*80)
    print("OLIST E-COMMERCE SALES & FORECASTING ANALYTICS")
    print("-"*80)
    print("\nconnected to dwh")
    return engine

# 2. DATA EXTRACTION

def extract_sales_data(engine):

    sales_query = """
    SELECT 
        foi.order_id,
        foi.total_price,
        dc.customer_state,
        dp.product_category_name,
        dd.full_date,
        dd.year,
        dd.month,
        dd.month_name
    FROM dwh.fact_order_items foi
    JOIN dwh.dim_customer dc ON foi.customer_key = dc.customer_key
    JOIN dwh.dim_product dp ON foi.product_key = dp.product_key
    JOIN dwh.dim_date dd ON foi.date_key = dd.date_key
    ORDER BY dd.full_date
    """
    
    print("\nsales data from warehouse")
    df_sales = pd.read_sql(sales_query, engine)
    
    print(f"Extracted {len(df_sales):,} sales records")
    print(f"Date range: {df_sales['full_date'].min()} to {df_sales['full_date'].max()}")
    
    return df_sales

# 3. DESCRIPTIVE ANALYTICS 

def descriptive_analytics(df_sales):
    
    print("\n" + "*"*80)
    print("DESCRIPTIVE ANALYTICS OF SALES DATA")
    print("-"*80)
    
    # Aggregate to monthly level for analysis
    df_monthly = df_sales.groupby(['year', 'month', 'month_name']).agg({
        'total_price': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    df_monthly.columns = ['year', 'month', 'month_name', 'sales', 'orders']
    df_monthly['year_month'] = df_monthly['year'].astype(str) + '-' + df_monthly['month'].astype(str).str.zfill(2)
    df_monthly = df_monthly.sort_values(['year', 'month']).reset_index(drop=True)
    
    # Statistical Summary
    print("\n STATISTICAL SUMMARY OF MONTHLY SALES")
    print("-" * 80)
    
    print(f"Total Revenue (All Time): R$ {df_monthly['sales'].sum():,.2f}")
    print(f"Number of Months: {len(df_monthly)}")
    print(f"\nMonthly Sales Statistics:")
    print(f"  Mean:   R$ {df_monthly['sales'].mean():,.2f}")
    print(f"  Median: R$ {df_monthly['sales'].median():,.2f}")
    print(f"  Std:    R$ {df_monthly['sales'].std():,.2f}")
    print(f"  Min:    R$ {df_monthly['sales'].min():,.2f}")
    print(f"  Max:    R$ {df_monthly['sales'].max():,.2f}")
    
    # Growth Analysis
    first_month_sales = df_monthly['sales'].iloc[0]
    last_month_sales = df_monthly['sales'].iloc[-1]
    growth_rate = ((last_month_sales - first_month_sales) / first_month_sales * 100)
    
    print("-" * 80)
    print(f"\n GROWTH ANALYSIS")
    print("-" * 80)
    print(f"First Month ({df_monthly['year_month'].iloc[0]}): R$ {first_month_sales:,.2f}")
    print(f"Last Month ({df_monthly['year_month'].iloc[-1]}): R$ {last_month_sales:,.2f}")
    print(f"Overall Growth: {growth_rate:+.2f}%")
    
    # Top Categories
    print("-" * 80)
    print(f"\n TOP 5 PRODUCT CATEGORIES BY REVENUE")
    print("-" * 80)
    top_categories = df_sales.groupby('product_category_name')['total_price'].sum().nlargest(5)
    for i, (category, revenue) in enumerate(top_categories.items(), 1):
        pct = (revenue / df_sales['total_price'].sum() * 100)
        print(f"{i}. {category}: R$ {revenue:,.2f} ({pct:.1f}%)")
    
    # Top States
    print("-" * 80)
    print(f"\n TOP 5 STATES BY REVENUE")
    print("-" * 80)
    top_states = df_sales.groupby('customer_state')['total_price'].sum().nlargest(5)
    for i, (state, revenue) in enumerate(top_states.items(), 1):
        pct = (revenue / df_sales['total_price'].sum() * 100)
        print(f"{i}. {state}: R$ {revenue:,.2f} ({pct:.1f}%)")
    
    # Create visualizations
    create_descriptive_visualizations(df_monthly, df_sales)
    
    return df_monthly

# 4. VISUALIZATION OF DESCRIPTIVE

def create_descriptive_visualizations(df_monthly, df_sales):
  
    fig = plt.figure(figsize=(14, 10))
    
    # 1. Monthly Sales Trend (Main chart)
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(range(len(df_monthly)), df_monthly['sales'], 
             marker='o', linewidth=2, markersize=6, color='steelblue')
    ax1.set_title('Monthly Sales Trend', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Month Index')
    ax1.set_ylabel('Sales (R$)')
    ax1.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(range(len(df_monthly)), df_monthly['sales'], 1)
    p = np.poly1d(z)
    ax1.plot(range(len(df_monthly)), p(range(len(df_monthly))), 
             "r--", linewidth=2, alpha=0.8, label='Trend')
    ax1.legend()
    
    # 2. Sales Distribution
    ax2 = plt.subplot(2, 2, 2)
    ax2.hist(df_monthly['sales'], bins=15, color='coral', edgecolor='black', alpha=0.7)
    ax2.axvline(df_monthly['sales'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: R$ {df_monthly["sales"].mean():,.0f}')
    ax2.axvline(df_monthly['sales'].median(), color='green', linestyle='--', 
                linewidth=2, label=f'Median: R$ {df_monthly["sales"].median():,.0f}')
    ax2.set_title('Monthly Sales Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Sales (R$)')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Top 10 Product Categories
    ax3 = plt.subplot(2, 2, 3)
    top_categories = df_sales.groupby('product_category_name')['total_price'].sum().nlargest(10)
    ax3.barh(range(len(top_categories)), top_categories.values, color='lightgreen')
    ax3.set_yticks(range(len(top_categories)))
    ax3.set_yticklabels(top_categories.index, fontsize=9)
    ax3.set_title('Top 10 Product Categories by Revenue', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Total Revenue (R$)')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # 4. Top 10 States
    ax4 = plt.subplot(2, 2, 4)
    top_states = df_sales.groupby('customer_state')['total_price'].sum().nlargest(10)
    ax4.bar(range(len(top_states)), top_states.values, color='skyblue', edgecolor='black')
    ax4.set_xticks(range(len(top_states)))
    ax4.set_xticklabels(top_states.index, rotation=45)
    ax4.set_title('Top 10 States by Revenue', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Total Revenue (R$)')
    ax4.grid(True, alpha=0.3, axis='y')
    
    
    plt.tight_layout()
    plt.savefig('descriptive_analytics_sales.png', dpi=300, bbox_inches='tight')
    print("\nVisualizations saved: descriptive_analytics_sales.png")
    plt.close()

# 5. PREDICTIVE ANALYTICS 

def prepare_predictive_data(df_monthly):
  
    print("\n" + "*"*80)
    print("PREDICTIVE ANALYTICS - NEXT MONTH SALES FORECAST")
    print("-" * 80)
    
    print("\n features for prediction")
    
    # Create features for time series forecasting
    df_ml = df_monthly.copy()
    
    # Time-based features
    df_ml['month_index'] = range(len(df_ml))  # Sequential month number
    df_ml['month_of_year'] = df_ml['month']   # 1-12
    
    # Lag features (previous months' sales)
    df_ml['sales_lag_1'] = df_ml['sales'].shift(1)  # Last month
    df_ml['sales_lag_2'] = df_ml['sales'].shift(2)  # 2 months ago
    df_ml['sales_lag_3'] = df_ml['sales'].shift(3)  # 3 months ago
    
    # Moving averages
    df_ml['sales_ma_3'] = df_ml['sales'].rolling(window=3, min_periods=1).mean()
    
    # Growth rate
    df_ml['sales_growth'] = df_ml['sales'].pct_change()
    
    # Remove rows with NaN from lag features
    df_ml_clean = df_ml.dropna()
    
    print(f"time series features")
    print(f"Available samples: {len(df_ml_clean)} months")
    
    return df_ml_clean

# 6. TRAIN PREDICTION MODEL

def train_forecast_model(df_ml):
    
    print("\n" + "*"*80)
    print("\nGradient Boosting Model")
    print("-" * 80)
    
    # Define features
    feature_columns = [
        'month_index',      # Time trend
        'month_of_year',    # Seasonality
        'sales_lag_1',      # Last month's sales
        'sales_lag_2',      # 2 months ago
        'sales_lag_3',      # 3 months ago
        'sales_ma_3',       # 3-month moving average
        'sales_growth',     # Growth rate
        'orders'            # Number of orders
    ]
    
    X = df_ml[feature_columns]
    y = df_ml['sales']
    
    # Split data: Use last few months as test (simulate predicting future)
    split_point = len(X) - 3  # Hold out last 3 months for testing
    X_train, X_test = X[:split_point], X[split_point:]
    y_train, y_test = y[:split_point], y[split_point:]
    
    print(f"Training set: {len(X_train)} months")
    print(f"Test set: {len(X_test)} months (most recent)")
    
    # Train model
    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    print("Model training complete")
    
    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Evaluate
    evaluate_model(y_train, y_pred_train, y_test, y_pred_test, model, feature_columns)
    
    # Forecast next month
    forecast_next_month(df_ml, model, feature_columns)
    
    return model, X_test, y_test, y_pred_test, feature_columns

# 7. EVALUTATION PREDICTION MODEL

def evaluate_model(y_train, y_pred_train, y_test, y_pred_test, model, feature_columns):
    print("-" * 80)
    print("\n MODEL PERFORMANCE METRICS")
    print("-" * 80)
    
    # Training metrics
    train_r2 = r2_score(y_train, y_pred_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    
    print("Training Set:")
    print(f"  R² Score: {train_r2:.4f}")
    print(f"  RMSE: R$ {train_rmse:,.2f}")

    
    # Test metrics
    test_r2 = r2_score(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    print(f"\nTest Set (Recent Months):")
    print(f"  R² Score: {test_r2:.4f}")
    print(f"  RMSE: R$ {test_rmse:,.2f}")
   
    
    # Create visualizations
    create_predictive_visualizations(y_test, y_pred_test)

# 8. VISUAALIZATION OF PREDICTION

def create_predictive_visualizations(y_test, y_pred_test):
   
    fig = plt.figure(figsize=(14, 5))
    
    # 1. Actual vs Predicted
    ax1 = plt.subplot(1, 3, 1)
    months = range(len(y_test))
    ax1.plot(months, y_test.values, marker='o', linewidth=2, 
             markersize=8, label='Actual Sales', color='blue')
    ax1.plot(months, y_pred_test, marker='s', linewidth=2, 
             markersize=8, label='Predicted Sales', color='orange')
    ax1.set_title('Actual vs Predicted Sales (Test Set)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Sales (R$)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Prediction Accuracy
    ax2 = plt.subplot(1, 3, 2)
    ax2.scatter(y_test, y_pred_test, s=100, alpha=0.6, color='green')
    ax2.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
             'r--', lw=2, label='Perfect Prediction')
    ax2.set_title('Prediction Accuracy', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Actual Sales (R$)')
    ax2.set_ylabel('Predicted Sales (R$)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('predictive_model_next_month.png', dpi=300, bbox_inches='tight')
    
    plt.close()

# 9. FORECAST OF NEXT MONTH

def forecast_next_month(df_ml, model, feature_columns):
   
    print("\n" + "*"*80)
    print(" FORECASTING NEXT MONTH'S SALES")
    print("-" * 80)
    
    
    # Get last available data
    last_row = df_ml.iloc[-1].copy()
    
    print(f"\nCurrent Month: {last_row['year_month']}")
    print(f"Current Sales: R$ {last_row['sales']:,.2f}")
    print(f"Last 3 months average: R$ {last_row['sales_ma_3']:,.2f}")
    
    # Prepare features for next month
    next_month_features = {
        'month_index': last_row['month_index'] + 1,
        'month_of_year': (last_row['month'] % 12) + 1,
        'sales_lag_1': last_row['sales'],  # Current month becomes lag_1
        'sales_lag_2': last_row['sales_lag_1'],
        'sales_lag_3': last_row['sales_lag_2'],
        'sales_ma_3': last_row['sales_ma_3'],
        'sales_growth': last_row['sales_growth'],
        'orders': last_row['orders']
    }
    
    X_next = pd.DataFrame([next_month_features])[feature_columns]
    
    # Make prediction
    next_month_prediction = model.predict(X_next)[0]
    
    # Calculate confidence interval (based on test set error)
    recent_avg = df_ml['sales'].tail(6).mean()
    recent_std = df_ml['sales'].tail(6).std()
    
    lower_bound = next_month_prediction - (1.96 * recent_std)
    upper_bound = next_month_prediction + (1.96 * recent_std)
    
    print("-" * 80)
    print(f"\n NEXT MONTH SALES FORECAST:")
    print("-" * 80)
    print(f"Predicted Sales: R$ {next_month_prediction:,.2f}")
    print(f"\n95% Confidence Interval:")
    print(f"  Lower Bound: R$ {max(0, lower_bound):,.2f}")
    print(f"  Upper Bound: R$ {upper_bound:,.2f}")
    
    # Compare to recent average
    pct_change = ((next_month_prediction - last_row['sales']) / last_row['sales'] * 100)
    print(f"\nExpected change from current month: {pct_change:+.2f}%")
    
# 10. INSIGHTS GENERATION 

def generate_insights(df_monthly, df_sales):
    
    print("\n" + "*"*80)
    print("BUSINESS INSIGHTS & RECOMMENDATIONS")
    print("-" * 80)
    
    
    insights = []
    
    # 1. Overall sales trend
    total_revenue = df_sales['total_price'].sum()
    months_count = len(df_monthly)
    avg_monthly = df_monthly['sales'].mean()
    insights.append(f"1. Total Revenue: R$ {total_revenue:,.2f} across {months_count} months")
    
    # 2. Top performing category
    top_category = df_sales.groupby('product_category_name')['total_price'].sum().idxmax()
    top_category_sales = df_sales.groupby('product_category_name')['total_price'].sum().max()
    category_pct = (top_category_sales / total_revenue * 100)
    insights.append(f"3. Best Category: '{top_category}' accounts for {category_pct:.1f}% of revenue")
    
    # 3. Geographic concentration
    top_state = df_sales.groupby('customer_state')['total_price'].sum().idxmax()
    top_state_sales = df_sales.groupby('customer_state')['total_price'].sum().max()
    state_pct = (top_state_sales / total_revenue * 100)
    insights.append(f"4. Key Market: State '{top_state}' generates {state_pct:.1f}% of sales")
    
    
    print("\n KEY INSIGHTS:")
    print("-" * 80)

    # Save insights to txt.file
    with open('business_insights.txt', 'w') as f:
        f.write("KEY INSIGHTS\n")
        f.write("-" * 80 + "\n")
        for insight in insights:
            f.write(insight + "\n")
            print(insight)  # print to console as well

    print("saved to: business_insights.txt")
    
# 11. MAIN EXECUTION

def main():
    
    try:
        # Connect to dwh 
        engine = connect_to_warehouse()
        
        # Extract data
        df_sales = extract_sales_data(engine)
        
        # Descriptive Analytics 
        df_monthly = descriptive_analytics(df_sales)
        
        # Predictive Analytics 
        df_ml = prepare_predictive_data(df_monthly)
        model, X_test, y_test, y_pred_test, features= train_forecast_model(df_ml)
        
        # Generate Insights 
        generate_insights(df_monthly, df_sales)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()