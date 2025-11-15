"""
Web scraping tool for venue information (addresses, details)
Uses BeautifulSoup to scrape public data without requiring API keys
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import time
import re


def scrape_google_search(venue_name: str, location: str) -> Optional[Dict[str, str]]:
    """
    Scrape Google search results for venue address and details
    
    Args:
        venue_name: Name of the venue/restaurant/place
        location: City or area
        
    Returns:
        Dict with address, phone, website if found
    """
    try:
        # Add "address" to search query for better results
        query_with_address = f"{venue_name} {location} address"
        url = f"https://www.google.com/search?q={requests.utils.quote(query_with_address)}"
        
        # Rotate user agents to avoid blocking
        import random
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
        }
        
        # Add small random delay to avoid rate limiting
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        result = {
            'address': None,
            'phone': None,
            'website': None
        }
        
        # Try multiple methods to find address
        
        # Method 1: Look for specific Google business card elements
        address_divs = soup.find_all('span', class_=lambda x: x and 'LrzXr' in str(x))
        for div in address_divs:
            text = div.get_text(strip=True)
            if any(word in text for word in ['St', 'Ave', 'Road', 'Blvd', 'Drive', 'Lane', 'Way', 'Street']):
                result['address'] = text
                break
        
        # Method 2: Look in any span/div that contains address-like text
        if not result['address']:
            all_text_elements = soup.find_all(['span', 'div', 'a'])
            for elem in all_text_elements:
                text = elem.get_text(strip=True)
                # More comprehensive address patterns
                address_patterns = [
                    r'\d+\s+[A-Z][a-zA-Z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Plaza|Square|Circle|Parkway|Pkwy)(?:[\s,]+[A-Za-z\s]+)?(?:,\s*[A-Z]{2})?\s*\d{5}',
                    r'\d+\s+[A-Z][a-zA-Z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)[,\s]+[A-Za-z\s]+',
                    r'\d{1,5}\s+[A-Z][a-zA-Z\s]+\w+.*(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way)'
                ]
                
                for pattern in address_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        potential_address = match.group(0).strip()
                        # Validate it's not too short and contains a number
                        if len(potential_address) > 10 and re.search(r'\d', potential_address):
                            result['address'] = potential_address
                            break
                if result['address']:
                    break
        
        # Try to find phone number
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        text_content = soup.get_text()
        phone_match = re.search(phone_pattern, text_content)
        if phone_match:
            result['phone'] = phone_match.group(0).strip()
        
        return result if result['address'] else None
        
    except Exception as e:
        print(f"Error scraping {venue_name}: {str(e)}")
        return None


def scrape_yelp_business(venue_name: str, location: str) -> Optional[Dict[str, str]]:
    """
    Scrape Yelp for business information
    
    Args:
        venue_name: Name of the business
        location: City or area
        
    Returns:
        Dict with address, rating, price range if found
    """
    try:
        # Clean venue name for URL
        clean_name = venue_name.lower().replace(' ', '-').replace("'", '')
        clean_location = location.lower().replace(' ', '-')
        
        # Try common Yelp URL pattern
        url = f"https://www.yelp.com/biz/{clean_name}-{clean_location}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        if response.status_code != 200:
            # Try searching instead
            search_url = f"https://www.yelp.com/search?find_desc={requests.utils.quote(venue_name)}&find_loc={requests.utils.quote(location)}"
            response = requests.get(search_url, headers=headers, timeout=10, verify=False)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        result = {
            'address': None,
            'rating': None,
            'price': None
        }
        
        # Look for address in common Yelp selectors
        address_elem = soup.find('address')
        if address_elem:
            result['address'] = address_elem.get_text(strip=True)
        
        return result if result['address'] else None
        
    except Exception as e:
        print(f"Error scraping Yelp for {venue_name}: {str(e)}")
        return None


def get_venue_details(venue_name: str, location: str, venue_type: str = "restaurant") -> Dict[str, str]:
    """
    Get venue details using web scraping (no API key needed)
    
    Args:
        venue_name: Name of the venue
        location: City/area
        venue_type: Type of venue (restaurant, movie, outdoor, event)
        
    Returns:
        Dict with available information
    """
    result = {
        'name': venue_name,
        'address': 'Address not found',
        'phone': None,
        'website': None
    }
    
    # Try Google search first (most reliable)
    google_data = scrape_google_search(venue_name, location)
    if google_data and google_data.get('address'):
        result['address'] = google_data['address']
        result['phone'] = google_data.get('phone')
        result['website'] = google_data.get('website')
        return result
    
    # Fallback to Yelp for restaurants
    if venue_type == 'restaurant':
        yelp_data = scrape_yelp_business(venue_name, location)
        if yelp_data and yelp_data.get('address'):
            result['address'] = yelp_data['address']
            return result
    
    # If nothing found, return None so summarizer can handle it gracefully
    result['address'] = None
    return result


# Test function
if __name__ == "__main__":
    # Test with a known restaurant
    details = get_venue_details("Poor Calvin's", "Atlanta", "restaurant")
    print(f"Name: {details['name']}")
    print(f"Address: {details['address']}")
    print(f"Phone: {details.get('phone', 'N/A')}")
