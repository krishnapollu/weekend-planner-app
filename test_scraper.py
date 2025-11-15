from tools.venue_scraper import get_venue_details

print("Testing address scraper...")
print("-" * 50)

venues = [
    ("The Iberian Pig", "Atlanta", "restaurant"),
    ("Mary Mac's Tea Room", "Atlanta", "restaurant"),
    ("Piedmont Park", "Atlanta", "outdoor")
]

for venue_name, location, venue_type in venues:
    print(f"\nScraping: {venue_name}")
    result = get_venue_details(venue_name, location, venue_type)
    if result and result.get('address'):
        print(f"✅ Address: {result['address']}")
    else:
        print("❌ No address found")
