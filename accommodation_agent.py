import time
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SearchCriteria:
    location: str
    check_in: str
    check_out: str
    guests: int
    max_price_per_night: float
    property_type: str = "entire_place"
    amenities: List[str] = None
    
    def __post_init__(self):
        if self.amenities is None:
            self.amenities = ["kitchen", "wifi", "air_conditioning"]

@dataclass
class PropertyListing:
    platform: str
    title: str
    price_per_night: float
    total_price: float
    location: str
    rating: Optional[float]
    review_count: Optional[int]
    amenities: List[str]
    url: str
    property_type: str
    host_name: Optional[str] = None
    instant_book: bool = False
    cancellation_policy: Optional[str] = None

class AccommodationSearchAgent:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.ua = UserAgent()
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        try:
            chrome_options = Options()
            # Headless handling for modern Chrome
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            
            # Use system chrome if present
            try:
                import shutil
                chrome_path = shutil.which("google-chrome") or shutil.which("chromium-browser") or shutil.which("chromium")
                if chrome_path:
                    chrome_options.binary_location = chrome_path
            except Exception:
                pass
            
            # Use undetected-chromedriver for better anti-detection
            self.driver = uc.Chrome(options=chrome_options)
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception:
                pass
            
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            # Fallback to regular selenium
            self.driver = webdriver.Chrome(options=chrome_options)
    
    def search_booking_com(self, criteria: SearchCriteria) -> List[PropertyListing]:
        """Search for accommodations on Booking.com"""
        logger.info(f"Searching Booking.com for {criteria.location}")
        
        try:
            # Build direct search URL to avoid flaky UI interactions
            from urllib.parse import urlencode
            check_in = datetime.strptime(criteria.check_in, "%Y-%m-%d")
            check_out = datetime.strptime(criteria.check_out, "%Y-%m-%d")
            params = {
                "ss": criteria.location,
                "checkin_monthday": check_in.day,
                "checkin_month": check_in.month,
                "checkin_year": check_in.year,
                "checkout_monthday": check_out.day,
                "checkout_month": check_out.month,
                "checkout_year": check_out.year,
                "group_adults": max(criteria.guests, 1),
                "no_rooms": 1,
                "group_children": 0,
                "map": 0,
                "order": "price"
            }
            url = f"https://www.booking.com/searchresults.html?{urlencode(params)}"
            self.driver.get(url)
            time.sleep(5)
            self.accept_cookies()
            
            # Apply filters
            self.apply_booking_filters(criteria)
            
            # Extract results
            listings = self.extract_booking_results()
            
            logger.info(f"Found {len(listings)} properties on Booking.com")
            return listings
            
        except Exception as e:
            logger.error(f"Error searching Booking.com: {e}")
            return []
    
    def search_airbnb(self, criteria: SearchCriteria) -> List[PropertyListing]:
        """Search for accommodations on Airbnb"""
        logger.info(f"Searching Airbnb for {criteria.location}")
        
        try:
            # Build direct search URL (Airbnb URL params are more stable than UI)
            from urllib.parse import urlencode, quote
            check_in = datetime.strptime(criteria.check_in, "%Y-%m-%d").strftime("%Y-%m-%d")
            check_out = datetime.strptime(criteria.check_out, "%Y-%m-%d").strftime("%Y-%m-%d")
            qp = {
                "query": criteria.location,
                "adults": max(criteria.guests, 1),
                "checkin": check_in,
                "checkout": check_out,
                "display_currency": "USD",
                "price_filter_input_type": 0,
                "price_filter_num_nights": 1,
                # Page may ignore price param, but we still include a hint
            }
            url = f"https://www.airbnb.com/s/{quote(criteria.location)}/homes?{urlencode(qp)}"
            self.driver.get(url)
            time.sleep(7)
            self.accept_cookies()
            
            # Apply filters
            self.apply_airbnb_filters(criteria)
            
            # Extract results
            listings = self.extract_airbnb_results()
            
            logger.info(f"Found {len(listings)} properties on Airbnb")
            return listings
            
        except Exception as e:
            logger.error(f"Error searching Airbnb: {e}")
            return []
    
    def accept_cookies(self):
        """Accept cookies on various platforms"""
        try:
            # Common cookie accept selectors
            cookie_selectors = [
                "button[data-testid='cookie-banner-accept']",
                "button[aria-label*='Accept']",
                "button[aria-label*='Accept all']",
                ".cookie-accept",
                "#onetrust-accept-btn-handler"
            ]
            
            for selector in cookie_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    element.click()
                    time.sleep(1)
                    break
                except TimeoutException:
                    continue
                    
        except Exception as e:
            logger.debug(f"No cookie banner found or already accepted: {e}")
    
    def fill_booking_search_form(self, criteria: SearchCriteria):
        """Fill the Booking.com search form"""
        try:
            # Destination input
            destination_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='ss']"))
            )
            destination_input.clear()
            destination_input.send_keys(criteria.location)
            time.sleep(2)
            
            # Select first suggestion
            try:
                suggestion = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".c-autocomplete__item"))
                )
                suggestion.click()
            except TimeoutException:
                destination_input.send_keys(Keys.ENTER)
            
            # Check-in date
            check_in_input = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='date-display-field-start']")
            check_in_input.click()
            
            # Select check-in date
            check_in_date = datetime.strptime(criteria.check_in, "%Y-%m-%d")
            self.select_date(check_in_date)
            
            # Select check-out date
            check_out_date = datetime.strptime(criteria.check_out, "%Y-%m-%d")
            self.select_date(check_out_date)
            
            # Guests
            guests_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='occupancy-config']")
            guests_button.click()
            
            # Set adult count
            adult_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='adults-input']")
            adult_input.clear()
            adult_input.send_keys(str(criteria.guests))
            
            # Search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Error filling Booking.com form: {e}")
    
    def fill_airbnb_search_form(self, criteria: SearchCriteria):
        """Fill the Airbnb search form"""
        try:
            # Destination input
            destination_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='structured-search-input-field-query']"))
            )
            destination_input.clear()
            destination_input.send_keys(criteria.location)
            time.sleep(2)
            
            # Select first suggestion
            try:
                suggestion = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='structured-search-input-field-query-item']"))
                )
                suggestion.click()
            except TimeoutException:
                destination_input.send_keys(Keys.ENTER)
            
            # Check-in date
            check_in_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='structured-search-input-field-split-dates-0']")
            check_in_button.click()
            
            # Select dates
            check_in_date = datetime.strptime(criteria.check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(criteria.check_out, "%Y-%m-%d")
            self.select_airbnb_dates(check_in_date, check_out_date)
            
            # Guests
            guests_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='structured-search-input-field-guests-button']")
            guests_button.click()
            
            # Set guest count
            guest_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='stepper-adults-increase-button']")
            for _ in range(criteria.guests - 1):
                guest_input.click()
            
            # Search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='structured-search-input-search-button']")
            search_button.click()
            
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Error filling Airbnb form: {e}")
    
    def select_date(self, target_date: datetime):
        """Select a date on Booking.com calendar"""
        try:
            # Find the date element
            date_str = target_date.strftime("%Y-%m-%d")
            date_element = self.driver.find_element(
                By.CSS_SELECTOR, 
                f"[data-date='{date_str}']"
            )
            date_element.click()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error selecting date {target_date}: {e}")
    
    def select_airbnb_dates(self, check_in: datetime, check_out: datetime):
        """Select dates on Airbnb calendar"""
        try:
            # Select check-in date
            check_in_str = check_in.strftime("%Y-%m-%d")
            check_in_element = self.driver.find_element(
                By.CSS_SELECTOR,
                f"[data-testid='calendar-day-{check_in_str}']"
            )
            check_in_element.click()
            
            # Select check-out date
            check_out_str = check_out.strftime("%Y-%m-%d")
            check_out_element = self.driver.find_element(
                By.CSS_SELECTOR,
                f"[data-testid='calendar-day-{check_out_str}']"
            )
            check_out_element.click()
            
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error selecting Airbnb dates: {e}")
    
    def apply_booking_filters(self, criteria: SearchCriteria):
        """Apply filters on Booking.com"""
        try:
            # Property type filter - Entire homes & apartments
            try:
                property_filter = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='property-type-filter']"))
                )
                property_filter.click()
                
                entire_place = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='entire-place-filter']")
                entire_place.click()
            except TimeoutException:
                logger.debug("Property type filter not found")
            
            # Price filter
            try:
                price_filter = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='price-filter']")
                price_filter.click()
                
                max_price_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='price-max']")
                max_price_input.clear()
                max_price_input.send_keys(str(int(criteria.max_price_per_night)))
                
                apply_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='filter-button']")
                apply_button.click()
            except TimeoutException:
                logger.debug("Price filter not found")
            
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Error applying Booking.com filters: {e}")
    
    def apply_airbnb_filters(self, criteria: SearchCriteria):
        """Apply filters on Airbnb"""
        try:
            # Property type filter
            try:
                filters_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='filter-button']"))
                )
                filters_button.click()
                
                # Entire place filter
                entire_place = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='entire-place-filter']")
                entire_place.click()
                
                # Price filter
                price_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='price-max-input']")
                price_input.clear()
                price_input.send_keys(str(int(criteria.max_price_per_night)))
                
                # Apply filters
                show_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='filter-button-show']")
                show_button.click()
                
            except TimeoutException:
                logger.debug("Airbnb filters not found")
            
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Error applying Airbnb filters: {e}")
    
    def extract_booking_results(self) -> List[PropertyListing]:
        """Extract property listings from Booking.com results"""
        listings = []
        
        try:
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='property-card']"))
            )
            
            # Get all property cards
            property_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='property-card']")
            
            for card in property_cards[:20]:  # Limit to first 20 results
                try:
                    listing = self.parse_booking_card(card)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.debug(f"Error parsing booking card: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting Booking.com results: {e}")
        
        return listings
    
    def extract_airbnb_results(self) -> List[PropertyListing]:
        """Extract property listings from Airbnb results"""
        listings = []
        
        try:
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='listing-card']"))
            )
            
            # Get all listing cards
            listing_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='listing-card']")
            
            for card in listing_cards[:20]:  # Limit to first 20 results
                try:
                    listing = self.parse_airbnb_card(card)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.debug(f"Error parsing Airbnb card: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting Airbnb results: {e}")
        
        return listings
    
    def parse_booking_card(self, card) -> Optional[PropertyListing]:
        """Parse a Booking.com property card"""
        try:
            # Title
            title = card.find_element(By.CSS_SELECTOR, "[data-testid='title']").text
            
            # Price
            price_element = card.find_element(By.CSS_SELECTOR, "[data-testid='price-and-discounted-price']")
            price_text = price_element.text
            price_per_night = self.extract_price(price_text)
            
            # Location
            location = card.find_element(By.CSS_SELECTOR, "[data-testid='address']").text
            
            # Rating
            try:
                rating_element = card.find_element(By.CSS_SELECTOR, "[data-testid='review-score']")
                rating = float(rating_element.text.split()[0])
            except:
                rating = None
            
            # URL
            url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            
            return PropertyListing(
                platform="Booking.com",
                title=title,
                price_per_night=price_per_night,
                total_price=price_per_night,  # Will be calculated later
                location=location,
                rating=rating,
                review_count=None,
                amenities=[],
                url=url,
                property_type="apartment"
            )
            
        except Exception as e:
            logger.debug(f"Error parsing booking card: {e}")
            return None
    
    def parse_airbnb_card(self, card) -> Optional[PropertyListing]:
        """Parse an Airbnb listing card"""
        try:
            # Title
            title = card.find_element(By.CSS_SELECTOR, "[data-testid='listing-card-name']").text
            
            # Price
            price_element = card.find_element(By.CSS_SELECTOR, "[data-testid='listing-card-price']")
            price_text = price_element.text
            price_per_night = self.extract_price(price_text)
            
            # Location
            location = card.find_element(By.CSS_SELECTOR, "[data-testid='listing-card-location']").text
            
            # Rating
            try:
                rating_element = card.find_element(By.CSS_SELECTOR, "[data-testid='listing-card-rating']")
                rating = float(rating_element.text.split()[0])
            except:
                rating = None
            
            # URL
            url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            
            return PropertyListing(
                platform="Airbnb",
                title=title,
                price_per_night=price_per_night,
                total_price=price_per_night,  # Will be calculated later
                location=location,
                rating=rating,
                review_count=None,
                amenities=[],
                url=url,
                property_type="entire_place"
            )
            
        except Exception as e:
            logger.debug(f"Error parsing Airbnb card: {e}")
            return None
    
    def extract_price(self, price_text: str) -> float:
        """Extract numeric price from price text"""
        import re
        try:
            # Remove currency symbols and extract numbers
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                return float(price_match.group())
            return 0.0
        except:
            return 0.0
    
    def search_accommodations(self, criteria: SearchCriteria) -> Dict[str, List[PropertyListing]]:
        """Search both platforms and return results"""
        results = {}
        
        # Search Booking.com
        booking_results = self.search_booking_com(criteria)
        results['booking_com'] = booking_results
        
        # Search Airbnb
        airbnb_results = self.search_airbnb(criteria)
        results['airbnb'] = airbnb_results
        
        return results
    
    def save_results(self, results: Dict[str, List[PropertyListing]], filename: str = None):
        """Save search results to CSV and JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accommodation_search_{timestamp}"
        
        # Convert to DataFrame
        all_listings = []
        for platform, listings in results.items():
            for listing in listings:
                all_listings.append({
                    'platform': listing.platform,
                    'title': listing.title,
                    'price_per_night': listing.price_per_night,
                    'total_price': listing.total_price,
                    'location': listing.location,
                    'rating': listing.rating,
                    'review_count': listing.review_count,
                    'amenities': ', '.join(listing.amenities),
                    'url': listing.url,
                    'property_type': listing.property_type,
                    'host_name': listing.host_name,
                    'instant_book': listing.instant_book,
                    'cancellation_policy': listing.cancellation_policy
                })
        
        df = pd.DataFrame(all_listings)
        
        # Save to CSV
        df.to_csv(f"{filename}.csv", index=False)
        
        # Save to JSON
        with open(f"{filename}.json", 'w') as f:
            json.dump(all_listings, f, indent=2, default=str)
        
        logger.info(f"Results saved to {filename}.csv and {filename}.json")
        return df
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def main():
    """Example usage of the accommodation search agent"""
    
    # Define search criteria
    criteria = SearchCriteria(
        location="Bar, Montenegro",
        check_in="2024-09-01",
        check_out="2024-09-15",
        guests=2,
        max_price_per_night=40.0,
        amenities=["kitchen", "wifi", "air_conditioning"]
    )
    
    # Create agent
    agent = AccommodationSearchAgent(headless=False)
    
    try:
        # Search for accommodations
        results = agent.search_accommodations(criteria)
        
        # Save results
        df = agent.save_results(results)
        
        # Display summary
        print(f"\nSearch Results Summary:")
        print(f"Booking.com: {len(results['booking_com'])} properties")
        print(f"Airbnb: {len(results['airbnb'])} properties")
        
        if not df.empty:
            print(f"\nTop 5 cheapest properties:")
            top_5 = df.nsmallest(5, 'price_per_night')[['platform', 'title', 'price_per_night', 'location']]
            print(top_5.to_string(index=False))
        
    finally:
        agent.close()

if __name__ == "__main__":
    main()
