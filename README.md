# 🏨 Accommodation Search Agent

An intelligent web automation agent that can search for accommodations on Booking.com and Airbnb, analyze results, and provide personalized recommendations for your travel needs.

## 🌟 Features

- **Multi-Platform Search**: Searches both Booking.com and Airbnb simultaneously
- **Real-Time Pricing**: Gets actual current prices and availability
- **Advanced Filtering**: Applies your specific criteria (dates, guests, budget, amenities)
- **Detailed Analysis**: Provides value scores, location analysis, and market insights
- **Automated Recommendations**: Suggests the best options based on your preferences
- **Data Export**: Saves results to CSV, JSON, and Excel formats
- **Anti-Detection**: Uses advanced techniques to avoid being blocked by websites

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Chrome browser (if not already installed)
# The agent will automatically download ChromeDriver
```

### 2. Run the Agent

#### Interactive Mode (Recommended)
```bash
python cli_interface.py
```

#### Quick Search (Default Montenegro settings)
```bash
python cli_interface.py --quick
```

#### Headless Mode (No browser window)
```bash
python cli_interface.py --headless
```

### 3. Follow the Prompts

The agent will guide you through:
- Location selection
- Date range
- Number of guests
- Budget constraints
- Amenity preferences
- Property type preferences

## 📋 Requirements

- **Python 3.8+**
- **Chrome Browser** (will be auto-downloaded)
- **Internet Connection**

## 🔧 Installation Details

### System Requirements

#### Linux
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y chromium-browser
```

#### macOS
```bash
# Install via Homebrew
brew install --cask google-chrome
```

#### Windows
- Download and install Chrome from https://www.google.com/chrome/

### Python Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 How It Works

### 1. Search Process
1. **Input Validation**: Validates your search criteria
2. **Web Automation**: Opens browser and navigates to booking sites
3. **Form Filling**: Automatically fills search forms with your criteria
4. **Filter Application**: Applies your filters (price, amenities, etc.)
5. **Data Extraction**: Scrapes property listings and pricing
6. **Analysis**: Calculates value scores and provides insights

### 2. Analysis Features
- **Value Scoring**: Combines price, amenities, and ratings
- **Location Analysis**: Evaluates proximity to your target area
- **Market Insights**: Provides pricing trends and availability
- **Recommendations**: Suggests best options within your budget

### 3. Output Formats
- **CSV**: Simple spreadsheet format
- **JSON**: Detailed structured data
- **Excel**: Multi-sheet workbook with analysis
- **Console**: Real-time recommendations

## 📊 Example Output

```
🤖 AUTOMATED BOOKING ASSISTANT
============================================================
🎯 TOP RECOMMENDATION: Cozy Apartment in Bar Old Town
   Price: $35/night
   Location: Bar, Montenegro
   Rating: 4.8/5
   Book here: https://booking.com/property/12345
   ✅ Instant booking available!

🔍 ALTERNATIVE OPTIONS:
   1. Beach View Studio - $38/night
   2. Modern Apartment Center - $40/night

💡 BOOKING TIPS:
   • Book at least 2-3 months in advance for best availability
   • Contact hosts directly for longer stay discounts
   • Check cancellation policies before booking
   • Consider travel insurance for peace of mind
============================================================
```

## 🛠️ Advanced Usage

### Programmatic Usage

```python
from accommodation_agent import AccommodationSearchAgent, SearchCriteria

# Create search criteria
criteria = SearchCriteria(
    location="Bar, Montenegro",
    check_in="2024-09-01",
    check_out="2024-09-15",
    guests=2,
    max_price_per_night=40.0,
    amenities=["kitchen", "wifi", "air_conditioning"]
)

# Create agent and search
agent = AccommodationSearchAgent(headless=False)
results = agent.search_accommodations(criteria)
agent.save_results(results)
agent.close()
```

### Advanced Analysis

```python
from advanced_accommodation_agent import AdvancedAccommodationAgent

# Create advanced agent
agent = AdvancedAccommodationAgent(headless=False)

# Search and analyze
results = agent.search_accommodations(criteria)
analysis = agent.analyze_search_results(results, criteria)

# Save detailed analysis
agent.save_detailed_analysis(analysis)

# Get booking assistance
agent.automated_booking_assistant(analysis, criteria)
```

## 📁 File Structure

```
accommodation-search-agent/
├── accommodation_agent.py          # Basic search agent
├── advanced_accommodation_agent.py # Advanced analysis agent
├── cli_interface.py               # Command-line interface
├── requirements.txt               # Python dependencies
├── README.md                     # This file
├── montenegro_accommodation_strategy.md  # Original strategy document
└── data/                         # Output directory (created automatically)
    ├── accommodation_search_20241201_143022.csv
    ├── accommodation_search_20241201_143022.json
    ├── detailed_analysis_20241201_143022.xlsx
    └── detailed_analysis_20241201_143022.json
```

## 🔍 Search Capabilities

### Supported Platforms
- **Booking.com**: Full search and filtering
- **Airbnb**: Full search and filtering

### Search Filters
- **Location**: Any destination worldwide
- **Dates**: Flexible check-in/check-out
- **Guests**: 1-20 guests
- **Price Range**: Customizable budget
- **Property Type**: Entire place, private room, shared room
- **Amenities**: Kitchen, WiFi, AC, parking, etc.

### Analysis Features
- **Value Scoring**: Price-to-amenity ratio
- **Location Scoring**: Proximity to target area
- **Market Analysis**: Price trends and availability
- **Host Analysis**: Response rates and ratings
- **Booking Recommendations**: Instant vs. contact required

## ⚠️ Important Notes

### Rate Limiting
- The agent includes delays between requests to be respectful to websites
- Don't run multiple instances simultaneously
- Consider using headless mode for faster execution

### Legal Considerations
- This tool is for personal use only
- Respect website terms of service
- Don't use for commercial scraping
- Be mindful of rate limits

### Troubleshooting

#### Chrome Driver Issues
```bash
# If ChromeDriver fails to download automatically
pip install webdriver-manager --upgrade
```

#### Permission Issues (Linux/macOS)
```bash
# Make CLI executable
chmod +x cli_interface.py
```

#### Browser Detection
- The agent uses anti-detection techniques
- If blocked, try running in headless mode
- Consider using a VPN if needed

## 🎯 Use Cases

### Perfect For:
- **Budget Travel**: Find the best value accommodations
- **Long-term Stays**: Analyze monthly rates and discounts
- **Group Travel**: Search for larger properties
- **Last-minute Booking**: Check real-time availability
- **Market Research**: Understand pricing trends

### Example Scenarios:
1. **Montenegro Trip**: Find budget apartments in Bar area
2. **Group Vacation**: Search for 6-person villas in popular destinations
3. **Business Travel**: Find long-term furnished apartments
4. **Weekend Getaway**: Quick search for last-minute availability

## 🤝 Contributing

Feel free to contribute improvements:
- Bug fixes
- Additional platform support
- Enhanced analysis features
- Better UI/UX

## 📄 License

This project is for educational and personal use only. Please respect the terms of service of the websites being accessed.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify Chrome browser is installed
4. Check your internet connection
5. Try running in headless mode

---

**Happy Travel Planning! 🗺️✈️**
