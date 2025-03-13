import string
import re

# Define the file path
file_path = "/Users/kebbaleigh/Library/Mobile Documents/com~apple~CloudDocs/Documents/Education/DATA 304/data_wrangling_304/data/assignment_2/paragraph.txt"

# Read the text from the file
with open(file_path, 'r') as file:
    text = file.read()

# 1. Split the text into sentences (more robust than just using '.')
sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
number_of_sentences = len(sentences)

# 2. Create a list of words (without punctuation)
text_cleaned = text.translate(str.maketrans('', '', string.punctuation))
words = text_cleaned.split()

# 3. Create a set of unique words
unique_words = set(words)
unique_word_count = len(unique_words)

# 4. Find the hidden message
indexes = [60, 26, 10, 10, 41, 35, 26, 44, 48]
hidden_message = ''.join(words[i][0] for i in indexes if i < len(words))

# Print the required values
print(number_of_sentences)  # 10
print(unique_word_count)    # 81
print(hidden_message)       # 'hAppyCAts'