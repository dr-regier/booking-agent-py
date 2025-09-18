import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import logging
import re
from pathlib import Path

# Import the base agent
from accommodation_agent import AccommodationSearchAgent, SearchCriteria, PropertyListing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DetailedPropertyListing(PropertyListing):
    """Extended property listing with detailed information"""
    # Basic info
    description: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    max_guests: Optional[int] = None
    square_meters: Optional[float] = None
    
    # Pricing details
    cleaning_fee: Optional[float] = None
    service_fee: Optional[float] = None
    taxes: Optional[float] = None
    security_deposit: Optional[float] = None
    weekly_discount: Optional[float] = None
    monthly_discount: Optional[float] = None
    
    # Availability
    availability_calendar: Optional[Dict] = None
    minimum_stay: Optional[int] = None
    maximum_stay: Optional[int] = None
    
    # Host information
    host_rating: Optional[float] = None
    host_response_time: Optional[str] = None
    host_response_rate: Optional[float] = None
    host_verification: Optional[List[str]] = None
    
    # Property features
    property_features: Optional[List[str]] = None
    house_rules: Optional[List[str]] = None
    cancellation_policy_details: Optional[str] = None
    
    # Analysis
    value_score: Optional[float] = None
    location_score: Optional[float] = None
    overall_score: Optional[float] = None

@dataclass
class SearchAnalysis:
    """Analysis results for accommodation search"""
    total_properties_found: int
    average_price_per_night: float
    price_range: Tuple[float, float]
    best_value_properties: List[DetailedPropertyListing]
    budget_options: List[DetailedPropertyListing]
    premium_options: List[DetailedPropertyListing]
    recommendations: List[str]
    market_insights: Dict[str, Any]

