# Edge Favorites to PDF Converter

Convert Microsoft Edge favorites/bookmarks from a specific folder to individual PDFs and merge them into a single PDF file.

## Features

- Extract URLs from Edge favorites subfolder
- Convert each webpage to individual PDF
- Merge all PDFs into a single file
- Progress tracking and error handling
- Configurable settings
- Cross-platform support

## Installation

### Prerequisites

- Python 3.8 or higher
- Microsoft Edge browser
- Internet connection for downloading Edge WebDriver

### Quick Install

```bash
# Clone the repository
git clone https://github.com/anit-z/edge-favorites-to-pdf.git
cd edge-favorites-to-pdf

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .

## Usage
# Command Line Interface
# Convert a specific bookmark folder to PDF
edge2pdf --folder "Work Bookmarks" --output work_sites.pdf

# Using short options
edge2pdf -f "Research" -o research.pdf

# Get help
edge2pdf --help

# Python API
from src.favorites_parser import EdgeFavoritesParser
from src.pdf_converter import PDFConverter

# Parse bookmarks
parser = EdgeFavoritesParser()
urls = parser.get_urls_from_folder("My Folder")

# Convert to PDF
with PDFConverter() as converter:
    converter.convert_urls_to_pdf(urls, "output.pdf")