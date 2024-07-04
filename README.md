# Data Scrapy Project: bhhsamp

## Project Overview
This Scrapy project (bhhsamp) is designed to scrape agent information from the website BHHSAMB. It collects detailed data about real estate agents including their names, contact details, addresses, descriptions, and social media profiles where available. The scraped data is then stored in both JSON and CSV formats for further analysis or integration into other systems.

## Features
- Data Extraction: Extracts agent information such as name, image URL, phone number, address, description, and social media links (Facebook, Twitter, LinkedIn, YouTube, Pinterest, Instagram).
- Data Storage: Stores scraped data in both JSON (agents_data.json) and CSV (agents_data.csv) formats.
- Pagination Handling: Handles pagination to ensure all agent listings are visited and data is extracted comprehensively.
- Custom Headers: Includes custom HTTP headers to mimic browser requests and handle specific website requirements.

## Dependencies
- Scrapy: A powerful web scraping framework for Python.
- json: Python's built-in module for JSON handling.
- csv: Python's built-in module for CSV handling.
- logging: Python's built-in module for logging information during script execution.

## Setup
To run this project, ensure you have Python installed along with the required dependencies. You can install Scrapy using pip: (pip install scrapy)

## Usage
- Clone the Repository:
- Running the Spider: (scrapy crawl bhhsamp). This command starts the spider, which will begin 
  scraping agent data from the specified website.
- Output Files: . agents_data.json: Contains scraped data in JSON format.
                . agents_data.csv: Contains scraped data in CSV format.

## Output Files
- JSON (agents_data.json): Contains detailed agent information in JSON format, stored as individual lines for each agent.
- CSV (agents_data.csv): Stores the same agent information in CSV format, with each field separated by commas and each agent's data on a new row.

## Configuration
Headers: Custom HTTP headers are defined in settings.py to ensure compatibility with the website's requirements.

