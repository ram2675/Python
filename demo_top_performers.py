#!/usr/bin/env python3
"""
Demo: Finding Top Performers from Sample Data

This script demonstrates how to find top performers from any dataset
using sample employee performance data.
"""

import pandas as pd
import numpy as np
from typing import List, Optional

def generate_sample_employee_data(n_employees: int = 100) -> pd.DataFrame:
    """Generate sample employee performance data."""
    np.random.seed(42)  # For reproducible results
    
    data = {
        'Employee_ID': [f"EMP_{i:03d}" for i in range(1, n_employees + 1)],
        'Name': [f"Employee_{i}" for i in range(1, n_employees + 1)],
        'Sales_Performance': np.random.normal(75, 15, n_employees).clip(0, 100),
        'Customer_Satisfaction': np.random.normal(4.2, 0.8, n_employees).clip(1, 5),
        'Team_Collaboration': np.random.normal(3.8, 0.6, n_employees).clip(1, 5),
        'Innovation_Score': np.random.normal(70, 20, n_employees).clip(0, 100),
        'Attendance_Rate': np.random.normal(95, 5, n_employees).clip(80, 100),
        'Years_Experience': np.random.randint(1, 20, n_employees),
        'Department': np.random.choice(['Sales', 'Marketing', 'Engineering', 'Support'], n_employees)
    }
    
    return pd.DataFrame(data).round(2)

def find_top_performers_simple(df: pd.DataFrame, metrics: List[str], 
                              weights: Optional[List[float]] = None, 
                              top_n: int = 10) -> pd.DataFrame:
    """
    Simple function to find top performers based on multiple metrics.
    
    Args:
        df: DataFrame with performance data
        metrics: List of column names to use for ranking
        weights: Optional weights for each metric (must sum to 1)
        top_n: Number of top performers to return
    
    Returns:
        DataFrame with top performers and their composite scores
    """
    
    if weights is None:
        weights = [1.0 / len(metrics)] * len(metrics)
    
    if len(weights) != len(metrics):
        raise ValueError("Number of weights must match number of metrics")
    
    if abs(sum(weights) - 1.0) > 1e-6:
        raise ValueError("Weights must sum to 1.0")
    
    # Calculate composite score
    composite_score = pd.Series(0.0, index=df.index)
    
    print(f"Calculating composite scores using metrics: {metrics}")
    print(f"Weights: {dict(zip(metrics, weights))}")
    
    for metric, weight in zip(metrics, weights):
        # Normalize to 0-1 scale
        min_val = df[metric].min()
        max_val = df[metric].max()
        
        if max_val != min_val:
            normalized = (df[metric] - min_val) / (max_val - min_val)
            composite_score += normalized * weight
    
    # Add composite score and return top performers
    result_df = df.copy()
    result_df['Composite_Score'] = composite_score
    
    return result_df.nlargest(top_n, 'Composite_Score')

def analyze_performance_by_department(df: pd.DataFrame, metrics: List[str]) -> None:
    """Analyze performance by department."""
    print("\nPERFORMANCE BY DEPARTMENT:")
    print("-" * 40)
    
    for dept in df['Department'].unique():
        dept_data = df[df['Department'] == dept]
        print(f"\n{dept} Department ({len(dept_data)} employees):")
        
        for metric in metrics:
            avg_score = dept_data[metric].mean()
            print(f"  Average {metric}: {avg_score:.2f}")

