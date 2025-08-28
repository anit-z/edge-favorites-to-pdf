"""Edge Favorites to PDF Converter"""
from .main import FavoritesToPDF
from .favorites_parser import EdgeFavoritesParser
from .pdf_converter import PDFConverter
from .pdf_merger import PDFMerger

__version__ = "1.0.0"
__all__ = ["FavoritesToPDF", "EdgeFavoritesParser", "PDFConverter", "PDFMerger"]