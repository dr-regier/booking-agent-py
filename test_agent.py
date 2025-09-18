#!/usr/bin/env python3
"""
Test script for Accommodation Search Agent
"""

import sys
import time
from accommodation_agent import AccommodationSearchAgent, SearchCriteria

def test_basic_functionality():
    """Test basic agent functionality"""
    print("🧪 Testing Accommodation Search Agent")
    print("=" * 40)
    
    # Create a simple search criteria
    criteria = SearchCriteria(
        location="Bar, Montenegro",
        check_in="2024-09-01",
        check_out="2024-09-03",  # Short stay for testing
        guests=2,
        max_price_per_night=50.0,
        amenities=["kitchen", "wifi"]
    )
    
    print(f"📍 Location: {criteria.location}")
    print(f"📅 Dates: {criteria.check_in} to {criteria.check_out}")
    print(f"💰 Max Price: ${criteria.max_price_per_night}/night")
    print()
    
    # Create agent
    print("🔧 Initializing agent...")
    agent = AccommodationSearchAgent(headless=True)  # Headless for testing
    
    try:
        # Test Booking.com search
        print("🔍 Testing Booking.com search...")
        booking_results = agent.search_booking_com(criteria)
        print(f"   Found {len(booking_results)} properties on Booking.com")
        
        # Test Airbnb search
        print("🔍 Testing Airbnb search...")
        airbnb_results = agent.search_airbnb(criteria)
        print(f"   Found {len(airbnb_results)} properties on Airbnb")
        
        # Show sample results
        if booking_results:
            print(f"\n📋 Sample Booking.com result:")
            sample = booking_results[0]
            print(f"   Title: {sample.title}")
            print(f"   Price: ${sample.price_per_night}/night")
            print(f"   Location: {sample.location}")
        
        if airbnb_results:
            print(f"\n📋 Sample Airbnb result:")
            sample = airbnb_results[0]
            print(f"   Title: {sample.title}")
            print(f"   Price: ${sample.price_per_night}/night")
            print(f"   Location: {sample.location}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        agent.close()
    
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
