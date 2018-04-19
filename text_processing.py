import re

numberNames = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
letterWords = [
    ("be", "B"), ("bee", "B"),
    ("sea", "C"), ("see", "C"),
    ("eye", "I"),
    ("pea", "P"),
    ("are", "R"),
    ("tee", "T"), ("tea", "T"),
    ("you", "U"), ("ex", "X")
]

def number_words_to_number(text):
    for val, name in enumerate(numberNames):
        text = re.sub(r'\b'+name+r'\b', str(val), text)
    return re.sub(r'(\d)\s+(?=\d)', r'\1', text)

def letters_to_abbrev(text):
    for w, l in letterWords:
        text = re.sub(r'\b'+w+r'\b', l+".", text)
    text = re.sub(r'([A-Z])\. (?=[A-Z]\.)', r'\1', text)
    text = re.sub(r'([A-Z]+)\. ', r'\1 ', text)
    return text

def merge_abbrev_numbers(text):
    text = re.sub(r'([A-Z]+) (?=[0-9]+)', r'\1', text)
    text = re.sub(r'([A-Z0-9]+) (?=[A-Z0-9]+[ \.])', r'\1', text)
    return text

def replace_space(text):
    return re.sub(r' space ', r' ', text)

def normalize(text):
    text = number_words_to_number(text)
    text = letters_to_abbrev(text)
    text = merge_abbrev_numbers(text)
    text = replace_space(text)
    return text

if __name__ == "__main__":
    import sys
    text = sys.argv[1]
    print normalize(text)