#!/usr/bin/env python3
"""
Montenegro Accommodation Search Example
Based on the montenegro_accommodation_strategy.md document
"""

from datetime import datetime, timedelta
from advanced_accommodation_agent import AdvancedAccommodationAgent, SearchCriteria

def search_montenegro_accommodations():
    """Search for accommodations in Montenegro based on the strategy document"""
    
    print("🇲🇪 Montenegro Accommodation Search")
    print("=" * 50)
    print("Based on the accommodation strategy document")
    print()
    
    # Define search criteria based on the strategy
    criteria = SearchCriteria(
        location="Bar, Montenegro",
        check_in="2024-09-01",  # Shoulder season for better prices
        check_out="2024-09-15",  # 14 nights
        guests=2,
        max_price_per_night=40.0,  # $36/night target from strategy
        amenities=["kitchen", "wifi", "air_conditioning", "parking"]
    )
    
    print("🔍 Search Criteria:")
    print(f"   Location: {criteria.location}")
    print(f"   Dates: {criteria.check_in} to {criteria.check_out}")
    print(f"   Guests: {criteria.guests}")
    print(f"   Max Price: ${criteria.max_price_per_night}/night")
    print(f"   Amenities: {', '.join(criteria.amenities)}")
    print()
    
    # Create advanced agent
    agent = AdvancedAccommodationAgent(headless=False)
    
    try:
        # Search for accommodations
        print("🔍 Searching Booking.com and Airbnb...")
        results = agent.search_accommodations(criteria)
        
        # Analyze results
        print("📊 Analyzing search results...")
        analysis = agent.analyze_search_results(results, criteria)
        
        # Save detailed analysis
        filename = f"montenegro_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        agent.save_detailed_analysis(analysis, filename)
        
        # Display results
        print(f"\n✅ Search completed!")
        print(f"   Total properties found: {analysis.total_properties_found}")
        print(f"   Average price: ${analysis.average_price_per_night:.2f}/night")
        print(f"   Price range: ${analysis.price_range[0]:.2f} - ${analysis.price_range[1]:.2f}")
        
        # Show top recommendations
        if analysis.best_value_properties:
            print(f"\n🏆 Top 5 Recommendations:")
            for i, prop in enumerate(analysis.best_value_properties[:5], 1):
                print(f"   {i}. {prop.title}")
                print(f"      Price: ${prop.price_per_night}/night")
                print(f"      Location: {prop.location}")
                if prop.rating:
                    print(f"      Rating: {prop.rating}/5")
                print(f"      Platform: {prop.platform}")
                print()
        
        # Show budget options
        if analysis.budget_options:
            print(f"💰 Budget Options (≤${criteria.max_price_per_night * 0.8:.0f}/night):")
            for i, prop in enumerate(analysis.budget_options[:3], 1):
                print(f"   {i}. {prop.title} - ${prop.price_per_night}/night")
            print()
        
        # Provide booking assistance
        agent.automated_booking_assistant(analysis, criteria)
        
        # Strategy insights
        print("\n📋 Strategy Insights:")
        print("   • Search completed for Bar area with 10km radius")
        print("   • Focused on entire homes & apartments only")
        print("   • Prioritized properties with kitchen, WiFi, and AC")
        print("   • September dates chosen for shoulder season pricing")
        print("   • Results saved for comparison and analysis")
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
    
    finally:
        agent.close()

def search_alternative_locations():
    """Search alternative locations mentioned in the strategy"""
    
    print("\n🗺️ Alternative Location Search")
    print("=" * 40)
    
    # Alternative locations from the strategy
    alternative_locations = [
        "Sutomore, Montenegro",
        "Petrovac, Montenegro", 
        "Ulcinj, Montenegro",
        "Podgorica, Montenegro"
    ]
    
    criteria = SearchCriteria(
        location="",  # Will be set for each location
        check_in="2024-09-01",
        check_out="2024-09-15",
        guests=2,
        max_price_per_night=40.0,
        amenities=["kitchen", "wifi", "air_conditioning"]
    )
    
    agent = AdvancedAccommodationAgent(headless=False)
    
    try:
        for location in alternative_locations:
            print(f"\n🔍 Searching {location}...")
            criteria.location = location
            
            results = agent.search_accommodations(criteria)
            
            # Quick summary
            total_properties = sum(len(listings) for listings in results.values())
            if total_properties > 0:
                prices = []
                for listings in results.values():
                    prices.extend([l.price_per_night for l in listings if l.price_per_night > 0])
                
                avg_price = sum(prices) / len(prices) if prices else 0
                print(f"   Found {total_properties} properties")
                print(f"   Average price: ${avg_price:.2f}/night")
            else:
                print("   No properties found")
            
            # Be respectful with delays
            import time
            time.sleep(3)
    
    except Exception as e:
        print(f"❌ Error searching alternatives: {e}")
    
    finally:
        agent.close()

def main():
    """Main function"""
    print("🇲🇪 Montenegro Accommodation Search Agent")
    print("Based on the accommodation strategy document")
    print()
    
    # Main search
    search_montenegro_accommodations()
    
    # Ask if user wants to search alternatives
    print("\n" + "="*50)
    response = input("Search alternative locations (Sutomore, Petrovac, etc.)? (y/n): ").lower()
    
    if response in ['y', 'yes']:
        search_alternative_locations()
    
    print("\n🎉 Search completed! Check the data/ directory for detailed results.")

if __name__ == "__main__":
    main()
