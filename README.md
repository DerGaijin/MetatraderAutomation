# MetaTrader Automation

Python utilities for automating MetaTrader 5 tasks, including expert compilation, Market Watch setup, strategy backtests, and report parsing.

## Requirements

- Windows with MetaTrader 5 installed
- Python 3.10+
- Beautiful Soup: `pip install beautifulsoup4`

## Usage

```python
from MetatraderAutomation import BacktestConfig, find_metaeditor, find_metaquotes, run_backtest_config

terminal_data = find_metaquotes()
metaeditor = find_metaeditor(terminal_data)

config = BacktestConfig(
    symbol="EURUSD",
    from_date="2024.01.01",
    to_date="2025.01.01",
    report_name="BacktestResult.htm",
)

run_backtest_config(
    terminal_data,
    metaeditor,
    "Examples\\MACD Sample.ex5",
    config,
)
```

The example runs the bundled `MACD Sample` expert and writes the report to the terminal data directory.
