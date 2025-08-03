#!/usr/bin/env python3
"""
Top Performers Analysis Script

This script analyzes student admission data to identify top performers
based on various criteria and metrics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TopPerformersAnalyzer:
    """
    A class to analyze and identify top performers from student admission data.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the analyzer with data.
        
        Args:
            data_path (str): Path to the CSV file containing student data
        """
        self.data_path = data_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and prepare the data for analysis."""
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"Data loaded successfully: {len(self.df)} records")
            print(f"Columns: {list(self.df.columns)}")
            
            # Clean column names (remove extra spaces)
            self.df.columns = self.df.columns.str.strip()
            
            # Display basic info about the dataset
            print("\nDataset Info:")
            print(self.df.info())
            print("\nFirst few rows:")
            print(self.df.head())
            
        except FileNotFoundError:
            print(f"Error: File {self.data_path} not found.")
            return
        except Exception as e:
            print(f"Error loading data: {e}")
            return
    
    def calculate_composite_score(self, weights: Optional[Dict[str, float]] = None) -> pd.Series:
        """
        Calculate a composite performance score based on multiple metrics.
        
        Args:
            weights (dict): Dictionary of column names and their weights
            
        Returns:
            pd.Series: Composite scores for each student
        """
        if weights is None:
            # Default weights - adjust based on importance
            weights = {
                'GRE Score': 0.25,
                'TOEFL Score': 0.20,
                'CGPA': 0.30,
                'University Rating': 0.15,
                'Chance of Admit': 0.10
            }
        
        # Normalize scores to 0-1 scale
        normalized_scores = pd.DataFrame()
        
        for column, weight in weights.items():
            if column in self.df.columns:
                # Normalize each metric to 0-1 scale
                min_val = self.df[column].min()
                max_val = self.df[column].max()
                normalized_scores[column] = (self.df[column] - min_val) / (max_val - min_val)
        
        # Calculate weighted composite score
        composite_score = sum(normalized_scores[col] * weight 
                            for col, weight in weights.items() 
                            if col in normalized_scores.columns)
        
        return composite_score
    
    def find_top_performers_by_metric(self, metric: str, top_n: int = 10) -> pd.DataFrame:
        """
        Find top performers based on a single metric.
        
        Args:
            metric (str): Column name to rank by
            top_n (int): Number of top performers to return
            
        Returns:
            pd.DataFrame: Top performers data
        """
        if metric not in self.df.columns:
            print(f"Error: Metric '{metric}' not found in data")
            return pd.DataFrame()
        
        top_performers = self.df.nlargest(top_n, metric)
        return top_performers
    
    def find_top_performers_composite(self, top_n: int = 10, 
                                    weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Find top performers based on composite score.
        
        Args:
            top_n (int): Number of top performers to return
            weights (dict): Custom weights for different metrics
            
        Returns:
            pd.DataFrame: Top performers with composite scores
        """
        composite_scores = self.calculate_composite_score(weights)
        
        # Add composite score to dataframe
        result_df = self.df.copy()
        result_df['Composite_Score'] = composite_scores
        
        # Get top performers
        top_performers = result_df.nlargest(top_n, 'Composite_Score')
        return top_performers
    
    def find_well_rounded_performers(self, top_n: int = 10, 
                                   threshold_percentile: float = 75) -> pd.DataFrame:
        """
        Find well-rounded performers who score above threshold in multiple areas.
        
        Args:
            top_n (int): Number of performers to return
            threshold_percentile (float): Percentile threshold for each metric
            
        Returns:
            pd.DataFrame: Well-rounded performers
        """
        metrics = ['GRE Score', 'TOEFL Score', 'CGPA', 'University Rating']
        
        # Calculate thresholds for each metric
        thresholds = {}
        for metric in metrics:
            if metric in self.df.columns:
                thresholds[metric] = np.percentile(self.df[metric], threshold_percentile)
        
        # Find students who meet all thresholds
        mask = pd.Series([True] * len(self.df))
        for metric, threshold in thresholds.items():
            mask &= (self.df[metric] >= threshold)
        
        well_rounded = self.df[mask]
        
        # Sort by chance of admit and return top N
        if len(well_rounded) > 0:
            well_rounded = well_rounded.nlargest(top_n, 'Chance of Admit')
        
        print(f"Found {len(well_rounded)} well-rounded performers")
        print(f"Thresholds used: {thresholds}")
        
        return well_rounded
    
    def analyze_performance_categories(self) -> Dict[str, pd.DataFrame]:
        """
        Categorize students into performance groups and analyze each.
        
        Returns:
            dict: Dictionary with different performance categories
        """
        categories = {}
        
        # High achievers (top 10% in chance of admit)
        admit_threshold = np.percentile(self.df['Chance of Admit'], 90)
        categories['High_Achievers'] = self.df[self.df['Chance of Admit'] >= admit_threshold]
        
        # Academic stars (top 15% in CGPA)
        cgpa_threshold = np.percentile(self.df['CGPA'], 85)
        categories['Academic_Stars'] = self.df[self.df['CGPA'] >= cgpa_threshold]
        
        # Test champions (top 15% in both GRE and TOEFL)
        gre_threshold = np.percentile(self.df['GRE Score'], 85)
        toefl_threshold = np.percentile(self.df['TOEFL Score'], 85)
        categories['Test_Champions'] = self.df[
            (self.df['GRE Score'] >= gre_threshold) & 
            (self.df['TOEFL Score'] >= toefl_threshold)
        ]
        
        # Research oriented (have research experience)
        if 'Research' in self.df.columns:
            categories['Research_Oriented'] = self.df[self.df['Research'] == 1]
        
        return categories
    
    def generate_performance_report(self, top_n: int = 10):
        """
        Generate a comprehensive performance report.
        
        Args:
            top_n (int): Number of top performers to include in each category
        """
        print("=" * 60)
        print("TOP PERFORMERS ANALYSIS REPORT")
        print("=" * 60)
        
        # 1. Top performers by composite score
        print(f"\n1. TOP {top_n} PERFORMERS BY COMPOSITE SCORE")
        print("-" * 50)
        top_composite = self.find_top_performers_composite(top_n)
        print(top_composite[['Serial No.', 'GRE Score', 'TOEFL Score', 'CGPA', 
                           'Chance of Admit', 'Composite_Score']].round(3))
        
        # 2. Top performers by individual metrics
        metrics = ['GRE Score', 'TOEFL Score', 'CGPA', 'Chance of Admit']
        for metric in metrics:
            print(f"\n2. TOP 5 PERFORMERS BY {metric.upper()}")
            print("-" * 50)
            top_metric = self.find_top_performers_by_metric(metric, 5)
            print(top_metric[['Serial No.', metric, 'Chance of Admit']].round(3))
        
        # 3. Well-rounded performers
        print(f"\n3. WELL-ROUNDED PERFORMERS (75th percentile in all areas)")
        print("-" * 50)
        well_rounded = self.find_well_rounded_performers(top_n)
        if len(well_rounded) > 0:
            print(well_rounded[['Serial No.', 'GRE Score', 'TOEFL Score', 'CGPA', 
                              'University Rating', 'Chance of Admit']].round(3))
        else:
            print("No students found meeting all criteria.")
        
        # 4. Performance categories analysis
        print(f"\n4. PERFORMANCE CATEGORIES ANALYSIS")
        print("-" * 50)
        categories = self.analyze_performance_categories()
        for category, data in categories.items():
            print(f"{category}: {len(data)} students")
            if len(data) > 0:
                print(f"  Average Chance of Admit: {data['Chance of Admit'].mean():.3f}")
                print(f"  Average CGPA: {data['CGPA'].mean():.3f}")
        
        # 5. Statistical summary
        print(f"\n5. STATISTICAL SUMMARY")
        print("-" * 50)
        print("Key Performance Metrics:")
        for metric in ['GRE Score', 'TOEFL Score', 'CGPA', 'Chance of Admit']:
            print(f"{metric}:")
            print(f"  Mean: {self.df[metric].mean():.3f}")
            print(f"  Std:  {self.df[metric].std():.3f}")
            print(f"  Max:  {self.df[metric].max():.3f}")
            print(f"  Min:  {self.df[metric].min():.3f}")
            print()
    
    def visualize_top_performers(self, top_n: int = 20):
        """
        Create visualizations for top performers analysis.
        
        Args:
            top_n (int): Number of top performers to visualize
        """
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Top Performers Analysis', fontsize=16, fontweight='bold')
        
        # 1. Top performers by composite score
        top_composite = self.find_top_performers_composite(top_n)
        axes[0, 0].bar(range(len(top_composite)), top_composite['Composite_Score'])
        axes[0, 0].set_title(f'Top {top_n} Performers - Composite Score')
        axes[0, 0].set_xlabel('Student Rank')
        axes[0, 0].set_ylabel('Composite Score')
        
        # 2. Correlation heatmap
        numeric_cols = ['GRE Score', 'TOEFL Score', 'CGPA', 'University Rating', 'Chance of Admit']
        correlation_matrix = self.df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[0, 1])
        axes[0, 1].set_title('Performance Metrics Correlation')
        
        # 3. Distribution of chance of admit
        axes[1, 0].hist(self.df['Chance of Admit'], bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].axvline(self.df['Chance of Admit'].mean(), color='red', 
                          linestyle='--', label=f'Mean: {self.df["Chance of Admit"].mean():.3f}')
        axes[1, 0].set_title('Distribution of Admission Chances')
        axes[1, 0].set_xlabel('Chance of Admit')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        
        # 4. CGPA vs GRE Score scatter plot
        scatter = axes[1, 1].scatter(self.df['CGPA'], self.df['GRE Score'], 
                                   c=self.df['Chance of Admit'], cmap='viridis', alpha=0.6)
        axes[1, 1].set_title('CGPA vs GRE Score (colored by Admission Chance)')
        axes[1, 1].set_xlabel('CGPA')
        axes[1, 1].set_ylabel('GRE Score')
        plt.colorbar(scatter, ax=axes[1, 1], label='Chance of Admit')
        
        plt.tight_layout()
        plt.show()
        
        # Save the plot
        plt.savefig('top_performers_analysis.png', dpi=300, bbox_inches='tight')
        print("Visualization saved as 'top_performers_analysis.png'")


def main():
    """Main function to run the top performers analysis."""
    
    # Initialize the analyzer
    data_path = "Pandas/Admission_Predict_Ver1.1.csv"
    analyzer = TopPerformersAnalyzer(data_path)
    
    if analyzer.df is None:
        print("Failed to load data. Exiting.")
        return
    
    try:
        # Generate comprehensive report
        analyzer.generate_performance_report(top_n=10)
        
        # Create visualizations
        print("\nGenerating visualizations...")
        analyzer.visualize_top_performers(top_n=15)
        
        # Example of finding top performers with custom weights
        print("\n" + "="*60)
        print("CUSTOM ANALYSIS: Academic-focused ranking")
        print("="*60)
        
        custom_weights = {
            'GRE Score': 0.15,
            'TOEFL Score': 0.15,
            'CGPA': 0.50,  # Higher weight on academic performance
            'University Rating': 0.15,
            'Chance of Admit': 0.05
        }
        
        top_academic = analyzer.find_top_performers_composite(10, custom_weights)
        print("Top 10 Academic Performers (CGPA-weighted):")
        print(top_academic[['Serial No.', 'GRE Score', 'TOEFL Score', 'CGPA', 
                          'Chance of Admit', 'Composite_Score']].round(3))
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()