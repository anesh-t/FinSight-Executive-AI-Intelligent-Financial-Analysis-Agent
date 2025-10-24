"""Test metric detection for stock prices"""
from formatter import ResponseFormatter

formatter = ResponseFormatter()

# Test queries
queries = [
    "show apple opening price for 2023",
    "show apple opening and closing price for 2023",
    "show closing stock price for apple and microsoft for year 2023",
    "show apple, microsoft, google closing price 2023",
    "show high and low price for apple 2023",
]

for query in queries:
    metrics = formatter._extract_requested_metrics(query)
    print(f"\nQuery: {query}")
    print(f"Detected metrics: {metrics}")
