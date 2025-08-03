#!/usr/bin/env python3
"""
Simple Top Performers Analysis

A streamlined version focusing on core analysis without visualizations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class SimpleTopPerformersAnalyzer:
    """Simple analyzer for finding top performers."""
    
    def __init__(self, data_path: str):
        self.df = pd.read_csv(data_path)
        self.df.columns = self.df.columns.str.strip()
        print(f"Data loaded: {len(self.df)} records")
        print(f"Columns: {list(self.df.columns)}")
    
    def find_top_by_single_metric(self, metric: str, top_n: int = 10):
        """Find top performers by a single metric."""
        return self.df.nlargest(top_n, metric)
    
    def find_top_by_composite_score(self, metrics: List[str], weights: Optional[List[float]] = None, top_n: int = 10):
        """Find top performers by composite score."""
        if weights is None:
            weights = [1.0 / len(metrics)] * len(metrics)
        
        # Normalize and calculate composite score
        composite_score = pd.Series(0.0, index=self.df.index)
        
        for metric, weight in zip(metrics, weights):
            min_val = self.df[metric].min()
            max_val = self.df[metric].max()
            if max_val != min_val:
                normalized = (self.df[metric] - min_val) / (max_val - min_val)
                composite_score += normalized * weight
        
        result_df = self.df.copy()
        result_df['Composite_Score'] = composite_score
        return result_df.nlargest(top_n, 'Composite_Score')
    
    def find_well_rounded_performers(self, metrics: List[str], percentile: float = 75, top_n: int = 10):
        """Find performers above percentile threshold in all metrics."""
        mask = pd.Series([True] * len(self.df))
        thresholds = {}
        
        for metric in metrics:
            threshold = np.percentile(self.df[metric], percentile)
            thresholds[metric] = threshold
            mask &= (self.df[metric] >= threshold)
        
        filtered_df = self.df[mask]
        print(f"Found {len(filtered_df)} well-rounded performers")
        print(f"Thresholds: {thresholds}")
        
        if len(filtered_df) > 0:
            return filtered_df.head(top_n)
        return filtered_df
    
    def generate_report(self, metrics: List[str], top_n: int = 10):
        """Generate a comprehensive analysis report."""
        print("\n" + "="*60)
        print("TOP PERFORMERS ANALYSIS REPORT")
        print("="*60)
        
        # Dataset overview
        print(f"\nDATASET OVERVIEW:")
        print(f"Total records: {len(self.df)}")
        print(f"Analysis metrics: {metrics}")
        
        # Statistical summary
        print(f"\nSTATISTICAL SUMMARY:")
        for metric in metrics:
            print(f"\n{metric}:")
            print(f"  Mean: {self.df[metric].mean():.3f}")
            print(f"  Std:  {self.df[metric].std():.3f}")
            print(f"  Min:  {self.df[metric].min():.3f}")
            print(f"  Max:  {self.df[metric].max():.3f}")
            print(f"  90th percentile: {np.percentile(self.df[metric], 90):.3f}")
        
        # Top performers by individual metrics
        print(f"\nTOP 5 PERFORMERS BY INDIVIDUAL METRICS:")
        for metric in metrics:
            print(f"\nTop 5 by {metric}:")
            top_single = self.find_top_by_single_metric(metric, 5)
            display_cols = ['Serial No.'] + [metric] + ['Chance of Admit']
            display_cols = [col for col in display_cols if col in top_single.columns]
            print(top_single[display_cols].to_string(index=False))
        
        # Top performers by composite score
        print(f"\nTOP {top_n} PERFORMERS BY COMPOSITE SCORE:")
        weights = [0.25, 0.20, 0.35, 0.20]  # Custom weights
        top_composite = self.find_top_by_composite_score(metrics, weights, top_n)
        display_cols = ['Serial No.'] + metrics + ['Composite_Score']
        display_cols = [col for col in display_cols if col in top_composite.columns]
        print(top_composite[display_cols].round(3).to_string(index=False))
        
        # Well-rounded performers
        print(f"\nWELL-ROUNDED PERFORMERS (75th percentile in all metrics):")
        well_rounded = self.find_well_rounded_performers(metrics, 75, top_n)
        if len(well_rounded) > 0:
            display_cols = ['Serial No.'] + metrics
            display_cols = [col for col in display_cols if col in well_rounded.columns]
            print(well_rounded[display_cols].to_string(index=False))
        else:
            print("No performers found meeting all criteria.")
        
        # Performance categories
        print(f"\nPERFORMANCE CATEGORIES:")
        
        # High achievers (top 10% in admission chance)
        if 'Chance of Admit' in self.df.columns:
            threshold = np.percentile(self.df['Chance of Admit'], 90)
            high_achievers = self.df[self.df['Chance of Admit'] >= threshold]
            print(f"High Achievers (top 10% admission chance): {len(high_achievers)} students")
            print(f"  Average chance of admit: {high_achievers['Chance of Admit'].mean():.3f}")
        
        # Academic stars (top 15% CGPA)
        if 'CGPA' in self.df.columns:
            threshold = np.percentile(self.df['CGPA'], 85)
            academic_stars = self.df[self.df['CGPA'] >= threshold]
            print(f"Academic Stars (top 15% CGPA): {len(academic_stars)} students")
            print(f"  Average CGPA: {academic_stars['CGPA'].mean():.3f}")
        
        # Test champions (top 15% in both GRE and TOEFL)
        if 'GRE Score' in self.df.columns and 'TOEFL Score' in self.df.columns:
            gre_threshold = np.percentile(self.df['GRE Score'], 85)
            toefl_threshold = np.percentile(self.df['TOEFL Score'], 85)
            test_champions = self.df[
                (self.df['GRE Score'] >= gre_threshold) & 
                (self.df['TOEFL Score'] >= toefl_threshold)
            ]
            print(f"Test Champions (top 15% in both GRE & TOEFL): {len(test_champions)} students")
            if len(test_champions) > 0:
                print(f"  Average GRE: {test_champions['GRE Score'].mean():.1f}")
                print(f"  Average TOEFL: {test_champions['TOEFL Score'].mean():.1f}")


def main():
    """Main function to run the analysis."""
    print("Simple Top Performers Analysis")
    print("="*35)
    
    # Analyze admission data
    data_path = "Pandas/Admission_Predict_Ver1.1.csv"
    analyzer = SimpleTopPerformersAnalyzer(data_path)
    
    # Define performance metrics
    metrics = ['GRE Score', 'TOEFL Score', 'CGPA', 'University Rating']
    
    # Generate comprehensive report
    analyzer.generate_report(metrics, top_n=8)
    
    print(f"\n{'='*60}")
    print("CUSTOM ANALYSIS EXAMPLES")
    print("="*60)
    
    # Example 1: Academic-focused ranking (higher weight on CGPA)
    print(f"\nExample 1: Academic-focused ranking (CGPA weighted 50%)")
    academic_weights = [0.20, 0.15, 0.50, 0.15]
    top_academic = analyzer.find_top_by_composite_score(metrics, academic_weights, 5)
    display_cols = ['Serial No.', 'CGPA', 'GRE Score', 'TOEFL Score', 'Composite_Score']
    print(top_academic[display_cols].round(3).to_string(index=False))
    
    # Example 2: Test-focused ranking (higher weight on GRE and TOEFL)
    print(f"\nExample 2: Test-focused ranking (GRE + TOEFL weighted 70%)")
    test_weights = [0.35, 0.35, 0.20, 0.10]
    top_test = analyzer.find_top_by_composite_score(metrics, test_weights, 5)
    display_cols = ['Serial No.', 'GRE Score', 'TOEFL Score', 'CGPA', 'Composite_Score']
    print(top_test[display_cols].round(3).to_string(index=False))
    
    # Example 3: Find students with specific criteria
    print(f"\nExample 3: Students with GRE > 330 AND CGPA > 9.0")
    high_performers = analyzer.df[
        (analyzer.df['GRE Score'] > 330) & 
        (analyzer.df['CGPA'] > 9.0)
    ]
    if len(high_performers) > 0:
        display_cols = ['Serial No.', 'GRE Score', 'CGPA', 'Chance of Admit']
        print(high_performers[display_cols].sort_values('Chance of Admit', ascending=False).to_string(index=False))
        print(f"Found {len(high_performers)} students meeting criteria")
    else:
        print("No students found meeting these strict criteria")


if __name__ == "__main__":
    main()