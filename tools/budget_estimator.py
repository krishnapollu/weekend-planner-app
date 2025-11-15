"""
Budget analysis tool for estimating activity costs
"""

from typing import Dict, List
import re


# Currency symbols by country/location
LOCATION_CURRENCY = {
    # US Cities
    'new york': ('$', 'USD'),
    'los angeles': ('$', 'USD'),
    'chicago': ('$', 'USD'),
    'houston': ('$', 'USD'),
    'phoenix': ('$', 'USD'),
    'philadelphia': ('$', 'USD'),
    'san antonio': ('$', 'USD'),
    'san diego': ('$', 'USD'),
    'dallas': ('$', 'USD'),
    'san jose': ('$', 'USD'),
    'austin': ('$', 'USD'),
    'seattle': ('$', 'USD'),
    'atlanta': ('$', 'USD'),
    'miami': ('$', 'USD'),
    'boston': ('$', 'USD'),
    'portland': ('$', 'USD'),
    'denver': ('$', 'USD'),
    'san francisco': ('$', 'USD'),
    'las vegas': ('$', 'USD'),
    
    # Other countries
    'london': ('£', 'GBP'),
    'paris': ('€', 'EUR'),
    'berlin': ('€', 'EUR'),
    'rome': ('€', 'EUR'),
    'madrid': ('€', 'EUR'),
    'amsterdam': ('€', 'EUR'),
    'tokyo': ('¥', 'JPY'),
    'osaka': ('¥', 'JPY'),
    'sydney': ('A$', 'AUD'),
    'melbourne': ('A$', 'AUD'),
    'toronto': ('C$', 'CAD'),
    'vancouver': ('C$', 'CAD'),
    'mumbai': ('₹', 'INR'),
    'delhi': ('₹', 'INR'),
    'bangalore': ('₹', 'INR'),
    'dubai': ('AED', 'AED'),
    'singapore': ('S$', 'SGD'),
}


def get_currency_for_location(location: str) -> tuple:
    """
    Get currency symbol and code for a location
    
    Args:
        location: City name
        
    Returns:
        Tuple of (symbol, code) e.g., ('$', 'USD')
    """
    location_lower = location.lower().strip()
    return LOCATION_CURRENCY.get(location_lower, ('$', 'USD'))  # Default to USD


# Average cost estimates by activity type
COST_ESTIMATES = {
    'restaurant': {
        'budget': (10, 20),      # per person
        'moderate': (20, 40),
        'upscale': (40, 80),
        'fine_dining': (80, 150)
    },
    'movie': {
        'matinee': (8, 12),
        'evening': (12, 18),
        'premium': (18, 25)      # IMAX, 3D, etc.
    },
    'outdoor': {
        'free': (0, 0),          # Parks, trails
        'admission': (5, 15),    # Botanical gardens, etc.
        'activity': (20, 50)     # Kayaking, bike rental, etc.
    },
    'event': {
        'free': (0, 0),          # Street festivals
        'ticketed': (15, 50),    # Local events
        'concert': (30, 100),    # Music venues
        'premium': (100, 300)    # Major concerts, shows
    }
}


def estimate_restaurant_cost(name: str, details: str, rating: float) -> Dict[str, any]:
    """
    Estimate restaurant cost based on description and rating
    
    Args:
        name: Restaurant name
        details: Description text
        rating: Star rating
        
    Returns:
        Dict with estimated cost range and category
    """
    details_lower = details.lower()
    name_lower = name.lower()
    
    # Determine category based on keywords
    if any(word in details_lower for word in ['upscale', 'fine dining', 'michelin', 'tasting menu', 'prix fixe']):
        category = 'fine_dining'
    elif any(word in details_lower for word in ['upscale', 'elevated', 'contemporary', 'refined']):
        category = 'upscale'
    elif any(word in details_lower for word in ['casual', 'food hall', 'quick', 'counter']):
        category = 'budget'
    elif rating >= 4.5:
        category = 'upscale'
    elif rating >= 4.0:
        category = 'moderate'
    else:
        category = 'budget'
    
    cost_range = COST_ESTIMATES['restaurant'].get(category, COST_ESTIMATES['restaurant']['moderate'])
    
    return {
        'category': category,
        'min_cost': cost_range[0],
        'max_cost': cost_range[1],
        'avg_cost': (cost_range[0] + cost_range[1]) / 2
    }


def estimate_activity_cost(activity_type: str, name: str, details: str) -> Dict[str, any]:
    """
    Estimate cost for any activity type
    
    Args:
        activity_type: Type (restaurant, movie, outdoor, event)
        name: Activity name
        details: Description
        
    Returns:
        Dict with cost estimate
    """
    details_lower = details.lower()
    name_lower = name.lower()
    
    if activity_type == 'movie':
        if 'imax' in details_lower or '3d' in details_lower or 'premium' in details_lower:
            category = 'premium'
        elif 'matinee' in details_lower or 'afternoon' in details_lower:
            category = 'matinee'
        else:
            category = 'evening'
        cost_range = COST_ESTIMATES['movie'][category]
        
    elif activity_type == 'outdoor':
        if any(word in details_lower for word in ['free', 'trail', 'walk', 'hike', 'park']):
            category = 'free'
        elif any(word in details_lower for word in ['admission', 'ticket', 'entry fee', 'botanical', 'garden']):
            category = 'admission'
        else:
            category = 'activity'
        cost_range = COST_ESTIMATES['outdoor'][category]
        
    elif activity_type == 'event':
        if any(word in details_lower for word in ['free', 'no admission', 'no charge']):
            category = 'free'
        elif any(word in details_lower for word in ['concert', 'band', 'festival with tickets']):
            category = 'concert'
        elif 'ticket' in details_lower or 'admission' in details_lower:
            category = 'ticketed'
        else:
            category = 'free'
        cost_range = COST_ESTIMATES['event'][category]
        
    else:
        # Default moderate cost
        cost_range = (15, 35)
        category = 'moderate'
    
    return {
        'category': category,
        'min_cost': cost_range[0],
        'max_cost': cost_range[1],
        'avg_cost': (cost_range[0] + cost_range[1]) / 2
    }


