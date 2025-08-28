"""Convert web pages to PDF"""
import os
import time
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import base64
from tqdm import tqdm
import logging


logger = logging.getLogger(__name__)


class PDFConverter:
    """Convert web pages to PDF using Selenium"""
    
    def __init__(self, headless: bool = True, timeout: int = 30, 
                 page_load_delay: int = 2):
        self.headless = headless
        self.timeout = timeout
        self.page_load_delay = page_load_delay
        self.driver = None
        self.pdf_options = {
            'landscape': False,
            'displayHeaderFooter': True,
            'printBackground': True,
            'scale': 1.0,
            'paperWidth': 8.27,  # A4
            'paperHeight': 11.69,  # A4
            'marginTop': 0.4,
            'marginBottom': 0.4,
            'marginLeft': 0.4,
            'marginRight': 0.4,
            'headerTemplate': '<div></div>',
            'footerTemplate': '<div style="font-size:10px; text-align:center; width:100%;">' + 
                            '<span class="pageNumber"></span> / <span class="totalPages"></span></div>'
        }
    
    def __enter__(self):
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def setup_driver(self):
        """Setup Edge WebDriver"""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
            
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        # Setup service
        service = Service(EdgeChromiumDriverManager().install())
        
        self.driver = webdriver.Edge(service=service, options=options)
        self.driver.set_page_load_timeout(self.timeout)
    
    def cleanup(self):
        """Clean up driver resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def url_to_pdf(self, url: str, output_path: str) -> bool:
        """Convert a single URL to PDF"""
        try:
            # Load the page
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional delay for dynamic content
            time.sleep(self.page_load_delay)
            
            # Generate PDF
            result = self.driver.execute_cdp_cmd('Page.printToPDF', self.pdf_options)
            
            # Save PDF
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(result['data']))
            
            return True
            
        except TimeoutException:
            logger.error(f"Timeout loading URL: {url}")
            return False
        except WebDriverException as e:
            logger.error(f"WebDriver error for URL {url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error for URL {url}: {str(e)}")
            return False
    
    def convert_urls(self, urls: List[Dict[str, str]], output_dir: str, 
                    progress_callback=None) -> List[str]:
        """Convert multiple URLs to PDFs"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.driver:
            self.setup_driver()
        
        pdf_files = []
        failed_urls = []
        
        # Progress bar
        progress_bar = tqdm(urls, desc="Converting to PDF", unit="page")
        
        for i, item in enumerate(progress_bar):
            url = item['url']
            name = self._sanitize_filename(item['name'])
            output_path = os.path.join(output_dir, f"{i+1:04d}_{name}.pdf")
            
            progress_bar.set_postfix({'current': name[:30]})
            
            if self.url_to_pdf(url, output_path):
                pdf_files.append(output_path)
                logger.info(f"Successfully converted: {name}")
            else:
                failed_urls.append(item)
                logger.warning(f"Failed to convert: {name} ({url})")
            
            if progress_callback:
                progress_callback(i + 1, len(urls))
        
        # Log summary
        logger.info(f"Conversion complete: {len(pdf_files)}/{len(urls)} successful")
        
        if failed_urls:
            # Save failed URLs for retry
            import json
            with open(os.path.join(output_dir, 'failed_urls.json'), 'w') as f:
                json.dump(failed_urls, f, indent=2)
        
        return pdf_files
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        filename = filename[:100]
        
        # Remove trailing dots and spaces
        filename = filename.rstrip('. ')
        
        return filename or 'untitled'