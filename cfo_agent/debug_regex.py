import re

test = "1ST Q 2023"
pattern = r'\b([1-4])(ST|ND|RD|TH)\s*Q\b'

matches = re.finditer(pattern, test)
for match in matches:
    print(f"Match: '{match.group()}' at position {match.start()}-{match.end()}")
    print(f"  Group 1 (digit): '{match.group(1)}'")
    print(f"  Group 2 (ordinal): '{match.group(2)}'")
