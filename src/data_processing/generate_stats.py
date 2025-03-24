#!/usr/bin/env python3

"""
Generate statistics and visualizations from the cleaned pharma news data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import numpy as np
from collections import Counter
import json

# Set style for better-looking plots
plt.style.use('ggplot')
sns.set(style="whitegrid")

# Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
CLEAN_DIR = os.path.join(DATA_DIR, 'clean')
STATS_DIR = os.path.join(DATA_DIR, 'stats')
PLOTS_DIR = os.path.join(STATS_DIR, 'plots')

# Ensure directories exist
os.makedirs(STATS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

def load_data():
    """Load all cleaned data files and return a combined dataframe."""
    companies = {
        'pfizer': os.path.join(CLEAN_DIR, 'pfizer_news_cleaned.csv'),
        'merck': os.path.join(CLEAN_DIR, 'merck_news_cleaned.csv'),
        'lilly': os.path.join(CLEAN_DIR, 'lilly_news_cleaned.csv')
    }
    
    dfs = {}
    for company, file_path in companies.items():
        df = pd.read_csv(file_path)
        df['company'] = company
        df['date'] = pd.to_datetime(df['date'])
        dfs[company] = df
    
    # Combined dataframe with all companies
    combined_df = pd.concat(dfs.values(), ignore_index=True)
    return dfs, combined_df

def calculate_statistics(dfs, combined_df):
    """Calculate statistics from the data and return as a dictionary."""
    stats = {}
    
    # Overall statistics
    stats['total_articles'] = len(combined_df)
    stats['date_range'] = {
        'start': combined_df['date'].min().strftime('%Y-%m-%d'),
        'end': combined_df['date'].max().strftime('%Y-%m-%d')
    }
    
    # Company-specific statistics
    stats['company_counts'] = {company: len(df) for company, df in dfs.items()}
    
    # Category distribution
    category_counts = combined_df['category'].value_counts().to_dict()
    stats['category_counts'] = category_counts
    
    # Category distribution by company
    company_categories = {}
    for company, df in dfs.items():
        company_categories[company] = df['category'].value_counts().to_dict()
    stats['company_categories'] = company_categories
    
    # Monthly distribution
    combined_df['month'] = combined_df['date'].dt.to_period('M')
    monthly_counts = combined_df.groupby(['company', 'month']).size()
    monthly_series = {}
    for company in dfs.keys():
        if company in monthly_counts:
            company_monthly = monthly_counts[company].reset_index()
            company_monthly['month'] = company_monthly['month'].astype(str)
            monthly_series[company] = company_monthly.set_index('month')[0].to_dict()
    stats['monthly_counts'] = monthly_series
    
    return stats

def generate_plots(dfs, combined_df, stats):
    """Generate visualization plots and save them."""
    plots_info = []
    
    # 1. Category Distribution Pie Chart
    plt.figure(figsize=(12, 8))
    categories = list(stats['category_counts'].keys())
    values = list(stats['category_counts'].values())
    
    # Sort by frequency for better visualization
    sorted_idx = np.argsort(values)[::-1]
    categories = [categories[i] for i in sorted_idx]
    values = [values[i] for i in sorted_idx]
    
    # Take top 10 categories for cleaner visualization
    if len(categories) > 10:
        other_count = sum(values[10:])
        categories = categories[:10] + ['Other']
        values = values[:10] + [other_count]
    
    plt.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Distribution of News Categories Across All Companies', fontsize=16)
    pie_chart_path = os.path.join(PLOTS_DIR, 'category_distribution_pie.png')
    plt.tight_layout()
    plt.savefig(pie_chart_path)
    plots_info.append({
        'title': 'News Categories Distribution',
        'description': 'Pie chart showing the distribution of different news categories across all companies',
        'path': 'data/stats/plots/category_distribution_pie.png'
    })
    plt.close()
    
    # 2. Company Comparison Bar Chart
    plt.figure(figsize=(10, 6))
    companies = list(stats['company_counts'].keys())
    article_counts = list(stats['company_counts'].values())
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    plt.bar(companies, article_counts, color=colors)
    plt.title('Number of News Articles by Company', fontsize=16)
    plt.ylabel('Number of Articles')
    plt.ylim(0, max(article_counts) * 1.1)
    
    # Add count labels on top of each bar
    for i, count in enumerate(article_counts):
        plt.text(i, count + 5, str(count), ha='center', fontweight='bold')
    
    bar_chart_path = os.path.join(PLOTS_DIR, 'company_article_counts.png')
    plt.tight_layout()
    plt.savefig(bar_chart_path)
    plots_info.append({
        'title': 'Articles by Company',
        'description': 'Bar chart comparing the number of news articles published by each pharmaceutical company',
        'path': 'data/stats/plots/company_article_counts.png'
    })
    plt.close()
    
    # 3. Top Categories by Company Horizontal Bar Chart
    plt.figure(figsize=(14, 10))
    
    # Get top 5 categories for each company
    top_categories = {}
    for company, categories in stats['company_categories'].items():
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_categories[company] = dict(sorted_categories[:5])
    
    # Create subplots for each company
    fig, axes = plt.subplots(len(dfs), 1, figsize=(12, 5*len(dfs)))
    
    for i, (company, categories) in enumerate(top_categories.items()):
        ax = axes[i] if len(dfs) > 1 else axes
        cat_names = list(categories.keys())
        cat_counts = list(categories.values())
        
        # Sort for better visualization
        sorted_idx = np.argsort(cat_counts)
        cat_names = [cat_names[j] for j in sorted_idx]
        cat_counts = [cat_counts[j] for j in sorted_idx]
        
        ax.barh(cat_names, cat_counts, color=colors[i % len(colors)])
        ax.set_title(f'Top Categories for {company.capitalize()}', fontsize=14)
        ax.set_xlabel('Count')
        
        # Add count labels
        for j, count in enumerate(cat_counts):
            ax.text(count + 0.5, j, str(count), va='center')
    
    plt.tight_layout()
    categories_chart_path = os.path.join(PLOTS_DIR, 'top_categories_by_company.png')
    plt.savefig(categories_chart_path)
    plots_info.append({
        'title': 'Top Categories by Company',
        'description': 'Horizontal bar charts showing the most common news categories for each company',
        'path': 'data/stats/plots/top_categories_by_company.png'
    })
    plt.close()
    
    # 4. Timeline of News Articles
    plt.figure(figsize=(15, 8))
    
    # Create monthly time series
    for i, (company, df) in enumerate(dfs.items()):
        # Group by month and count
        monthly = df.groupby(df['date'].dt.to_period('M')).size()
        # Convert period index to datetime for plotting
        monthly.index = monthly.index.to_timestamp()
        plt.plot(monthly.index, monthly.values, marker='o', linestyle='-', label=company.capitalize(), color=colors[i % len(colors)])
    
    plt.title('Monthly News Articles by Company', fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Number of Articles')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    timeline_chart_path = os.path.join(PLOTS_DIR, 'monthly_articles_timeline.png')
    plt.savefig(timeline_chart_path)
    plots_info.append({
        'title': 'News Articles Timeline',
        'description': 'Line chart showing the monthly distribution of news articles for each company over time',
        'path': 'data/stats/plots/monthly_articles_timeline.png'
    })
    plt.close()
    
    return plots_info

def save_statistics(stats, plots_info):
    """Save statistics to a JSON file."""
    # Add plots information to stats
    stats['plots'] = plots_info
    
    # Save to JSON file
    stats_file = os.path.join(STATS_DIR, 'pharma_news_stats.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)
    
    return stats_file

def main():
    """Main function to generate statistics and visualizations."""
    print("Loading data...")
    dfs, combined_df = load_data()
    
    print("Calculating statistics...")
    stats = calculate_statistics(dfs, combined_df)
    
    print("Generating plots...")
    plots_info = generate_plots(dfs, combined_df, stats)
    
    print("Saving statistics...")
    stats_file = save_statistics(stats, plots_info)
    
    print(f"Statistics and visualizations generated successfully!")
    print(f"Statistics saved to: {stats_file}")
    print(f"Plots saved to: {PLOTS_DIR}")
    
    # Print summary
    print("\nSummary:")
    print(f"Total news articles: {stats['total_articles']}")
    print(f"Articles by company: {stats['company_counts']}")
    print(f"Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    print(f"Top categories: {list(sorted(stats['category_counts'].items(), key=lambda x: x[1], reverse=True)[:5])}")

if __name__ == "__main__":
    main() 