class AdvancedAccommodationAgent(AccommodationSearchAgent):
    """Advanced accommodation search agent with detailed analysis capabilities"""
    
    def __init__(self, headless: bool = False, data_dir: str = "data"):
        super().__init__(headless)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.search_history = []
        
    def get_detailed_property_info(self, listing: PropertyListing) -> DetailedPropertyListing:
        """Get detailed information about a specific property"""
        logger.info(f"Getting detailed info for: {listing.title}")
        
        try:
            # Navigate to property page
            self.driver.get(listing.url)
            time.sleep(3)
            
            # Accept cookies if present
            self.accept_cookies()
            
            # Extract detailed information
            detailed_info = self.extract_detailed_property_info()
            
            # Convert to DetailedPropertyListing
            detailed_listing = DetailedPropertyListing(
                platform=listing.platform,
                title=listing.title,
                price_per_night=listing.price_per_night,
                total_price=listing.total_price,
                location=listing.location,
                rating=listing.rating,
                review_count=listing.review_count,
                amenities=listing.amenities,
                url=listing.url,
                property_type=listing.property_type,
                host_name=listing.host_name,
                instant_book=listing.instant_book,
                cancellation_policy=listing.cancellation_policy,
                **detailed_info
            )
            
            return detailed_listing
            
        except Exception as e:
            logger.error(f"Error getting detailed info for {listing.title}: {e}")
            return DetailedPropertyListing(
                platform=listing.platform,
                title=listing.title,
                price_per_night=listing.price_per_night,
                total_price=listing.total_price,
                location=listing.location,
                rating=listing.rating,
                review_count=listing.review_count,
                amenities=listing.amenities,
                url=listing.url,
                property_type=listing.property_type,
                host_name=listing.host_name,
                instant_book=listing.instant_book,
                cancellation_policy=listing.cancellation_policy
            )
    
    def extract_detailed_property_info(self) -> Dict[str, Any]:
        """Extract detailed property information from the current page"""
        info = {}
        
        try:
            # Description
            try:
                description_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='description']")
                info['description'] = description_element.text
            except:
                info['description'] = None
            
            # Property details (bedrooms, bathrooms, etc.)
            try:
                details_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='property-details'] span")
                for element in details_elements:
                    text = element.text.lower()
                    if 'bedroom' in text:
                        info['bedrooms'] = int(re.search(r'\d+', text).group())
                    elif 'bathroom' in text:
                        info['bathrooms'] = int(re.search(r'\d+', text).group())
                    elif 'guest' in text:
                        info['max_guests'] = int(re.search(r'\d+', text).group())
            except:
                pass
            
            # Pricing details
            try:
                price_breakdown = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='price-breakdown'] div")
                for element in price_breakdown:
                    text = element.text.lower()
                    if 'cleaning' in text:
                        info['cleaning_fee'] = self.extract_price(text)
                    elif 'service' in text:
                        info['service_fee'] = self.extract_price(text)
                    elif 'tax' in text:
                        info['taxes'] = self.extract_price(text)
                    elif 'deposit' in text:
                        info['security_deposit'] = self.extract_price(text)
            except:
                pass
            
            # Host information
            try:
                host_section = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='host-profile']")
                host_name = host_section.find_element(By.CSS_SELECTOR, "[data-testid='host-name']").text
                info['host_name'] = host_name
                
                # Host rating
                try:
                    host_rating = host_section.find_element(By.CSS_SELECTOR, "[data-testid='host-rating']").text
                    info['host_rating'] = float(host_rating.split()[0])
                except:
                    pass
                
                # Response time
                try:
                    response_time = host_section.find_element(By.CSS_SELECTOR, "[data-testid='response-time']").text
                    info['host_response_time'] = response_time
                except:
                    pass
                
            except:
                pass
            
            # Property features
            try:
                features_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='amenities'] li")
                info['property_features'] = [elem.text for elem in features_elements]
            except:
                info['property_features'] = []
            
            # House rules
            try:
                rules_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='house-rules'] li")
                info['house_rules'] = [elem.text for elem in rules_elements]
            except:
                info['house_rules'] = []
            
        except Exception as e:
            logger.error(f"Error extracting detailed property info: {e}")
        
        return info
    
    def analyze_search_results(self, results: Dict[str, List[PropertyListing]], 
                             criteria: SearchCriteria) -> SearchAnalysis:
        """Analyze search results and provide insights"""
        logger.info("Analyzing search results...")
        
        # Get detailed information for top properties
        detailed_listings = []
        all_listings = []
        
        for platform, listings in results.items():
            all_listings.extend(listings)
            
            # Get detailed info for top 5 properties from each platform
            top_listings = sorted(listings, key=lambda x: x.price_per_night)[:5]
            for listing in top_listings:
                detailed_listing = self.get_detailed_property_info(listing)
                detailed_listings.append(detailed_listing)
                time.sleep(2)  # Be respectful to the websites
        
        # Calculate scores for detailed listings
        for listing in detailed_listings:
            listing.value_score = self.calculate_value_score(listing, criteria)
            listing.location_score = self.calculate_location_score(listing, criteria)
            listing.overall_score = (listing.value_score + listing.location_score) / 2
        
        # Sort by overall score
        detailed_listings.sort(key=lambda x: x.overall_score or 0, reverse=True)
        
        # Calculate statistics
        prices = [l.price_per_night for l in all_listings if l.price_per_night > 0]
        avg_price = np.mean(prices) if prices else 0
        price_range = (min(prices), max(prices)) if prices else (0, 0)
        
        # Categorize properties
        budget_threshold = criteria.max_price_per_night * 0.8
        premium_threshold = criteria.max_price_per_night * 1.2
        
        budget_options = [l for l in detailed_listings if l.price_per_night <= budget_threshold]
        premium_options = [l for l in detailed_listings if l.price_per_night >= premium_threshold]
        best_value = detailed_listings[:5]  # Top 5 by overall score
        
        # Generate recommendations
        recommendations = self.generate_recommendations(detailed_listings, criteria)
        
        # Market insights
        market_insights = self.generate_market_insights(detailed_listings, criteria)
        
        return SearchAnalysis(
            total_properties_found=len(all_listings),
            average_price_per_night=avg_price,
            price_range=price_range,
            best_value_properties=best_value,
            budget_options=budget_options,
            premium_options=premium_options,
            recommendations=recommendations,
            market_insights=market_insights
        )
    
    def calculate_value_score(self, listing: DetailedPropertyListing, criteria: SearchCriteria) -> float:
        """Calculate value score based on price and amenities"""
        score = 0.0
        
        # Price score (lower is better)
        if listing.price_per_night > 0:
            price_score = max(0, 100 - (listing.price_per_night / criteria.max_price_per_night) * 100)
            score += price_score * 0.4
        
        # Amenities score
        if listing.amenities:
            amenity_score = len([a for a in criteria.amenities if a in listing.amenities]) / len(criteria.amenities) * 100
            score += amenity_score * 0.3
        
        # Rating score
        if listing.rating:
            rating_score = (listing.rating / 5.0) * 100
            score += rating_score * 0.2
        
        # Host score
        if listing.host_rating:
            host_score = (listing.host_rating / 5.0) * 100
            score += host_score * 0.1
        
        return score
    
    def calculate_location_score(self, listing: DetailedPropertyListing, criteria: SearchCriteria) -> float:
        """Calculate location score based on proximity and area quality"""
        score = 0.0
        
        # Distance score (assuming closer to Bar is better)
        if "bar" in listing.location.lower():
            score += 80
        elif "sutomore" in listing.location.lower() or "petrovac" in listing.location.lower():
            score += 60
        else:
            score += 40
        
        # Additional location factors could be added here
        # (e.g., proximity to beach, restaurants, transportation)
        
        return score
    
    def generate_recommendations(self, listings: List[DetailedPropertyListing], 
                               criteria: SearchCriteria) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if not listings:
            recommendations.append("No properties found matching your criteria. Consider expanding your search area or adjusting your budget.")
            return recommendations
        
        # Price analysis
        avg_price = np.mean([l.price_per_night for l in listings if l.price_per_night > 0])
        if avg_price > criteria.max_price_per_night:
            recommendations.append(f"Average price (${avg_price:.0f}) is above your budget. Consider traveling in shoulder season or expanding your search area.")
        
        # Best value recommendations
        best_value = max(listings, key=lambda x: x.value_score or 0)
        recommendations.append(f"Best value option: {best_value.title} at ${best_value.price_per_night}/night")
        
        # Location recommendations
        bar_properties = [l for l in listings if "bar" in l.location.lower()]
        if bar_properties:
            recommendations.append(f"Found {len(bar_properties)} properties in Bar area - ideal for your location preference")
        
        # Booking recommendations
        instant_book_properties = [l for l in listings if l.instant_book]
        if instant_book_properties:
            recommendations.append(f"{len(instant_book_properties)} properties offer instant booking for immediate confirmation")
        
        return recommendations
    
    def generate_market_insights(self, listings: List[DetailedPropertyListing], 
                               criteria: SearchCriteria) -> Dict[str, Any]:
        """Generate market insights and trends"""
        insights = {}
        
        if not listings:
            return insights
        
        # Price distribution
        prices = [l.price_per_night for l in listings if l.price_per_night > 0]
        insights['price_distribution'] = {
            'min': min(prices),
            'max': max(prices),
            'median': np.median(prices),
            'std': np.std(prices)
        }
        
        # Platform comparison
        platform_stats = {}
        for listing in listings:
            platform = listing.platform
            if platform not in platform_stats:
                platform_stats[platform] = {'count': 0, 'avg_price': 0, 'prices': []}
            
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['prices'].append(listing.price_per_night)
        
        for platform, stats in platform_stats.items():
            stats['avg_price'] = np.mean(stats['prices'])
        
        insights['platform_comparison'] = platform_stats
        
        # Amenity analysis
        amenity_counts = {}
        for listing in listings:
            for amenity in listing.amenities:
                amenity_counts[amenity] = amenity_counts.get(amenity, 0) + 1
        
        insights['popular_amenities'] = sorted(amenity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return insights
    
    def save_detailed_analysis(self, analysis: SearchAnalysis, criteria: SearchCriteria, filename: str = None):
        """Save detailed analysis results as markdown and HTML reports"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accommodation_report_{timestamp}"
        
        # Save detailed listings to JSON
        detailed_listings = []
        for listing in analysis.best_value_properties + analysis.budget_options + analysis.premium_options:
            detailed_listings.append(asdict(listing))
        
        # Save to JSON
        output_data = {
            'analysis_summary': {
                'total_properties': analysis.total_properties_found,
                'average_price': analysis.average_price_per_night,
                'price_range': analysis.price_range,
                'recommendations': analysis.recommendations,
                'market_insights': analysis.market_insights
            },
            'detailed_listings': detailed_listings
        }
        
        with open(self.data_dir / f"{filename}.json", 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        # Generate markdown and HTML reports
        from report_generator import ReportGenerator
        report_gen = ReportGenerator(output_dir="output")
        md_file, html_file = report_gen.generate_reports(analysis, criteria, filename, open_browser=True)
        
        logger.info(f"Detailed analysis saved to {filename}.json")
        logger.info(f"Reports generated: {md_file} and {html_file}")
    
    def automated_booking_assistant(self, analysis: SearchAnalysis, criteria: SearchCriteria):
        """Provide automated booking assistance"""
        logger.info("Starting automated booking assistance...")
        
        recommendations = []
        
        # Find best options within budget
        budget_options = [l for l in analysis.best_value_properties 
                         if l.price_per_night <= criteria.max_price_per_night]
        
        if budget_options:
            top_choice = budget_options[0]
            recommendations.append(f"🎯 TOP RECOMMENDATION: {top_choice.title}")
            recommendations.append(f"   Price: ${top_choice.price_per_night}/night")
            recommendations.append(f"   Location: {top_choice.location}")
            recommendations.append(f"   Rating: {top_choice.rating}/5" if top_choice.rating else "   Rating: N/A")
            recommendations.append(f"   Book here: {top_choice.url}")
            
            if top_choice.instant_book:
                recommendations.append("   ✅ Instant booking available!")
            else:
                recommendations.append("   ⏳ Contact host required")
        
        # Alternative options
        if len(budget_options) > 1:
            recommendations.append(f"\n🔍 ALTERNATIVE OPTIONS:")
            for i, option in enumerate(budget_options[1:4], 1):
                recommendations.append(f"   {i}. {option.title} - ${option.price_per_night}/night")
        
        # Booking tips
        recommendations.append(f"\n💡 BOOKING TIPS:")
        recommendations.append("   • Book at least 2-3 months in advance for best availability")
        recommendations.append("   • Contact hosts directly for longer stay discounts")
        recommendations.append("   • Check cancellation policies before booking")
        recommendations.append("   • Consider travel insurance for peace of mind")
        
        # Print recommendations
        print("\n" + "="*60)
        print("🤖 AUTOMATED BOOKING ASSISTANT")
        print("="*60)
        for rec in recommendations:
            print(rec)
        print("="*60)
        
        return recommendations

def main():
    """Example usage of the advanced accommodation search agent"""
    
    # Define search criteria
    criteria = SearchCriteria(
        location="Bar, Montenegro",
        check_in="2024-09-01",
        check_out="2024-09-15",
        guests=2,
        max_price_per_night=40.0,
        amenities=["kitchen", "wifi", "air_conditioning"]
    )
    
    # Create advanced agent
    agent = AdvancedAccommodationAgent(headless=False)
    
    try:
        # Search for accommodations
        print("🔍 Searching for accommodations...")
        results = agent.search_accommodations(criteria)
        
        # Analyze results
        print("📊 Analyzing search results...")
        analysis = agent.analyze_search_results(results, criteria)
        
        # Save detailed analysis
        agent.save_detailed_analysis(analysis, criteria)
        
        # Provide booking assistance
        agent.automated_booking_assistant(analysis, criteria)
        
    finally:
        agent.close()

if __name__ == "__main__":
    main()
