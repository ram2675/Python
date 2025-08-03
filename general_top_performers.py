#!/usr/bin/env python3
"""
General Top Performers Finder

This script provides a flexible framework to find top performers from any dataset
based on customizable criteria and metrics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Union, Optional
import warnings
warnings.filterwarnings('ignore')

class GeneralTopPerformersFinder:
    """
    A flexible class to find top performers from any dataset.
    """
    
    def __init__(self, data: Union[str, pd.DataFrame]):
        """
        Initialize with data.
        
        Args:
            data: Either a file path (str) or pandas DataFrame
        """
        if isinstance(data, str):
            self.df = pd.read_csv(data)
            print(f"Data loaded from file: {len(self.df)} records")
        elif isinstance(data, pd.DataFrame):
            self.df = data.copy()
            print(f"Data loaded from DataFrame: {len(self.df)} records")
        else:
            raise ValueError("Data must be either a file path or pandas DataFrame")
        
        # Clean column names
        self.df.columns = self.df.columns.str.strip()
        self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        print(f"Available numeric columns: {self.numeric_columns}")
    
    def find_top_performers_single_metric(self, metric: str, top_n: int = 10, 
                                        ascending: bool = False) -> pd.DataFrame:
        """
        Find top performers based on a single metric.
        
        Args:
            metric (str): Column name to rank by
            top_n (int): Number of top performers to return
            ascending (bool): If True, rank in ascending order (lower is better)
            
        Returns:
            pd.DataFrame: Top performers data
        """
        if metric not in self.df.columns:
            raise ValueError(f"Metric '{metric}' not found. Available columns: {list(self.df.columns)}")
        
        if ascending:
            top_performers = self.df.nsmallest(top_n, metric)
        else:
            top_performers = self.df.nlargest(top_n, metric)
        
        return top_performers
    
    def find_top_performers_multiple_metrics(self, metrics: List[str], 
                                           weights: Optional[List[float]] = None,
                                           top_n: int = 10,
                                           higher_is_better: Optional[List[bool]] = None) -> pd.DataFrame:
        """
        Find top performers based on multiple metrics with optional weights.
        
        Args:
            metrics (List[str]): List of column names to consider
            weights (List[float]): Weights for each metric (must sum to 1)
            top_n (int): Number of top performers to return
            higher_is_better (List[bool]): For each metric, True if higher values are better
            
        Returns:
            pd.DataFrame: Top performers with composite scores
        """
        # Validate inputs
        for metric in metrics:
            if metric not in self.df.columns:
                raise ValueError(f"Metric '{metric}' not found in data")
        
        if weights is None:
            weights = [1.0 / len(metrics)] * len(metrics)
        
        if len(weights) != len(metrics):
            raise ValueError("Number of weights must match number of metrics")
        
        if abs(sum(weights) - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1.0")
        
        if higher_is_better is None:
            higher_is_better = [True] * len(metrics)
        
        # Calculate composite score
        composite_scores = pd.Series(0.0, index=self.df.index)
        
        for i, (metric, weight, is_higher_better) in enumerate(zip(metrics, weights, higher_is_better)):
            # Normalize to 0-1 scale
            min_val = self.df[metric].min()
            max_val = self.df[metric].max()
            
            if max_val == min_val:
                normalized = pd.Series(0.5, index=self.df.index)
            else:
                normalized = (self.df[metric] - min_val) / (max_val - min_val)
            
            # Invert if lower is better
            if not is_higher_better:
                normalized = 1 - normalized
            
            composite_scores += normalized * weight
        
        # Add composite score to dataframe
        result_df = self.df.copy()
        result_df['Composite_Score'] = composite_scores
        
        # Get top performers
        top_performers = result_df.nlargest(top_n, 'Composite_Score')
        return top_performers
    
    def find_top_performers_percentile_filter(self, metrics: List[str], 
                                            percentile_threshold: float = 75,
                                            top_n: int = 10,
                                            ranking_metric: Optional[str] = None) -> pd.DataFrame:
        """
        Find performers who score above percentile threshold in ALL specified metrics.
        
        Args:
            metrics (List[str]): Metrics to apply percentile filter on
            percentile_threshold (float): Percentile threshold (0-100)
            top_n (int): Number of top performers to return
            ranking_metric (str): Metric to rank filtered results by
            
        Returns:
            pd.DataFrame: Filtered top performers
        """
        # Calculate thresholds
        thresholds = {}
        for metric in metrics:
            if metric not in self.df.columns:
                raise ValueError(f"Metric '{metric}' not found in data")
            thresholds[metric] = np.percentile(self.df[metric], percentile_threshold)
        
        # Apply filters
        mask = pd.Series([True] * len(self.df))
        for metric, threshold in thresholds.items():
            mask &= (self.df[metric] >= threshold)
        
        filtered_df = self.df[mask]
        
        print(f"Found {len(filtered_df)} performers above {percentile_threshold}th percentile")
        print(f"Thresholds used: {thresholds}")
        
        # Rank filtered results
        if len(filtered_df) == 0:
            return filtered_df
        
        if ranking_metric:
            if ranking_metric not in filtered_df.columns:
                ranking_metric = metrics[0]
        else:
            ranking_metric = metrics[0]
        
        top_performers = filtered_df.nlargest(min(top_n, len(filtered_df)), ranking_metric)
        return top_performers
    
    def analyze_performance_distribution(self, metrics: List[str]) -> Dict:
        """
        Analyze the distribution of performance across specified metrics.
        
        Args:
            metrics (List[str]): Metrics to analyze
            
        Returns:
            dict: Statistical summary of each metric
        """
        analysis = {}
        
        for metric in metrics:
            if metric not in self.df.columns:
                continue
                
            analysis[metric] = {
                'count': len(self.df[metric].dropna()),
                'mean': self.df[metric].mean(),
                'std': self.df[metric].std(),
                'min': self.df[metric].min(),
                'max': self.df[metric].max(),
                'median': self.df[metric].median(),
                'q25': self.df[metric].quantile(0.25),
                'q75': self.df[metric].quantile(0.75),
                'top_10_percent_threshold': np.percentile(self.df[metric].dropna(), 90),
                'top_5_percent_threshold': np.percentile(self.df[metric].dropna(), 95)
            }
        
        return analysis
    
    def create_performance_dashboard(self, metrics: List[str], top_n: int = 15):
        """
        Create a comprehensive performance dashboard.
        
        Args:
            metrics (List[str]): Metrics to include in dashboard
            top_n (int): Number of top performers to highlight
        """
        # Determine number of plots needed
        n_metrics = len(metrics)
        n_rows = (n_metrics + 1) // 2
        
        fig, axes = plt.subplots(n_rows, 2, figsize=(15, 5 * n_rows))
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        fig.suptitle('Performance Analysis Dashboard', fontsize=16, fontweight='bold')
        
        for i, metric in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            # Distribution plot
            self.df[metric].hist(bins=30, alpha=0.7, ax=axes[row, col], edgecolor='black')
            
            # Add mean line
            mean_val = self.df[metric].mean()
            axes[row, col].axvline(mean_val, color='red', linestyle='--', 
                                 label=f'Mean: {mean_val:.2f}')
            
            # Add top 10% threshold
            top_10_threshold = np.percentile(self.df[metric], 90)
            axes[row, col].axvline(top_10_threshold, color='green', linestyle=':', 
                                 label=f'Top 10%: {top_10_threshold:.2f}')
            
            axes[row, col].set_title(f'Distribution of {metric}')
            axes[row, col].set_xlabel(metric)
            axes[row, col].set_ylabel('Frequency')
            axes[row, col].legend()
        
        # Hide empty subplot if odd number of metrics
        if n_metrics % 2 == 1:
            axes[-1, -1].set_visible(False)
        
        plt.tight_layout()
        plt.show()
        
        # Create correlation heatmap if multiple metrics
        if len(metrics) > 1:
            plt.figure(figsize=(10, 8))
            correlation_matrix = self.df[metrics].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, fmt='.3f')
            plt.title('Performance Metrics Correlation Matrix')
            plt.tight_layout()
            plt.show()
    
    def generate_comprehensive_report(self, metrics: List[str], 
                                    weights: Optional[List[float]] = None,
                                    top_n: int = 10):
        """
        Generate a comprehensive performance analysis report.
        
        Args:
            metrics (List[str]): Primary metrics to analyze
            weights (List[float]): Weights for composite scoring
            top_n (int): Number of top performers in each category
        """
        print("=" * 80)
        print("COMPREHENSIVE TOP PERFORMERS ANALYSIS REPORT")
        print("=" * 80)
        
        # 1. Dataset Overview
        print(f"\n1. DATASET OVERVIEW")
        print("-" * 40)
        print(f"Total records: {len(self.df)}")
        print(f"Total columns: {len(self.df.columns)}")
        print(f"Numeric columns: {len(self.numeric_columns)}")
        print(f"Analysis metrics: {metrics}")
        
        # 2. Statistical Summary
        print(f"\n2. STATISTICAL SUMMARY")
        print("-" * 40)
        stats = self.analyze_performance_distribution(metrics)
        for metric, stat_dict in stats.items():
            print(f"\n{metric}:")
            print(f"  Count: {stat_dict['count']}")
            print(f"  Mean:  {stat_dict['mean']:.3f}")
            print(f"  Std:   {stat_dict['std']:.3f}")
            print(f"  Range: {stat_dict['min']:.3f} - {stat_dict['max']:.3f}")
            print(f"  Top 10% threshold: {stat_dict['top_10_percent_threshold']:.3f}")
        
        # 3. Top performers by individual metrics
        print(f"\n3. TOP {top_n} PERFORMERS BY INDIVIDUAL METRICS")
        print("-" * 60)
        for metric in metrics:
            print(f"\nTop {min(5, top_n)} by {metric}:")
            top_single = self.find_top_performers_single_metric(metric, min(5, top_n))
            if len(top_single) > 0:
                display_cols = [col for col in [metric] + metrics if col in top_single.columns]
                print(top_single[display_cols].round(3).to_string())
        
        # 4. Top performers by composite score
        print(f"\n4. TOP {top_n} PERFORMERS BY COMPOSITE SCORE")
        print("-" * 60)
        try:
            top_composite = self.find_top_performers_multiple_metrics(metrics, weights, top_n)
            if len(top_composite) > 0:
                display_cols = metrics + ['Composite_Score']
                display_cols = [col for col in display_cols if col in top_composite.columns]
                print(top_composite[display_cols].round(3).to_string())
        except Exception as e:
            print(f"Error calculating composite scores: {e}")
        
        # 5. High performers (75th percentile filter)
        print(f"\n5. WELL-ROUNDED PERFORMERS (75th percentile in all metrics)")
        print("-" * 60)
        try:
            well_rounded = self.find_top_performers_percentile_filter(metrics, 75, top_n)
            if len(well_rounded) > 0:
                display_cols = [col for col in metrics if col in well_rounded.columns]
                print(well_rounded[display_cols].round(3).to_string())
            else:
                print("No performers found meeting all criteria.")
        except Exception as e:
            print(f"Error finding well-rounded performers: {e}")


def demo_with_sample_data():
    """
    Demonstrate the functionality with sample employee performance data.
    """
    # Create sample employee performance data
    np.random.seed(42)
    n_employees = 100
    
    sample_data = pd.DataFrame({
        'Employee_ID': range(1, n_employees + 1),
        'Sales_Performance': np.random.normal(75, 15, n_employees),
        'Customer_Satisfaction': np.random.normal(4.2, 0.8, n_employees),
        'Team_Collaboration': np.random.normal(3.8, 0.6, n_employees),
        'Innovation_Score': np.random.normal(70, 20, n_employees),
        'Attendance_Rate': np.random.normal(95, 5, n_employees),
        'Years_Experience': np.random.randint(1, 20, n_employees)
    })
    
    # Ensure realistic ranges
    sample_data['Customer_Satisfaction'] = sample_data['Customer_Satisfaction'].clip(1, 5)
    sample_data['Team_Collaboration'] = sample_data['Team_Collaboration'].clip(1, 5)
    sample_data['Sales_Performance'] = sample_data['Sales_Performance'].clip(0, 100)
    sample_data['Innovation_Score'] = sample_data['Innovation_Score'].clip(0, 100)
    sample_data['Attendance_Rate'] = sample_data['Attendance_Rate'].clip(80, 100)
    
    print("Generated sample employee performance data:")
    print(sample_data.head())
    
    # Initialize analyzer
    analyzer = GeneralTopPerformersFinder(sample_data)
    
    # Define performance metrics
    performance_metrics = ['Sales_Performance', 'Customer_Satisfaction', 
                          'Team_Collaboration', 'Innovation_Score', 'Attendance_Rate']
    
    # Generate comprehensive report
    analyzer.generate_comprehensive_report(performance_metrics, top_n=10)
    
    # Create dashboard
    print("\nGenerating performance dashboard...")
    analyzer.create_performance_dashboard(performance_metrics)
    
    return analyzer


def main():
    """Main function demonstrating the top performers analysis."""
    
    print("Top Performers Analysis Tool")
    print("="*40)
    
    # First try with the admission data if it exists
    try:
        print("\nAnalyzing admission prediction data...")
        admission_analyzer = GeneralTopPerformersFinder("Pandas/Admission_Predict_Ver1.1.csv")
        
        # Define metrics for admission data
        admission_metrics = ['GRE Score', 'TOEFL Score', 'CGPA', 'University Rating']
        
        # Custom weights emphasizing academic performance
        weights = [0.25, 0.20, 0.40, 0.15]  # Higher weight on CGPA
        
        admission_analyzer.generate_comprehensive_report(
            admission_metrics, weights=weights, top_n=8
        )
        
        print("\nGenerating admission data dashboard...")
        admission_analyzer.create_performance_dashboard(admission_metrics)
        
    except FileNotFoundError:
        print("Admission data not found, proceeding with sample data...")
    
    # Demonstrate with sample data
    print("\n" + "="*60)
    print("DEMONSTRATION WITH SAMPLE EMPLOYEE DATA")
    print("="*60)
    demo_analyzer = demo_with_sample_data()


if __name__ == "__main__":
    main()