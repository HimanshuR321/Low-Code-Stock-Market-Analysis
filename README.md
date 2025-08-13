# Low Code Stock Market Analysis Platform

A comprehensive financial dashboard for tracking, analyzing, and managing stock market portfolios with real-time data visualization and interactive features.

## 🚀 Project Overview

This project is part of my internship in the Industrial Learning Program (2024) and provides a sophisticated financial dashboard for tracking and visualizing stock data. The platform combines modern web technologies with financial data analysis to create an intuitive portfolio management experience.

## ✨ Features

### 📊 Interactive Dashboard
- **Real-time Stock Data**: Live data from Yahoo Finance APIs for 8 major equity stocks
- **Interactive Charts**: Candlestick charts with 2+ years of historical data
- **Portfolio Visualization**: Dynamic pie charts showing portfolio distribution
- **Responsive Design**: Dark theme UI optimized for all device sizes

### 📈 Portfolio Management
- **8 Major Stocks**: AAPL, MSFT, AMZN, GOOGL, TSLA, BRK-B, UNH, JNJ
- **Editable Tables**: Inline editing for quantities, actions, and notes
- **Real-time Calculations**: Automatic market value updates based on quantity changes
- **Action Tracking**: Buy/Sell/Hold recommendations with color-coded indicators

### 🔧 Technical Features
- **Data Caching**: 600-second TTL for optimized performance
- **Database Integration**: MongoDB persistence with RESTful API
- **Responsive Layout**: Stretch-width design with 800px max height constraints
- **Export Functionality**: Copy-to-clipboard support for data analysis

## 🛠️ Technologies Used

### Backend & Data Processing
- **Python 3.12.2**: Core programming language
- **Pandas 2.2.1**: Data manipulation and analysis
- **Flask 3.0.3**: Web framework and REST API
- **MongoDB**: NoSQL database for data persistence
- **PyMongo 4.7.3**: MongoDB driver for Python

### Frontend & Visualization
- **Panel 1.4.4**: Interactive web application framework
- **Plotly 5.22.0**: Advanced charting and visualization
- **HTML/CSS**: Custom styling with dark theme
- **JavaScript**: Interactive functionality and data binding

### Data Sources & APIs
- **Yahoo Finance**: Real-time stock market data
- **Holoviz Datasets**: Historical equity data (2+ years)
- **RESTful APIs**: Custom endpoints for data management

## 📁 Project Structure

```
ILP/
├── dashboard.py          # Main dashboard application (298 lines)
├── panel_code.py         # Enhanced UI components (456 lines)
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── LICENSE              # Project license
└── venv/                # Virtual environment
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.12 or higher
- MongoDB server (local or cloud)
- Git for version control

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd ILP
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure MongoDB
1. Start MongoDB server locally or configure cloud connection
2. Update MongoDB connection string in `dashboard.py` if needed:
   ```python
   client = MongoClient("mongodb://localhost:27017/")
   ```

### Step 5: Run the Application
```bash
python dashboard.py
```

The application will start on:
- **Main Dashboard**: http://localhost:5006
- **Flask API**: http://localhost:5000

## 📊 Dashboard Features

### Stock Portfolio Table
- **8 Columns**: Ticker, Company, Info, Shares, Price, Value, Action, Notes
- **Editable Fields**: Quantity, Action, Notes with validation
- **Frozen Columns**: Ticker and Company names remain visible during scrolling
- **Real-time Updates**: Automatic value calculations on quantity changes

### Interactive Charts
- **Candlestick Charts**: Daily OHLC data with dark theme
- **Portfolio Distribution**: Dynamic pie charts showing allocation percentages
- **Responsive Design**: Charts adapt to screen size and orientation

### Data Management
- **MongoDB Integration**: Persistent storage of portfolio data
- **REST API**: GET and POST endpoints for data operations
- **Data Export**: Copy functionality for external analysis

## 🔌 API Endpoints

### GET /get_data
Retrieves current portfolio data from MongoDB
```bash
curl http://localhost:5000/get_data
```

### POST /update_data
Updates portfolio data in MongoDB
```bash
curl -X POST http://localhost:5000/update_data \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "quantity": 100}'
```

### GET /dashboard
Serves the main Panel dashboard interface

## 🎨 UI/UX Features

### Dark Theme Design
- **Color Scheme**: Professional dark theme with accent colors
- **Responsive Layout**: Optimized for desktop, tablet, and mobile
- **Interactive Elements**: Hover effects and smooth transitions
- **Accessibility**: High contrast and readable typography

### Responsive Components
- **Flexible Tables**: Auto-sizing columns with horizontal scrolling
- **Adaptive Charts**: Charts resize based on viewport dimensions
- **Mobile Optimization**: Touch-friendly interface elements

## 📈 Data Sources

### Stock Information
- **Real-time Prices**: Live data from Yahoo Finance
- **Historical Data**: 2+ years of OHLC data from Holoviz datasets
- **Company Details**: 8 major US equity stocks with company names

### Portfolio Data
- **Sample Holdings**: Pre-configured with realistic portfolio quantities
- **Action Recommendations**: Buy/Sell/Hold suggestions for each position
- **Notes System**: Custom annotations for portfolio management

## 🔧 Configuration Options

### Dashboard Settings
- **Cache TTL**: Configurable data refresh intervals (default: 600 seconds)
- **Chart Themes**: Dark theme with customizable colors
- **Table Layout**: Adjustable column widths and frozen columns
- **Responsive Behavior**: Configurable height and width policies

### MongoDB Configuration
- **Database Name**: `equities_database`
- **Collection Name**: `equities_data`
- **Connection String**: Configurable for local or cloud deployment

## 🚀 Performance Features

### Optimization Strategies
- **Data Caching**: 10-minute TTL reduces API calls
- **Lazy Loading**: Charts render on-demand for better performance
- **Efficient Updates**: Real-time calculations without full page reloads
- **Memory Management**: Optimized data structures for large datasets

### Scalability Considerations
- **Modular Architecture**: Separate components for easy scaling
- **Database Indexing**: Optimized MongoDB queries
- **API Rate Limiting**: Built-in request handling
- **Error Handling**: Graceful degradation for data failures

## 🧪 Testing & Development

### Development Environment
- **Virtual Environment**: Isolated Python dependencies
- **Hot Reload**: Flask debug mode for development
- **Error Logging**: Comprehensive error handling and logging

### Code Quality
- **Modular Design**: Separated concerns between dashboard and UI components
- **Documentation**: Comprehensive inline code comments
- **Best Practices**: PEP 8 compliance and clean code structure

## 📊 Project Statistics

- **Total Lines of Code**: 754 lines (298 + 456)
- **Supported Stocks**: 8 major US equities
- **Data History**: 2+ years of historical data
- **Cache Performance**: 600-second TTL optimization
- **UI Components**: 2 interactive chart types + 1 data table
- **API Endpoints**: 3 RESTful endpoints
- **Database Collections**: 1 MongoDB collection

