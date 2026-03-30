# Olist E-commerce Analytics
## BID3000 - Group AABLM

### Project Overview
This project analyzes Olist e-commerce data using SQL and Python to provide business insights and sales forecasting.

### Components
- **Python Analytics**: Descriptive statistics and predictive modeling for sales forecasting

### Python Dependencies

#### Required Libraries and Python version
```bash
python==3.10.19
pandas==2.3.3
numpy==2.2.5
matplotlib==3.10.6
seaborn==0.13.2 # Only for gridlines, not necessary,comment out '#'sns.style and import
scikit-learn==1.7.2
sqlalchemy==2.0.43
psycopg2-binary==2.9.11
```

#### Installation
```bash
pip install -r requirements.txt
```
or 

- Create Anaconda enviroment with the needed dependencies (ctrl+shift+p = change interpeter vscode)

### Database Configuration
- **Database**: PostgreSQL
- **Port**: 5432(common)or 5433
- **Database Name**: Bid3000
- **Schema**: dwh (data warehouse)

### Running the Analysis

1. Ensure PostgreSQL database is running
2. Update database credentials in the script if needed
3. Run the Python script:
   ```bash
   python python_analytic_integration.py
   ```

### Output Files
- `descriptive_analytics_sales.png` - Sales trend visualizations
- `predictive_model_next_month.png` - Model performance charts
- `analytics_report.txt` - Key business insights

### Key Features
- Automated data warehouse connection
- Monthly sales trend analysis
- Top performing categories and states analysis
- Gradient Boosting regression for sales forecasting
- Next month sales prediction with confidence intervals
- Automated insight generation and reporting

### Model Performance
- Uses Gradient Boosting Regressor
- Features: Time-based, lag features, moving averages
- Evaluation metrics: R² Score, RMSE
- Provides 95% confidence interval for predictions

### Authors
Group AABLM - BID3000
November 2025