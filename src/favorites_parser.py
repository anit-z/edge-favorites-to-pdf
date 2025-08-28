"""Parse Edge favorites/bookmarks"""
import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class EdgeFavoritesParser:
    """Parser for Microsoft Edge favorites"""
    
    def __init__(self):
        self.edge_profile_path = self._get_edge_profile_path()
        self.bookmarks_file = os.path.join(self.edge_profile_path, "Bookmarks")
    
    @staticmethod
    def _get_edge_profile_path() -> str:
        """Get Edge default profile path"""
        if os.name == 'nt':  # Windows
            base_path = os.path.join(os.environ['LOCALAPPDATA'], 
                                   'Microsoft', 'Edge', 'User Data', 'Default')
        elif os.name == 'posix':  # macOS/Linux
            if 'darwin' in os.sys.platform:
                base_path = os.path.expanduser(
                    '~/Library/Application Support/Microsoft Edge/Default')
            else:
                base_path = os.path.expanduser(
                    '~/.config/microsoft-edge/Default')
        else:
            raise OSError(f"Unsupported OS: {os.name}")
        
        return base_path
    
    def parse_bookmarks(self) -> Dict:
        """Parse Edge bookmarks file"""
        if not os.path.exists(self.bookmarks_file):
            raise FileNotFoundError(f"Bookmarks file not found: {self.bookmarks_file}")
        
        with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def find_folder(self, folder_name: str, node: Dict = None) -> Optional[Dict]:
        """Recursively find a folder by name"""
        if node is None:
            bookmarks = self.parse_bookmarks()
            # Search in all roots
            for root_name, root in bookmarks['roots'].items():
                if 'children' in root:
                    for child in root['children']:
                        result = self._search_node(child, folder_name)
                        if result:
                            return result
            return None
        else:
            return self._search_node(node, folder_name)

    def _search_node(self, node: Dict, folder_name: str) -> Optional[Dict]:
        """Helper method to search in a single node"""
        # Check if current node matches
        if node.get('type') == 'folder' and node.get('name') == folder_name:
            return node
        
        # Search in children
        if 'children' in node:
            for child in node['children']:
                result = self._search_node(child, folder_name)
                if result:
                    return result
        
        return None
    
    def get_urls_from_folder(self, folder_name: str) -> List[Dict[str, str]]:
        """Extract all URLs from a specific favorites folder"""
        folder = self.find_folder(folder_name)
        
        if not folder:
            raise ValueError(f"Folder '{folder_name}' not found in Edge favorites")
        
        urls = []
        self._extract_urls(folder, urls)
        
        return urls
    
    def _extract_urls(self, node: Dict, urls: List[Dict[str, str]]):
        """Recursively extract URLs from bookmarks node"""
        if node.get('type') == 'url':
            urls.append({
                'name': node.get('name', 'Untitled'),
                'url': node.get('url', ''),
                'date_added': node.get('date_added', '')
            })
        elif 'children' in node:
            for child in node['children']:
                self._extract_urls(child, urls)
    
    def list_all_folders(self) -> List[str]:
        """List all available favorite folders"""
        bookmarks = self.parse_bookmarks()
        folders = []
        self._list_folders(bookmarks['roots'], folders)
        return folders
    
    def _list_folders(self, node: Dict, folders: List[str], path: str = ""):
        """Recursively list all folders"""
        if isinstance(node, dict):
            if node.get('type') == 'folder' and 'name' in node:
                current_path = f"{path}/{node['name']}" if path else node['name']
                folders.append(current_path)
                
            if 'children' in node:
                for child in node['children']:
                    self._list_folders(child, folders, 
                                     f"{path}/{node.get('name', '')}" if path else node.get('name', ''))
            elif isinstance(node, dict):
                for value in node.values():
                    if isinstance(value, dict):
                        self._list_folders(value, folders, path)