def analyze_itinerary_budget(activities: List[Dict], group_size: int = 1, location: str = None) -> Dict[str, any]:
    """
    Analyze total budget for an itinerary
    
    Args:
        activities: List of activity dicts with name, type, details, rating
        group_size: Number of people
        location: City/location for currency detection
        
    Returns:
        Budget analysis with breakdown
    """
    # Get currency for location
    currency_symbol, currency_code = get_currency_for_location(location) if location else ('$', 'USD')
    
    total_min = 0
    total_max = 0
    breakdown = []
    
    for activity in activities:
        activity_type = activity.get('type', 'restaurant')
        name = activity.get('name', 'Unknown')
        details = activity.get('details', '')
        rating = activity.get('rating', 4.0)
        
        if activity_type == 'restaurant':
            cost_info = estimate_restaurant_cost(name, details, rating)
        else:
            cost_info = estimate_activity_cost(activity_type, name, details)
        
        # Multiply by group size for applicable activities
        if activity_type in ['restaurant', 'movie', 'event'] and 'free' not in cost_info['category']:
            per_person_min = cost_info['min_cost']
            per_person_max = cost_info['max_cost']
            total_min_cost = per_person_min * group_size
            total_max_cost = per_person_max * group_size
        else:
            total_min_cost = cost_info['min_cost']
            total_max_cost = cost_info['max_cost']
        
        total_min += total_min_cost
        total_max += total_max_cost
        
        breakdown.append({
            'name': name,
            'type': activity_type,
            'category': cost_info['category'],
            'min_per_person': cost_info['min_cost'],
            'max_per_person': cost_info['max_cost'],
            'total_min': total_min_cost,
            'total_max': total_max_cost,
            'currency_symbol': currency_symbol,
            'currency_code': currency_code
        })
    
    return {
        'group_size': group_size,
        'location': location,
        'currency_symbol': currency_symbol,
        'currency_code': currency_code,
        'total_min': total_min,
        'total_max': total_max,
        'total_avg': (total_min + total_max) / 2,
        'per_person_min': total_min / group_size if group_size > 0 else total_min,
        'per_person_max': total_max / group_size if group_size > 0 else total_max,
        'per_person_avg': ((total_min + total_max) / 2) / group_size if group_size > 0 else (total_min + total_max) / 2,
        'breakdown': breakdown
    }


def format_budget_summary(budget_analysis: Dict) -> str:
    """
    Format budget analysis into friendly text
    
    Args:
        budget_analysis: Output from analyze_itinerary_budget
        
    Returns:
        Formatted string
    """
    group_size = budget_analysis['group_size']
    total_min = budget_analysis['total_min']
    total_max = budget_analysis['total_max']
    breakdown = budget_analysis['breakdown']
    
    if group_size > 1:
        summary = f"💰 **Budget Estimate** (for {group_size} people):\n"
        summary += f"Total: ${total_min:.0f} - ${total_max:.0f}\n"
        summary += f"Per Person: ${budget_analysis['per_person_min']:.0f} - ${budget_analysis['per_person_max']:.0f}\n\n"
    else:
        summary = f"💰 **Budget Estimate**:\n"
        summary += f"Total: ${total_min:.0f} - ${total_max:.0f}\n\n"
    
    summary += "**Breakdown:**\n"
    for item in breakdown:
        if item['total_min'] == 0:
            summary += f"- {item['name']}: FREE\n"
        elif group_size > 1:
            summary += f"- {item['name']}: ${item['min_per_person']:.0f}-${item['max_per_person']:.0f}/person (${item['total_min']:.0f}-${item['total_max']:.0f} total)\n"
        else:
            summary += f"- {item['name']}: ${item['total_min']:.0f}-${item['total_max']:.0f}\n"
    
    return summary


# Test function
if __name__ == "__main__":
    test_activities = [
        {
            'name': "Poor Calvin's",
            'type': 'restaurant',
            'rating': 4.7,
            'details': 'Upscale restaurant blending Southern and Asian flavors'
        },
        {
            'name': 'The Plaza Theatre',
            'type': 'movie',
            'rating': 4.6,
            'details': 'Independent movie theatre showing new releases'
        },
        {
            'name': 'Atlanta Botanical Garden',
            'type': 'outdoor',
            'rating': 4.7,
            'details': 'Beautiful botanical garden with admission fee'
        }
    ]
    
    analysis = analyze_itinerary_budget(test_activities, group_size=2)
    print(format_budget_summary(analysis))