def main():
    """Main demonstration function."""
    print("="*60)
    print("TOP PERFORMERS ANALYSIS DEMONSTRATION")
    print("="*60)
    
    # Generate sample data
    print("\n1. GENERATING SAMPLE EMPLOYEE DATA")
    print("-" * 40)
    df = generate_sample_employee_data(100)
    print(f"Generated data for {len(df)} employees")
    print(f"Departments: {list(df['Department'].unique())}")
    print("\nSample data:")
    print(df.head())
    
    # Define performance metrics
    metrics = ['Sales_Performance', 'Customer_Satisfaction', 'Team_Collaboration', 
               'Innovation_Score', 'Attendance_Rate']
    
    print(f"\n2. STATISTICAL OVERVIEW")
    print("-" * 40)
    for metric in metrics:
        print(f"{metric}:")
        print(f"  Mean: {df[metric].mean():.2f}")
        print(f"  Std:  {df[metric].std():.2f}")
        print(f"  Range: {df[metric].min():.2f} - {df[metric].max():.2f}")
    
    # Example 1: Equal weights
    print(f"\n3. TOP 10 PERFORMERS (Equal Weights)")
    print("-" * 40)
    equal_weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    top_performers_equal = find_top_performers_simple(df, metrics, equal_weights, 10)
    
    display_cols = ['Employee_ID', 'Name', 'Department'] + metrics + ['Composite_Score']
    print(top_performers_equal[display_cols].to_string(index=False))
    
    # Example 2: Sales-focused weights
    print(f"\n4. TOP 10 PERFORMERS (Sales-Focused)")
    print("-" * 40)
    sales_weights = [0.4, 0.2, 0.15, 0.15, 0.1]  # Heavy weight on sales
    top_performers_sales = find_top_performers_simple(df, metrics, sales_weights, 10)
    print(top_performers_sales[display_cols].to_string(index=False))
    
    # Example 3: Team-focused weights
    print(f"\n5. TOP 10 PERFORMERS (Team-Focused)")
    print("-" * 40)
    team_weights = [0.15, 0.25, 0.4, 0.15, 0.05]  # Heavy weight on collaboration
    top_performers_team = find_top_performers_simple(df, metrics, team_weights, 10)
    print(top_performers_team[display_cols].to_string(index=False))
    
    # Single metric examples
    print(f"\n6. TOP 5 BY INDIVIDUAL METRICS")
    print("-" * 40)
    
    for metric in ['Sales_Performance', 'Customer_Satisfaction', 'Innovation_Score']:
        top_single = df.nlargest(5, metric)
        print(f"\nTop 5 by {metric}:")
        cols = ['Employee_ID', 'Name', 'Department', metric]
        print(top_single[cols].to_string(index=False))
    
    # Department analysis
    analyze_performance_by_department(df, metrics)
    
    # High performers with specific criteria
    print(f"\n7. HIGH PERFORMERS WITH SPECIFIC CRITERIA")
    print("-" * 40)
    
    # Example: Sales > 85 AND Customer Satisfaction > 4.5
    high_performers = df[
        (df['Sales_Performance'] > 85) & 
        (df['Customer_Satisfaction'] > 4.5)
    ]
    
    print(f"Employees with Sales > 85 AND Customer Satisfaction > 4.5:")
    if len(high_performers) > 0:
        cols = ['Employee_ID', 'Name', 'Department', 'Sales_Performance', 'Customer_Satisfaction']
        print(high_performers[cols].sort_values('Sales_Performance', ascending=False).to_string(index=False))
        print(f"\nFound {len(high_performers)} employees meeting criteria")
    else:
        print("No employees found meeting these criteria")
    
    # Well-rounded performers (above 75th percentile in multiple areas)
    print(f"\n8. WELL-ROUNDED PERFORMERS")
    print("-" * 40)
    
    key_metrics = ['Sales_Performance', 'Customer_Satisfaction', 'Team_Collaboration']
    
    # Calculate 75th percentile thresholds
    thresholds = {}
    for metric in key_metrics:
        thresholds[metric] = np.percentile(df[metric], 75)
    
    print(f"75th percentile thresholds: {thresholds}")
    
    # Find well-rounded performers
    mask = pd.Series([True] * len(df))
    for metric, threshold in thresholds.items():
        mask &= (df[metric] >= threshold)
    
    well_rounded = df[mask]
    print(f"\nWell-rounded performers ({len(well_rounded)} found):")
    
    if len(well_rounded) > 0:
        cols = ['Employee_ID', 'Name', 'Department'] + key_metrics
        print(well_rounded[cols].head(10).to_string(index=False))
    
    # Summary insights
    print(f"\n9. KEY INSIGHTS")
    print("-" * 40)
    print(f"• Total employees analyzed: {len(df)}")
    print(f"• Departments represented: {len(df['Department'].unique())}")
    print(f"• Average sales performance: {df['Sales_Performance'].mean():.1f}")
    print(f"• Highest customer satisfaction: {df['Customer_Satisfaction'].max():.2f}")
    print(f"• Most innovative employee: {df.loc[df['Innovation_Score'].idxmax(), 'Name']}")
    print(f"• Best team collaborator: {df.loc[df['Team_Collaboration'].idxmax(), 'Name']}")
    
    # Department with highest average performance
    dept_avg = df.groupby('Department')[metrics].mean()
    dept_avg['Overall_Avg'] = dept_avg.mean(axis=1)
    best_dept = dept_avg['Overall_Avg'].idxmax()
    print(f"• Department with highest average performance: {best_dept}")
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print("\nThis demonstration shows how to:")
    print("• Load and analyze performance data")
    print("• Find top performers using different weighting schemes")
    print("• Identify specialists vs well-rounded performers")
    print("• Apply custom criteria and filters")
    print("• Generate actionable insights from the data")

if __name__ == "__main__":
    main()