# Pharma Insights Scraper

A tool for scraping pharmaceutical news and press releases from major pharmaceutical companies' websites to gather insights about industry trends, regulatory approvals, clinical trials, and more.

## Features

- Scrapes news articles from major pharmaceutical companies:
  - Pfizer
  - Merck
  - Eli Lilly
- Cleans and processes the scraped data
- Categorizes news articles by type (regulatory approval, clinical trial updates, etc.)
- Stores data in structured CSV format

## Project Structure

```
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── scrapers/           # Company-specific web scrapers
│   ├── utils/              # Helper utilities
│   └── data_processing/    # Data cleaning and processing
└── data/
    ├── raw/                # Raw scraped data
    ├── processed/          # Processed data
    └── clean/              # Final cleaned dataset
```

## Setup and Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/pharma-insights-scraper.git
cd pharma-insights-scraper
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env file with your API keys
```

## Usage

### Running the scrapers

```bash
# Run scrapers for specific companies
python src/scrapers/pfizer_scraper.py
python src/scrapers/merck_scraper.py
python src/scrapers/lilly_scraper.py

# Process and clean the data
python src/data_processing/clean_data.py
```

## API Keys Required

This project requires API keys for:
- AgentQL
- Spider API

## License

[MIT License](LICENSE) 