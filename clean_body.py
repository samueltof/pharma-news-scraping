import pandas as pd
import re

def clean_press_release_text(text):
    """Clean press release text by removing boilerplate and formatting"""
    if pd.isna(text):
        return text
        
    # Remove Pfizer logo and header
    text = re.sub(r'\[!\[Pfizer logo\].*?\]\(.*?\)', '', text)
    
    # Remove navigation sections with ## headers
    text = re.sub(r'##\s*\*\s*\[.*?\].*?(?=##|\Z)', '', text, flags=re.DOTALL)
    
    # Remove email subscription and pipeline promotion
    text = re.sub(r'#{1,5}\s*Receive real-time updates.*?inbox\..*?pipeline\.', '', text, flags=re.DOTALL)
    
    # Remove markdown-style links
    text = re.sub(r"\[.*?\]\(.*?\)", "", text, flags=re.DOTALL)
    
    # Remove leftover bracketed text
    text = re.sub(r"\[.*?\]", "", text, flags=re.DOTALL)
    
    # Remove text in parentheses
    text = re.sub(r"\(.*?\)", "", text, flags=re.DOTALL)
    
    # Remove search box pattern
    text = re.sub(r"What can we help you find\? Search for: &gt;&gt;News release ##", "", text)
    
    # Split into lines for filtering
    lines = text.splitlines()
    
    # Add Pfizer-specific patterns
    extraneous_keywords = [
        "skip to main content",
        "select your country or region",
        "all rights reserved",
        "terms of use",
        "privacy statement",
        "accessibility statement",
        "sitemap",
        "copyright",
        "follow us on",
        "social media",
        "facebook",
        "twitter",
        "linkedin",
        "instagram",
        "youtube",
        "call(800)",
        "investors",
        "sources",
        "suppliers",
        "contact",
        "diversity",
        "menu",
        "pdf version",
        "search for",
        "what can we help you find",
        "hamburger",
        "header close",
        "changed",
        "how can we help you",
        "suggestions within pfizer.com",
        "view pdf",
        "copy to clipboard",
        "open in tab",
        "receive real-time updates",
        "delivered directly to your inbox",
        "visualized product pipeline",
        "check out our new"
    ]
    
    cleaned_lines = []
    for line in lines:
        lower_line = line.lower().strip()
        if any(keyword in lower_line for keyword in extraneous_keywords):
            continue
        if line.strip():  # Only keep non-empty lines
            cleaned_lines.append(line.strip())
    
    # Rejoin filtered lines
    cleaned_text = "\n".join(cleaned_lines)
    
    # Clean up extra whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def process_file(file_path):
    """Process a single file and clean its body content"""
    df = pd.read_csv(file_path)
    if 'body' in df.columns:
        df['body'] = df['body'].apply(clean_press_release_text)
    return df

files = [
    # 'data/processed/merck_news_cleaned.csv'
    'data/processed/pfizer_news_cleaned.csv'
]

for file_path in files:
    print(f"Processing {file_path}")
    df = process_file(file_path)
    output_path = file_path.replace('data/processed', 'data/output')
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned {output_path}")
