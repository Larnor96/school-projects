# BID3000 - Olist E-commerce Analytics

Business Intelligence project built around the Olist e-commerce dataset. The project combines data warehouse design, ETL, SQL analysis, Python-based analytics, and Power BI dashboards to produce decision-support insights.

## What the project includes
- PostgreSQL data warehouse schema and SQL queries
- Pentaho ETL flows for dimensions, facts, and data cleaning
- Python analysis for descriptive analytics and sales forecasting
- Power BI dashboard material and screenshots
- Final report and ERD documentation

## Tech stack
- PostgreSQL
- SQL
- Pentaho Data Integration
- Python
- Power BI

## Repository structure
- `Database/` schema creation and query files
- `ETL/` Pentaho transformations and ETL-related assets
- `Analytics/python_analytic_integration/` Python analysis, requirements, plots, and generated insights
- `Dashboard/` Power BI file and dashboard documentation
- `Documentation/` ERD and supporting documentation
- `Report/` final project report

## Dataset note
The original CSV datasets are not tracked in this repository to keep the project lightweight and GitHub-friendly. If needed, place the Olist CSV files in `ETL/Dataset/` before running the full ETL pipeline locally.

## Interview talking points
- How the warehouse schema supports analysis and reporting
- ETL design choices, data cleaning, and rejected records
- Forecasting approach in Python and how the output was interpreted
- How technical work was translated into dashboard-driven business insight
