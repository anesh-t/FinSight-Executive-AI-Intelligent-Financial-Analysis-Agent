"""Debug what requested_metrics contains"""
import asyncio
from formatter import Formatter

async def debug():
    formatter = Formatter()
    
    test_questions = [
        "show Apple R&D intensity for 2023",
        "show Apple SG&A intensity for 2023",
        "show Apple R&D expenses for 2023",
        "show Apple ROE for 2023",
    ]
    
    for question in test_questions:
        metrics = formatter._extract_requested_metrics(question)
        print(f"\nQuestion: '{question}'")
        print(f"  Extracted metrics: {metrics}")
        print(f"  Contains 'rd': {'rd' in metrics}")
        print(f"  Contains 'intensity': {'intensity' in metrics}")
        print(f"  Contains 'r&d intensity': {'r&d intensity' in metrics}")

asyncio.run(debug())
