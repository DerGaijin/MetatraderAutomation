#property strict
input string IN_SYMBOLS = "";
void OnStart()
{
    string symbols[];
    int symbolscount = StringSplit(IN_SYMBOLS, ',', symbols);
    const long current_chart = ChartID();
    for (long chart = ChartFirst(); chart != -1;)
    {
        long next_chart = ChartNext(chart);
        if (chart != current_chart)
        {
            ChartClose(chart);
        }
        chart = next_chart;
    }
    for (int index = SymbolsTotal(true) - 1; index >= 0; index--)
    {
        SymbolSelect(SymbolName(index, true), false);
    }
    for (int index = 0; index < symbolscount; index++)
    {
        StringTrimLeft(symbols[index]);
        StringTrimRight(symbols[index]);
        SymbolSelect(symbols[index], true);
    }
    ChartClose(current_chart);
}
