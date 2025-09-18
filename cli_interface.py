#!/usr/bin/env python3
"""
Command Line Interface for Accommodation Search Agent
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Import our agents
from accommodation_agent import AccommodationSearchAgent, SearchCriteria
from advanced_accommodation_agent import AdvancedAccommodationAgent

def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def get_date_input(prompt: str, default_days: int = None) -> str:
    """Get date input with optional default"""
    if default_days:
        default_date = (datetime.now() + timedelta(days=default_days)).strftime("%Y-%m-%d")
        date_str = get_user_input(prompt, default_date)
    else:
        date_str = get_user_input(prompt)
    
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print("❌ Invalid date format. Please use YYYY-MM-DD format.")
        return get_date_input(prompt, default_days)

def get_number_input(prompt: str, min_val: int = 1, max_val: int = 20, default: int = None) -> int:
    """Get numeric input with validation"""
    while True:
        try:
            if default:
                user_input = get_user_input(prompt, str(default))
            else:
                user_input = get_user_input(prompt)
            
            value = int(user_input)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"❌ Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print("❌ Please enter a valid number")

def get_float_input(prompt: str, min_val: float = 0, default: float = None) -> float:
    """Get float input with validation"""
    while True:
        try:
            if default:
                user_input = get_user_input(prompt, str(default))
            else:
                user_input = get_user_input(prompt)
            
            value = float(user_input)
            if value >= min_val:
                return value
            else:
                print(f"❌ Please enter a number greater than or equal to {min_val}")
        except ValueError:
            print("❌ Please enter a valid number")

def select_amenities() -> list:
    """Let user select amenities"""
    available_amenities = [
        "kitchen", "wifi", "air_conditioning", "parking", "washer", 
        "dryer", "tv", "balcony", "garden", "pool", "beach_access",
        "restaurant", "gym", "spa", "pet_friendly"
    ]
    
    print("\n🏠 Available amenities:")
    for i, amenity in enumerate(available_amenities, 1):
        print(f"   {i:2d}. {amenity.replace('_', ' ').title()}")
    
    print("\nSelect amenities (comma-separated numbers, or press Enter for default):")
    user_input = input("Default: kitchen, wifi, air_conditioning: ").strip()
    
    if not user_input:
        return ["kitchen", "wifi", "air_conditioning"]
    
    try:
        selected_indices = [int(x.strip()) - 1 for x in user_input.split(",")]
        selected_amenities = [available_amenities[i] for i in selected_indices if 0 <= i < len(available_amenities)]
        return selected_amenities if selected_amenities else ["kitchen", "wifi", "air_conditioning"]
    except (ValueError, IndexError):
        print("❌ Invalid selection. Using default amenities.")
        return ["kitchen", "wifi", "air_conditioning"]

def interactive_search():
    """Interactive search mode"""
    print("🏨 ACCOMMODATION SEARCH AGENT")
    print("=" * 50)
    
    # Get search criteria
    print("\n📍 Location:")
    location = get_user_input("Enter destination", "Bar, Montenegro")
    
    print("\n📅 Dates:")
    check_in = get_date_input("Check-in date", 30)  # Default 30 days from now
    check_out = get_date_input("Check-out date", 44)  # Default 14 days after check-in
    
    print("\n👥 Guests:")
    guests = get_number_input("Number of guests", 1, 10, 2)
    
    print("\n💰 Budget:")
    max_price = get_float_input("Maximum price per night (USD)", 0, 40)
    
    print("\n🏠 Property Type:")
    property_types = ["entire_place", "private_room", "shared_room"]
    for i, ptype in enumerate(property_types, 1):
        print(f"   {i}. {ptype.replace('_', ' ').title()}")
    property_type = get_user_input("Select property type", "1")
    
    try:
        property_type = property_types[int(property_type) - 1]
    except (ValueError, IndexError):
        property_type = "entire_place"
    
    # Get amenities
    amenities = select_amenities()
    
    # Create search criteria
    criteria = SearchCriteria(
        location=location,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        max_price_per_night=max_price,
        property_type=property_type,
        amenities=amenities
    )
    
    # Confirm search
    print("\n🔍 Search Summary:")
    print(f"   Location: {criteria.location}")
    print(f"   Dates: {criteria.check_in} to {criteria.check_out}")
    print(f"   Guests: {criteria.guests}")
    print(f"   Max Price: ${criteria.max_price_per_night}/night")
    print(f"   Property Type: {criteria.property_type}")
    print(f"   Amenities: {', '.join(criteria.amenities)}")
    
    confirm = get_user_input("\nStart search? (y/n)", "y").lower()
    if confirm not in ['y', 'yes']:
        print("❌ Search cancelled.")
        return
    
    # Choose agent type
    print("\n🤖 Agent Type:")
    print("   1. Basic Agent (faster, basic results)")
    print("   2. Advanced Agent (slower, detailed analysis)")
    agent_type = get_user_input("Select agent type", "2")
    
    # Run search
    try:
        if agent_type == "1":
            agent = AccommodationSearchAgent(headless=False)
            print("\n🔍 Searching for accommodations...")
            results = agent.search_accommodations(criteria)
            agent.save_results(results)
            
            # Display summary
            print(f"\n✅ Search completed!")
            print(f"   Booking.com: {len(results['booking_com'])} properties")
            print(f"   Airbnb: {len(results['airbnb'])} properties")
            
        else:
            agent = AdvancedAccommodationAgent(headless=False)
            print("\n🔍 Searching for accommodations...")
            results = agent.search_accommodations(criteria)
            
            print("\n📊 Analyzing results...")
            analysis = agent.analyze_search_results(results, criteria)
            
            # Save results
            agent.save_detailed_analysis(analysis, criteria)
            
            # Display results
            print(f"\n✅ Analysis completed!")
            print(f"   Total properties: {analysis.total_properties_found}")
            print(f"   Average price: ${analysis.average_price_per_night:.2f}/night")
            print(f"   Price range: ${analysis.price_range[0]:.2f} - ${analysis.price_range[1]:.2f}")
            
            # Show top recommendations
            if analysis.best_value_properties:
                print(f"\n🏆 Top Recommendations:")
                for i, prop in enumerate(analysis.best_value_properties[:3], 1):
                    print(f"   {i}. {prop.title}")
                    print(f"      Price: ${prop.price_per_night}/night | Rating: {prop.rating}/5" if prop.rating else f"      Price: ${prop.price_per_night}/night")
                    print(f"      Location: {prop.location}")
                    print()
            
            # Provide booking assistance
            agent.automated_booking_assistant(analysis, criteria)
        
        agent.close()
        
    except KeyboardInterrupt:
        print("\n❌ Search interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during search: {e}")

def quick_search():
    """Quick search with default settings"""
    print("⚡ QUICK SEARCH MODE")
    print("=" * 30)
    
    # Use default criteria for Montenegro
    criteria = SearchCriteria(
        location="Bar, Montenegro",
        check_in=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        check_out=(datetime.now() + timedelta(days=44)).strftime("%Y-%m-%d"),
        guests=2,
        max_price_per_night=40.0,
        amenities=["kitchen", "wifi", "air_conditioning"]
    )
    
    print(f"Searching for: {criteria.location}")
    print(f"Dates: {criteria.check_in} to {criteria.check_out}")
    print(f"Budget: ${criteria.max_price_per_night}/night")
    
    try:
        agent = AdvancedAccommodationAgent(headless=False)
        results = agent.search_accommodations(criteria)
        analysis = agent.analyze_search_results(results, criteria)
        agent.save_detailed_analysis(analysis)
        agent.automated_booking_assistant(analysis, criteria)
        agent.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Accommodation Search Agent")
    parser.add_argument("--quick", action="store_true", help="Run quick search with default settings")
    parser.add_argument("--interactive", action="store_true", help="Run interactive search (default)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_search()
    else:
        interactive_search()

if __name__ == "__main__":
    main()
