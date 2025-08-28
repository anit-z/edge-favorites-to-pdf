"""Merge multiple PDFs into one"""
import os
from typing import List
import PyPDF2
from tqdm import tqdm
import logging


logger = logging.getLogger(__name__)


class PDFMerger:
    """Merge multiple PDF files"""
    
    @staticmethod
    def merge_pdfs(pdf_files: List[str], output_path: str, 
                   add_bookmarks: bool = True) -> bool:
        """Merge multiple PDFs into a single file"""
        if not pdf_files:
            logger.error("No PDF files to merge")
            return False
        
        merger = PyPDF2.PdfMerger()
        
        try:
            # Progress bar for merging
            progress_bar = tqdm(pdf_files, desc="Merging PDFs", unit="file")
            
            for pdf_file in progress_bar:
                if os.path.exists(pdf_file):
                    try:
                        # Extract bookmark name from filename
                        bookmark_name = os.path.basename(pdf_file)
                        bookmark_name = bookmark_name.split('_', 1)[-1]  # Remove number prefix
                        bookmark_name = os.path.splitext(bookmark_name)[0]  # Remove .pdf
                        
                        # Add PDF to merger
                        with open(pdf_file, 'rb') as f:
                            merger.append(f, bookmark_name if add_bookmarks else None)
                            
                        progress_bar.set_postfix({'current': bookmark_name[:30]})
                        
                    except Exception as e:
                        logger.error(f"Error adding {pdf_file}: {str(e)}")
                else:
                    logger.warning(f"File not found: {pdf_file}")
            
            # Write merged PDF
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            merger.close()
            
            # Verify output
            if os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                logger.info(f"Successfully created merged PDF: {output_path} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("Failed to create merged PDF")
                return False
                
        except Exception as e:
            logger.error(f"Error during PDF merge: {str(e)}")
            return False
        finally:
            merger.close()
    
    @staticmethod
    def merge_pdfs_with_toc(pdf_files: List[str], output_path: str, 
                           toc_title: str = "Table of Contents") -> bool:
        """Merge PDFs with a table of contents page"""
        # This is an advanced feature - implement if needed
        pass