"""Main entry point for Edge Favorites to PDF converter"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from .favorites_parser import EdgeFavoritesParser
from .pdf_converter import PDFConverter
from .pdf_merger import PDFMerger


# Setup logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # File handler
    log_file = f"logs/conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


class FavoritesToPDF:
    """Main converter class"""
    
    def __init__(self, config: dict = None):
        self.config = config or self.default_config()
        self.parser = EdgeFavoritesParser()
        
    @staticmethod
    def default_config():
        """Default configuration"""
        return {
            'parallel_downloads': 1,
            'timeout_seconds': 30,
            'page_load_delay': 2,
            'headless': True,
            'add_bookmarks': True,
            'pdf_options': {
                'format': 'A4',
                'margin': {
                    'top': '20px',
                    'right': '20px',
                    'bottom': '20px',
                    'left': '20px'
                }
            }
        }
    
    def convert_folder(self, folder_name: str, output_path: str):
        """Convert all bookmarks in a folder to PDF"""
        logger = logging.getLogger(__name__)
        
        # Create temp directory for individual PDFs
        temp_dir = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Step 1: Parse favorites
            logger.info(f"Parsing Edge favorites folder: {folder_name}")
            urls = self.parser.get_urls_from_folder(folder_name)
            logger.info(f"Found {len(urls)} bookmarks in folder '{folder_name}'")
            
            if not urls:
                logger.warning("No bookmarks found in the specified folder")
                return
            
            # Step 2: Convert URLs to PDFs
            logger.info("Converting web pages to PDFs...")
            with PDFConverter(
                headless=self.config['headless'],
                timeout=self.config['timeout_seconds'],
                page_load_delay=self.config['page_load_delay']
            ) as converter:
                pdf_files = converter.convert_urls(urls, temp_dir)
            
            # Step 3: Merge PDFs
            if pdf_files:
                logger.info(f"Merging {len(pdf_files)} PDFs...")
                success = PDFMerger.merge_pdfs(
                    pdf_files, 
                    output_path,
                    add_bookmarks=self.config['add_bookmarks']
                )
                
                if success:
                    logger.info(f"Successfully created: {output_path}")
                else:
                    logger.error("Failed to merge PDFs")
            else:
                logger.error("No PDFs were successfully created")
            
        finally:
            # Cleanup temp directory
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("Cleaned up temporary files")
    
    def list_folders(self):
        """List all available favorites folders"""
        folders = self.parser.list_all_folders()
        print("\nAvailable Edge Favorites Folders:")
        print("-" * 40)
        for folder in folders:
            print(f"  • {folder}")
        print("-" * 40)
        return folders


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Convert Edge favorites to PDF"
    )
    
    parser.add_argument(
        '--folder', '-f',
        help='Name of the Edge favorites folder to convert'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output PDF file path',
        default='output/combined.pdf'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--list-folders', '-l',
        action='store_true',
        help='List all available favorites folders'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (not headless)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    if args.no_headless:
        config['headless'] = False
    
    # Create converter
    converter = FavoritesToPDF(config)
    
    # Handle commands
    if args.list_folders:
        converter.list_folders()
    elif args.folder:
        converter.convert_folder(args.folder, args.output)
    else:
        # Interactive mode
        print("\n=== Edge Favorites to PDF Converter ===\n")
        
        folders = converter.list_folders()
        
        if not folders:
            logger.error("No favorites folders found")
            return
        
        # Get user input
        folder_name = input("\nEnter folder name to convert: ").strip()
        
        if folder_name:
            output_path = input("Enter output PDF path (default: output/combined.pdf): ").strip()
            output_path = output_path or "output/combined.pdf"
            
            converter.convert_folder(folder_name, output_path)


if __name__ == "__main__":
    main()