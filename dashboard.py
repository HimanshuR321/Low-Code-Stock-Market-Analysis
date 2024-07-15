# Import necessary libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import panel as pn
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps

# Initialize the Flask application
app = Flask(__name__)

# MongoDB configuration - connecting to the local MongoDB server
client = MongoClient("mongodb://localhost:27017/")  # Change this if using a cloud MongoDB service
db = client['equities_database']  # Database name
collection = db['equities_data']  # Collection name

# Initialize Panel extension for Plotly and Tabulator
pn.extension('plotly', 'tabulator')

# Define constants and configurations for the application
ACCENT = "#BB2649"  # Accent color for the application
RED = "#D94467"  # Red color for sell actions
GREEN = "#5AD534"  # Green color for buy actions
CSV_URL = "https://datasets.holoviz.org/equities/v1/equities.csv"  # URL to fetch equity data

# Dictionary of equity tickers and their corresponding company names
EQUITIES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet",
    "TSLA": "Tesla",
    "BRK-B": "Berkshire Hathaway",
    "UNH": "United Health Group",
    "JNJ": "Johnson & Johnson",
}
EQUITY_LIST = tuple(EQUITIES.keys())  # List of equity tickers

# Cache function to get historical data with a time-to-live of 600 seconds
@pn.cache(ttl=600)
def get_historical_data(tickers=EQUITY_LIST, period="2y"):
    df = pd.read_csv(CSV_URL, index_col=[0, 1], parse_dates=['Date'])
    return df

# Fetch historical data
historical_data = get_historical_data()

# Function to get the last closing price for a given ticker
def last_close(ticker, data=historical_data):
    return data.loc[ticker]["Close"].iloc[-1]

# Function to fetch data from MongoDB
def get_data_from_mongodb():
    data = list(collection.find({}))
    return pd.DataFrame(data)

# Function to store data to MongoDB
def store_data_to_mongodb(data):
    collection.delete_many({})
    collection.insert_many(data.to_dict('records'))

# Prepare the summary data for the equities
summary_data_dict = {
    "ticker": EQUITY_LIST,
    "company": list(EQUITIES.values()),
    "info": [
        f"""<a href='https://finance.yahoo.com/quote/{ticker}' target='_blank'>
        <div title='Open in Yahoo'>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up-right-square" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M15 2a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2zM0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm5.854 8.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>
        </svg>
        </div></a>"""
        for ticker in EQUITIES
    ],
    "quantity": [75, 40, 100, 50, 40, 60, 20, 40],
    "price": [last_close(ticker) for ticker in EQUITIES],
    "value": None,
    "action": ["buy", "sell", "hold", "hold", "hold", "hold", "hold", "hold"],
    "notes": ["" for _ in range(8)],
}

# Convert the summary data dictionary to a DataFrame
summary_data = pd.DataFrame(summary_data_dict)

# Function to calculate the market value of each equity
def get_value_series(data=summary_data):
    return data["quantity"] * data["price"]

# Calculate the value column in the summary data
summary_data["value"] = get_value_series()

# Store the initial summary data to MongoDB
store_data_to_mongodb(summary_data)

# Define configuration for the summary table columns
titles = {
    "ticker": "Stock Ticker",
    "company": "Company",
    "info": "Info",
    "quantity": "Shares",
    "price": "Last Close Price",
    "value": "Market Value",
    "action": "Action",
    "notes": "Notes",
}
frozen_columns = ["ticker", "company"]  # Columns to be frozen
editors = {
    "ticker": None,
    "company": None,
    "quantity": {"type": "number", "min": 0, "step": 1},
    "price": None,
    "value": None,
    "action": {
        "type": "list",
        "values": {"buy": "buy", "sell": "sell", "hold": "hold"},
    },
    "notes": {
        "type": "textarea",
        "elementAttributes": {"maxlength": "100"},
        "selectContents": True,
        "verticalNavigation": "editor",
        "shiftEnterSubmit": True,
    },
    "info": None,
}
widths = {"notes": 400}  # Set custom width for notes column
formatters = {
    "price": {"type": "money", "decimal": ".", "thousand": ",", "precision": 2},
    "value": {"type": "money", "decimal": ".", "thousand": ",", "precision": 0},
    "info": {"type": "html", "field": "html"},
}
text_align = {
    "price": "right",
    "value": "right",
    "action": "center",
    "info": "center",
}
base_configuration = {
    "clipboard": "copy"  # Enable copying data to clipboard
}

