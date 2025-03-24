#!/usr/bin/env python3

"""Common utility functions used across the project."""

import os
import pandas as pd
from datetime import datetime
import logging

# Set up logging
def setup_logging(level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/scraper_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )
    return logging.getLogger(__name__)

# File operations
def ensure_directory(directory):
    """Ensure the directory exists, create if not."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def save_to_csv(data, filename, directory="data/raw"):
    """Save data to CSV file with proper naming."""
    ensure_directory(directory)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(directory, f"{filename}_{timestamp}.csv")
    
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return file_path

# Date handling
def parse_date(date_str, formats=None):
    """Parse date string using multiple possible formats."""
    if formats is None:
        formats = [
            '%B %d, %Y',  # e.g. "November 30, 2022"
            '%Y-%m-%dT%H:%M:%S',  # e.g. "2024-12-20T00:00:00"
            '%Y-%m-%d',  # e.g. "2024-12-20"
            '%m/%d/%Y',  # e.g. "12/20/2024"
            '%d %B %Y'  # e.g. "20 December 2024"
        ]
    
    if pd.isna(date_str) or not date_str:
        return None
    
    # Try pandas datetime parsing first
    try:
        return pd.to_datetime(date_str)
    except:
        # Try each format
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
    
    return None

# List all raw data files
def list_data_files(directory="data/raw", pattern="*.csv"):
    """List all data files in the given directory matching the pattern."""
    import glob
    return glob.glob(os.path.join(directory, pattern)) 