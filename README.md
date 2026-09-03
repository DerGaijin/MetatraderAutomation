# MetaTrader Automation

Python utilities for automating MetaTrader 5 tasks, including expert compilation, Market Watch setup, strategy backtests, and report parsing.

## Features

- Finds a uniquely installed MetaTrader terminal data directory and its matching MetaEditor executable.
- Starts MetaTrader with custom command-line arguments, optionally minimized in the background.
- Compiles `.mq5` sources and returns structured compiler errors and warnings from the MetaEditor log.
- Identifies compiled `.ex5` program types and deploys experts, indicators, or scripts to the appropriate `MQL5` directory.
- Sets the Market Watch symbol list through the bundled `SetMarketWatch` script.
- Creates Tester `.ini` files and runs configurable backtests with expert input parameters.
- Supports all standard timeframes, tester models, execution modes, optimization modes and criteria, forward-testing modes, deposits, leverage, visualization, and local, remote, or cloud agents.
- Removes matching tester caches and generated report files before a new run.
- Parses HTML backtest reports into backtest metadata, result metrics, and deal history.
- Parses XML optimization reports into typed rows keyed by their report columns.
- Reads MetaTrader `TesterOptCache` files, including cache metadata, input values, optimized inputs, and optimization-pass metrics.

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

## Main APIs

- `find_metaquotes()` and `find_metaeditor()` locate the terminal data directory and MetaEditor.
- `compile_mq5()` compiles a source file; `parse_compile_log()` parses an existing compiler log.
- `deploy_compiled_file()` copies a compiled program to `MQL5/Experts`, `MQL5/Indicators`, or `MQL5/Scripts` based on its EX5 header.
- `set_market_watch()` replaces the current Market Watch selection with the symbols supplied.
- `create_backtest_file()`, `run_backtest_file()`, and `run_backtest_config()` create and run tester configurations.
- `parse_backtest()` parses a generated HTML backtest report.
- `parse_optimization()` parses an XML optimization report, while `parse_optimization_cache()` and `parse_optimization_cache_file()` read binary tester optimization caches.
