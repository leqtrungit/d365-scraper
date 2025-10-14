#!/usr/bin/env python3
"""
Microsoft Learn Course Scraper
Generic scraper for Microsoft Learn training modules
Input: Module UID (e.g., learn-dynamics.get-started-financial-management-in-dynamics-365-finance-ops)
Output: JSON file with complete course data including all units
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import argparse
from typing import Dict, List, Optional
import time
from urllib.parse import urljoin


class MicrosoftLearnScraper:
    """Generic scraper for Microsoft Learn training modules"""
    
    API_BASE = "https://learn.microsoft.com/api/catalog"
    
    def __init__(self, uid: str):
        """
        Initialize scraper with module UID
        
        Args:
            uid: Module UID (e.g., learn-dynamics.get-started-financial-management-in-dynamics-365-finance-ops)
        """
        self.uid = uid
        self.module_data = None
        self.units_data = []
        
    def fetch_module_metadata(self) -> Dict:
        """
        Fetch module metadata from API
        
        Returns:
            Dict containing module information
        """
        try:
            response = requests.get(f"{self.API_BASE}?uid={self.uid}")
            response.raise_for_status()
            data = response.json()
            
            if not data.get('modules') or len(data['modules']) == 0:
                raise ValueError(f"No module found for UID: {self.uid}")
            
            self.module_data = data['modules'][0]
            return self.module_data
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch module metadata: {e}")
    
    def scrape_module_page_for_unit_urls(self) -> List[str]:
        """
        Scrape the module page to get actual unit URLs
        
        Returns:
            List of unit URLs
        """
        module_url = self.module_data.get('url', '')
        if not module_url:
            raise ValueError("No module URL found in module data")
        
        # Remove query parameters
        module_url = module_url.split('?')[0]
        
        try:
            response = requests.get(module_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            unit_urls = []
            
            # Find the units list in the module page
            # Look for list items that contain unit links
            main_content = soup.find('main')
            if main_content:
                # Find all links that appear to be unit links (relative paths with numbers)
                links = main_content.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    # Unit links are relative and start with a number followed by dash
                    # e.g., "1-introduction", "2-benefits", etc.
                    if href and not href.startswith(('http', '#', '/')):
                        # Check if it looks like a unit slug (starts with number-text pattern)
                        if href[0].isdigit() and '-' in href:
                            full_url = f"{module_url}{href}/"
                            unit_urls.append(full_url)
            
            return unit_urls
            
        except requests.RequestException as e:
            raise Exception(f"Failed to scrape module page: {e}")
    
    def scrape_unit_content(self, url: str) -> Dict:
        """
        Scrape content from a single unit page
        
        Args:
            url: Unit page URL
            
        Returns:
            Dict containing unit content
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.text.strip() if title_elem else ""
            
            # Extract duration - look for time indicators like "X minutes", "X min", "X hr"
            duration = ""
            # Try to find duration in various locations
            time_elements = soup.find_all('li')
            for elem in time_elements:
                text = elem.get_text(strip=True)
                if any(keyword in text.lower() for keyword in ['minute', 'min', 'hr', 'hour']):
                    # Check if it's just a time duration (not part of a longer sentence)
                    if len(text.split()) <= 3:
                        duration = text
                        break
            
            # Extract main content
            content_data = {
                'url': url,
                'title': title,
                'duration': duration,
                'paragraphs': [],
                'lists': [],
                'images': [],
                'links': []
            }
            
            # Find main content area (look for the main article content)
            main_content = soup.find('main')
            if main_content:
                # Extract paragraphs
                # Filter out common UI/feedback text
                exclude_phrases = [
                    'was this page helpful',
                    'need help',
                    'ask learn',
                    'feedback',
                    'troubleshooting'
                ]
                
                paragraphs = main_content.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Skip empty paragraphs and common UI text
                    if text and len(text) > 0:
                        # Check if paragraph contains excluded phrases
                        text_lower = text.lower()
                        if not any(phrase in text_lower for phrase in exclude_phrases):
                            content_data['paragraphs'].append(text)
                
                # Extract lists (ul, ol)
                lists = main_content.find_all(['ul', 'ol'])
                for lst in lists:
                    # Skip navigation lists
                    if 'breadcrumbs' in lst.get('class', []):
                        continue
                    
                    list_items = []
                    for li in lst.find_all('li', recursive=False):
                        text = li.get_text(strip=True)
                        if text:
                            list_items.append(text)
                    
                    if list_items:
                        content_data['lists'].append({
                            'type': lst.name,
                            'items': list_items
                        })
                
                # Extract images
                images = main_content.find_all('img')
                for img in images:
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    if src and 'docon' not in src:  # Skip icon fonts
                        # For relative URLs starting with 'media/', use module base URL
                        if src.startswith('media/'):
                            # Get module base URL by removing the last two segments (unit slug)
                            # e.g., .../module-name/1-introduction/ -> .../module-name/
                            module_base_url = '/'.join(url.rstrip('/').split('/')[:-1]) + '/'
                            absolute_src = urljoin(module_base_url, src)
                        else:
                            # For other relative URLs, use current page URL
                            absolute_src = urljoin(url, src)
                        
                        content_data['images'].append({
                            'src': absolute_src,
                            'alt': alt
                        })
                
                # Extract links (excluding navigation)
                links = main_content.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if href and text and not href.startswith('#'):
                        # Convert relative URLs to absolute URLs
                        absolute_href = urljoin(url, href)
                        content_data['links'].append({
                            'text': text,
                            'href': absolute_href
                        })
            
            return content_data
            
        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}", file=sys.stderr)
            return {
                'url': url,
                'error': str(e)
            }
    
    def scrape_all_units(self) -> List[Dict]:
        """
        Scrape all units in the module
        
        Returns:
            List of unit data dictionaries
        """
        if not self.module_data:
            raise ValueError("Module metadata not fetched. Call fetch_module_metadata() first.")
        
        # Get unit URLs from module page
        print("Fetching unit URLs from module page...", file=sys.stderr)
        unit_urls = self.scrape_module_page_for_unit_urls()
        
        if not unit_urls:
            raise ValueError("No unit URLs found on module page")
        
        print(f"Found {len(unit_urls)} units", file=sys.stderr)
        print(f"Scraping unit content...", file=sys.stderr)
        
        # Get UIDs for reference
        unit_uids = self.module_data.get('units', [])
        
        for i, url in enumerate(unit_urls, 1):
            print(f"[{i}/{len(unit_urls)}] Scraping: {url}", file=sys.stderr)
            
            unit_data = self.scrape_unit_content(url)
            # Try to match with UID if available
            if i <= len(unit_uids):
                unit_data['uid'] = unit_uids[i-1]
            unit_data['order'] = i
            
            self.units_data.append(unit_data)
            
            # Be polite - add delay between requests
            if i < len(unit_urls):
                time.sleep(0.5)
        
        return self.units_data
    
    def get_complete_data(self) -> Dict:
        """
        Get complete scraped data including module metadata and all units
        
        Returns:
            Dict containing complete course data
        """
        return {
            'module': {
                'uid': self.module_data.get('uid'),
                'title': self.module_data.get('title'),
                'summary': self.module_data.get('summary'),
                'duration_in_minutes': self.module_data.get('duration_in_minutes'),
                'levels': self.module_data.get('levels', []),
                'roles': self.module_data.get('roles', []),
                'products': self.module_data.get('products', []),
                'subjects': self.module_data.get('subjects', []),
                'url': self.module_data.get('url'),
                'number_of_units': len(self.units_data)
            },
            'units': self.units_data
        }
    
    def save_to_json(self, filename: str = 'course_data.json'):
        """
        Save scraped data to JSON file
        
        Args:
            filename: Output filename
        """
        data = self.get_complete_data()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\nData saved to {filename}", file=sys.stderr)


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description='Scrape Microsoft Learn training modules',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  python test_scraper.py learn-dynamics.get-started-financial-management-in-dynamics-365-finance-ops
  python test_scraper.py learn-dynamics.get-started-financial-management-in-dynamics-365-finance-ops -o output.json
        '''
    )
    
    parser.add_argument('uid', help='Module UID to scrape')
    parser.add_argument('-o', '--output', default='course_data.json', 
                       help='Output JSON file (default: course_data.json)')
    
    args = parser.parse_args()
    
    try:
        scraper = MicrosoftLearnScraper(args.uid)
        
        print(f"Fetching module metadata for: {args.uid}", file=sys.stderr)
        scraper.fetch_module_metadata()
        
        print(f"Module: {scraper.module_data.get('title')}", file=sys.stderr)
        print(f"Units: {len(scraper.module_data.get('units', []))}", file=sys.stderr)
        
        scraper.scrape_all_units()
        scraper.save_to_json(args.output)
        
        print("\nScraping completed successfully!", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()