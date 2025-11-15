"""
CrewAI tools for weekend planner agents
"""

from crewai.tools import tool
from typing import Dict, List
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from tools.venue_scraper import get_venue_details
from tools.budget_estimator import analyze_itinerary_budget, format_budget_summary


@tool("Get Venue Address")
def get_venue_address(venue_name: str, location: str, venue_type: str = "restaurant") -> str:
    """
    Get the address and contact details for a venue using web scraping.
    No API key required.
    
    Args:
        venue_name: Name of the venue/restaurant/place
        location: City or area (e.g., "Atlanta", "Austin")
        venue_type: Type of venue - "restaurant", "movie", "outdoor", or "event"
    
    Returns:
        JSON string with venue details including address, phone, website
    
    Example:
        get_venue_address("Poor Calvin's", "Atlanta", "restaurant")
    """
    try:
        details = get_venue_details(venue_name, location, venue_type)
        return json.dumps(details, indent=2)
    except Exception as e:
        return json.dumps({
            'name': venue_name,
            'address': f'Could not find address: {str(e)}',
            'phone': None,
            'website': None
        })


@tool("Calculate Budget")
def calculate_itinerary_budget(activities_json: str, group_size: int = 1, location: str = None) -> str:
    """
    Calculate estimated budget for a list of activities in local currency.
    
    Args:
        activities_json: JSON string of activities list. Each activity should have:
                        - name: Activity name
                        - type: One of "restaurant", "movie", "outdoor", "event"
                        - rating: Star rating (float)
                        - details: Description text
        group_size: Number of people in the group (default: 1)
        location: City/location name for currency detection (e.g., "Seattle", "London", "Tokyo")
    
    Returns:
        JSON with budget breakdown per activity (not summary) for the itinerary writer to format
    
    Example:
        activities = [
            {"name": "Restaurant", "type": "restaurant", "rating": 4.5, "details": "upscale dining"},
            {"name": "Movie", "type": "movie", "rating": 4.0, "details": "evening show"}
        ]
        calculate_itinerary_budget(json.dumps(activities), group_size=2, location="Seattle")
    """
    try:
        activities = json.loads(activities_json)
        analysis = analyze_itinerary_budget(activities, group_size, location)
        
        # Return breakdown per activity for the summarizer to integrate
        result = {
            'currency_symbol': analysis['currency_symbol'],
            'currency_code': analysis['currency_code'],
            'location': location,
            'group_size': group_size,
            'activities_with_costs': []
        }
        
        for item in analysis['breakdown']:
            activity_cost = {
                'name': item['name'],
                'type': item['type'],
                'cost_display': ''
            }
            
            if item['total_min'] == 0:
                activity_cost['cost_display'] = 'FREE'
            elif group_size > 1:
                activity_cost['cost_display'] = f"{analysis['currency_symbol']}{item['min_per_person']:.0f}-{analysis['currency_symbol']}{item['max_per_person']:.0f}/person ({analysis['currency_symbol']}{item['total_min']:.0f}-{analysis['currency_symbol']}{item['total_max']:.0f} total)"
            else:
                activity_cost['cost_display'] = f"{analysis['currency_symbol']}{item['total_min']:.0f}-{analysis['currency_symbol']}{item['total_max']:.0f}"
            
            result['activities_with_costs'].append(activity_cost)
        
        # Add total
        result['total_cost_display'] = f"{analysis['currency_symbol']}{analysis['total_min']:.0f}-{analysis['currency_symbol']}{analysis['total_max']:.0f}"
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            'error': f'Budget calculation failed: {str(e)}',
            'activities_with_costs': []
        })


@tool("Enrich Venues with Addresses")
def enrich_venues_with_addresses(venues_json: str, location: str) -> str:
    """
    Enrich a list of venues with their addresses and contact information.
    
    Args:
        venues_json: JSON string of venues list. Each venue should have:
                    - name: Venue name
                    - type: Venue type
                    Other fields will be preserved
        location: City/area for all venues
    
    Returns:
        JSON string with enriched venues including addresses
    
    Example:
        venues = [{"name": "Poor Calvin's", "type": "restaurant", "rating": 4.7}]
        enrich_venues_with_addresses(json.dumps(venues), "Atlanta")
    """
    try:
        import time
        import random
        
        venues = json.loads(venues_json)
        enriched = []
        
        for i, venue in enumerate(venues):
            venue_name = venue.get('name', '')
            venue_type = venue.get('type', 'restaurant')
            
            # Add delay between requests (except for first one)
            if i > 0:
                time.sleep(random.uniform(1.0, 2.0))
            
            # Get address details
            details = get_venue_details(venue_name, location, venue_type)
            
            # Merge with existing venue data
            enriched_venue = {**venue}  # Copy all existing fields
            
            # Only add address if we found one
            if details.get('address'):
                enriched_venue['address'] = details['address']
                if details.get('phone'):
                    enriched_venue['phone'] = details['phone']
                if details.get('website'):
                    enriched_venue['website'] = details['website']
            # If no address found, don't add the field at all
            
            enriched.append(enriched_venue)
        
        return json.dumps(enriched, indent=2)
    except Exception as e:
        return json.dumps({
            'error': f'Address enrichment failed: {str(e)}',
            'venues': venues_json
        })
