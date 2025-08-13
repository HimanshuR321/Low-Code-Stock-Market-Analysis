#import libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import panel as pn

# Initialize Panel with Plotly and Tabulator extensions
pn.extension('plotly', 'tabulator')

# Configure Panel for dark theme
pn.config.theme = 'dark'
pn.config.css_files = []

# Define dark theme color constants
DARK_BG = "#1a1a1a"
DARKER_BG = "#0d0d0d"
DARK_CARD = "#2d2d2d"
DARK_BORDER = "#404040"
DARK_TEXT = "#ffffff"
DARK_TEXT_SECONDARY = "#b0b0b0"
DARK_HOVER = "#3a3a3a"

# Define color constants
ACCENT = "#BB2649"
RED = "#D94467"
GREEN = "#5AD534"

# SVG for external link icon
LINK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up-right-square" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M15 2a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2zM0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm5.854 8.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>
</svg>
"""

# URL to fetch equity data
CSV_URL = "https://datasets.holoviz.org/equities/v1/equities.csv"

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

@pn.cache(ttl=600)
def get_historical_data(tickers=EQUITY_LIST, period="2y"):
    """Downloads the historical data from Yahoo Finance"""
    df = pd.read_csv(CSV_URL, index_col=[0, 1], parse_dates=['Date'])
    return df

# Fetch historical data
historical_data = get_historical_data()
historical_data.head(3).round(2)

def last_close(ticker, data=historical_data):
    """Returns the last close price for the given ticker"""
    return data.loc[ticker]["Close"].iloc[-1]

# Test fetching the last close price for AAPL
last_close("AAPL")

# Prepare the summary data dictionary
summary_data_dict = {
    "ticker": EQUITY_LIST,
    "company": EQUITIES.values(),
    "info": [
        f"""<a href='https://finance.yahoo.com/quote/{ticker}' target='_blank'>
        <div title='Open in Yahoo'>{LINK_SVG}</div></a>"""
        for ticker in EQUITIES
    ],
    "quantity": [75, 40, 100, 50, 40, 60, 20, 40],
    "price": [last_close(ticker) for ticker in EQUITIES],
    "value": None,
    "action": ["buy", "sell", "hold", "hold", "hold", "hold", "hold", "hold"],
    "notes": ["" for i in range(8)],
}

# Convert the summary data dictionary to a DataFrame
summary_data = pd.DataFrame(summary_data_dict)

def get_value_series(data=summary_data):
    """Returns the quantity * price series"""
    return data["quantity"] * data["price"]

# Calculate the value column in the summary data
summary_data["value"] = get_value_series()
summary_data.head(2)

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

widths = {}  # Let the table auto-size columns naturally
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
    layout="fit_data_table",  # Reverted back to original
    selectable=1,
    show_index=False,
    text_align=text_align,
    titles=titles,
    widths=widths,
    configuration=base_configuration,
    theme='modern',
    height=400,
    max_height=400,
    sizing_mode='stretch_width',
    width_policy='max'
)
summary_table

def style_of_action_cell(value, colors={'buy': GREEN, 'sell': RED}):
    """Returns the css to apply to an 'action' cell depending on the value"""
    return f'color: {colors[value]}' if value in colors else ''

# Apply the styles to the summary table
summary_table.style.map(style_of_action_cell, subset=["action"])

# IntInput widget to track patches
patches = pn.widgets.IntInput(description="Used to raise an event when a cell value has changed")

def handle_cell_edit(event, table=summary_table):
    """Updates the `value` cell when the `quantity` cell is updated"""
    row = event.row
    column = event.column
    if column == "quantity":
        quantity = event.value
        price = summary_table.value.loc[row, "price"]
        value = quantity * price
        table.patch({"value": [(row, value)]})

        patches.value += 1

# Function to generate candlestick plot
def candlestick(selection=[], data=summary_data):
    """Returns a candlestick plot"""
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
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_BG,
        font=dict(color=DARK_TEXT),
        xaxis=dict(
            gridcolor=DARK_BORDER,
            zerolinecolor=DARK_BORDER,
            tickfont=dict(color=DARK_TEXT_SECONDARY)
        ),
        yaxis=dict(
            gridcolor=DARK_BORDER,
            zerolinecolor=DARK_BORDER,
            tickfont=dict(color=DARK_TEXT_SECONDARY)
        )
    )
    return fig

# Test generating a candlestick plot
pn.pane.Plotly(candlestick())

# Function to generate portfolio distribution plot
def portfolio_distribution(patches=0):
    """Returns the distribution of the portfolio"""
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
    fig.update_layout(
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_BG,
        font=dict(color=DARK_TEXT),
        title_font_color=DARK_TEXT
    )
    fig.layout.autosize = True
    return fig

# Test generating a portfolio distribution plot
pn.pane.Plotly(portfolio_distribution())

# Bind the candlestick and portfolio_distribution functions to be reactive
candlestick = pn.bind(candlestick, selection=summary_table.param.selection)
summary_table.on_edit(handle_cell_edit)
portfolio_distribution = pn.bind(portfolio_distribution, patches=patches)

# Create the dashboard layout with responsive sizing and dark theme
dashboard = pn.Column(
    pn.Row(
        pn.pane.Plotly(candlestick, sizing_mode='stretch_width', height=300), 
        pn.pane.Plotly(portfolio_distribution, sizing_mode='stretch_width', height=300)
    ),
    pn.pane.HTML('<div style="text-align: center; width: 100%;">', width=0),
    summary_table,
    pn.pane.HTML('</div>', width=0),
    sizing_mode='stretch_width',
    height_policy='fit',
    min_height=600,
    max_height=800,
    styles={
        'background': DARK_BG,
        'color': DARK_TEXT,
        'border': f'1px solid {DARK_BORDER}',
        'padding': '20px',
        'border-radius': '8px'
    }
)

# Make the dashboard responsive and fit viewport
dashboard.servable()

# Add custom CSS for complete dark theme
pn.config.raw_css = [f"""
body {{
    background-color: {DARKER_BG} !important;
    color: {DARK_TEXT} !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
}}