# Create the summary table widget using Panel's Tabulator
summary_table = pn.widgets.Tabulator(
    summary_data,
    editors=editors,
    formatters=formatters,
    frozen_columns=frozen_columns,
    layout="fit_data_table",
    selectable=1,
    show_index=False,
    text_align=text_align,
    titles=titles,
    widths=widths,
    configuration=base_configuration,
)

# Define the style function for the action cell
def style_of_action_cell(value, colors={'buy': GREEN, 'sell': RED}):
    return f'color: {colors[value]}' if value in colors else ''

# Apply the styles to the summary table
summary_table.style.map(style_of_action_cell, subset=["action"]).set_properties(
    **{"background-color": "#444"}, subset=["quantity"]
)

# IntInput widget to track patches
patches = pn.widgets.IntInput(description="Used to raise an event when a cell value has changed")

# Function to handle cell edits
def handle_cell_edit(event, table=summary_table):
    row = event.row
    column = event.column
    if column == "quantity":
        quantity = event.value
        price = summary_table.value.loc[row, "price"]
        value = quantity * price
        table.patch({"value": [(row, value)]})
        patches.value += 1

# Bind the cell edit event to the handle_cell_edit function
summary_table.on_edit(handle_cell_edit)

# Function to generate candlestick plot
def candlestick(selection=[], data=summary_data):
    if not selection:
        ticker = "AAPL"
        company = "Apple"
    else:
        index = selection[0]
        ticker = data.loc[index, "ticker"]
        company = data.loc[index, "company"]

    dff_ticker_hist = historical_data.loc[ticker].reset_index()
    dff_ticker_hist["Date"] = pd.to_datetime(dff_ticker_hist["Date"])

    fig = go.Figure(
        go.Candlestick(
            x=dff_ticker_hist["Date"],
            open=dff_ticker_hist["Open"],
            high=dff_ticker_hist["High"],
            low=dff_ticker_hist["Low"],
            close=dff_ticker_hist["Close"],
        )
    )
    fig.update_layout(
        title_text=f"{ticker} {company} Daily Price",
        template="plotly_dark",
        autosize=True,
    )
    return fig

# Function to generate portfolio distribution plot
def portfolio_distribution(patches=0):
    data = summary_table.value
    portfolio_total = data["value"].sum()

    fig = px.pie(
        data,
        values="value",
        names="ticker",
        hole=0.3,
        title=f"Portfolio Total $ {portfolio_total:,.0f}",
        template="plotly_dark",
    )
    fig.layout.autosize = True
    return fig

# Bind the candlestick and portfolio_distribution functions to be reactive
candlestick = pn.bind(candlestick, selection=summary_table.param.selection)
portfolio_distribution = pn.bind(portfolio_distribution, patches=patches)

# Create the dashboard layout
dashboard = pn.Column(
    pn.Row(
        pn.pane.Plotly(candlestick), 
        pn.pane.Plotly(portfolio_distribution)
    ),
    summary_table,
    height=600
)

# Flask API endpoint to get data from MongoDB
@app.route('/get_data', methods=['GET'])
def get_data():
    data = get_data_from_mongodb()
    return data.to_json(orient='records')

# Flask API endpoint to update data in MongoDB
@app.route('/update_data', methods=['POST'])
def update_data():
    data = request.json
    df = pd.DataFrame(data)
    store_data_to_mongodb(df)
    return jsonify({"status": "success"})

# Function to serve the Panel dashboard
@app.route('/dashboard')
def serve_dashboard():
    return dashboard.show(port=5006, open=False)

# Run Flask app
if __name__ == "__main__":
    app.run(port=5000, debug=True)

# Function to save data to MongoDB from the Panel dashboard
import requests

def save_data():
    url = "http://localhost:5000/update_data"
    headers = {'Content-Type': 'application/json'}
    data = summary_table.value.to_json(orient='records')
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Data saved successfully.")
    else:
        print("Error saving data.")

# Add the save button to the Panel dashboard
save_button = pn.widgets.Button(name='Save Data', button_type='primary')
save_button.on_click(lambda event: save_data())

# Update the dashboard layout to include the save button
dashboard = pn.Column(
    pn.Row(
        pn.pane.Plotly(candlestick), 
        pn.pane.Plotly(portfolio_distribution)
    ),
    summary_table,
    save_button,
    height=600
)

# Make the dashboard servable
dashboard.servable()
