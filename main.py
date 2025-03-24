#!/usr/bin/env python3

"""
Main entry point for the Pharma Insights Scraper.
This script allows running different scrapers and data processing tools.
"""

import argparse
import asyncio
import os
import sys

# Add src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description='Pharma Insights Scraper')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scraper command
    scrape_parser = subparsers.add_parser('scrape', help='Run scrapers')
    scrape_parser.add_argument('--company', '-c', choices=['pfizer', 'merck', 'lilly', 'all'], 
                              default='all', help='Company to scrape')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process scraped data')
    process_parser.add_argument('--input', '-i', help='Input file or directory')
    process_parser.add_argument('--output', '-o', help='Output file or directory')
    
    return parser

async def run_pfizer_scraper():
    """Run the Pfizer scraper."""
    from scrapers.pfizer_scraper import main as pfizer_main
    await pfizer_main()

async def run_merck_scraper():
    """Run the Merck scraper."""
    from scrapers.merck_scraper import main as merck_main
    await merck_main()

async def run_lilly_scraper():
    """Run the Lilly scraper."""
    from scrapers.lilly_scraper import main as lilly_main
    await lilly_main()

async def run_scrapers(company):
    """Run the selected scrapers."""
    if company == 'all' or company == 'pfizer':
        print("Running Pfizer scraper...")
        await run_pfizer_scraper()
    
    if company == 'all' or company == 'merck':
        print("Running Merck scraper...")
        await run_merck_scraper()
    
    if company == 'all' or company == 'lilly':
        print("Running Lilly scraper...")
        await run_lilly_scraper()

def process_data(input_path, output_path):
    """Process scraped data."""
    from data_processing.clean_data import process_files
    from data_processing.clean_body import process_file
    
    print(f"Processing data from {input_path} to {output_path}...")
    # Implementation depends on the specific processing needs
    
    if not output_path:
        output_path = 'data/processed'
        
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Example implementation:
    # process_files(input_path, output_path)
    
    print("Data processing complete.")

def main():
    """Main entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.command == 'scrape':
        asyncio.run(run_scrapers(args.company))
    elif args.command == 'process':
        process_data(args.input, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 