/* Center align the table */
.tabulator {{
    margin: 0 auto !important;
    display: block !important;
    max-width: 90% !important;
}}

.tabulator-tableholder {{
    margin: 0 auto !important;
    display: block !important;
    max-width: 90% !important;
}}

.pn-panel {{
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
}}

.pn-panel .pn-panel {{
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
}}

.pn-widget {{
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
}}

.pn-pane {{
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
}}

/* Ensure Plotly charts have dark backgrounds */
.js-plotly-plot {{
    background-color: {DARK_BG} !important;
}}

/* Style the IntInput widget */
.bk-input {{
    background-color: {DARK_CARD} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.bk-input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px rgba(187, 38, 73, 0.2) !important;
}}

/* Ensure table fits within screen and has dark theme */
.tabulator {{
    max-height: 400px !important;
    overflow-y: auto !important;
    width: 100% !important;
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-tableholder {{
    max-height: 400px !important;
    overflow-y: auto !important;
    width: 100% !important;
    background-color: {DARK_BG} !important;
}}

.tabulator-table {{
    width: 100% !important;
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
}}

.tabulator-header {{
    width: 100% !important;
    background-color: {DARK_CARD} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-header .tabulator-col {{
    background-color: {DARK_CARD} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-row {{
    width: 100% !important;
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-row:nth-child(even) {{
    background-color: {DARKER_BG} !important;
    color: {DARK_TEXT} !important;
}}

.tabulator-row:hover {{
    background-color: {DARK_HOVER} !important;
    color: {DARK_TEXT} !important;
}}

.tabulator-col {{
    width: auto !important;
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-cell {{
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

/* Additional dark theme for table elements */
.tabulator-footer {{
    background-color: {DARK_CARD} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-paginator {{
    background-color: {DARK_CARD} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-paginator button {{
    background-color: {DARK_BG} !important;
    color: {DARK_TEXT} !important;
    border: 1px solid {DARK_BORDER} !important;
}}

.tabulator-paginator button:hover {{
    background-color: {DARK_HOVER} !important;
    color: {DARK_TEXT} !important;
}}

.tabulator-paginator button.active {{
    background-color: {ACCENT} !important;
    color: {DARK_TEXT} !important;
}}

/* Make dashboard responsive */
.pn-panel {{
    max-width: 100vw !important;
    overflow-x: hidden !important;
    width: 100% !important;
}}
"""]
