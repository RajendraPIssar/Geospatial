import pandas as pd
from rapidfuzz import fuzz
import spacy
from spellchecker import SpellChecker
import streamlit as st

# Load the spaCy model
nlp = spacy.load("en_core_web_trf", disable=["gpu"])

# Load the dataset
countries = pd.read_csv(r"countries.csv")
countries["category"] = "country"
countries["name"] = countries["name"].apply(lambda x: x.lower())

# List of country names for fuzzy matching
ld_list1 = list(countries["name"])

# Fuzzy matching function
def fuzzy_match_location(user_input, threshold=75.5):
    user_input = user_input.lower()
    matches = []
    for location in ld_list1:
        ratio = fuzz.token_set_ratio(user_input, location)
        if ratio >= threshold and abs(len(location) - len(user_input)) <= 2:
            matches.append((location, ratio, countries[countries["name"] == location]["category"].iloc[0]))
    
    # Sort matches by ratio in descending order
    matches = sorted(matches, key=lambda x: x[1], reverse=True)
    
    if matches:
        return matches[0]
    else:
        return None

# Function to correct names based on fuzzy matching
def correct_names(text):
    spell = SpellChecker()
    misspelled = spell.unknown(text.split())
    misspelled_list = list(misspelled)
    
    # Clean any punctuation at the beginning or end of misspelled words
    cleaned_list = [element[1:] if element[0] == ',' else element[:-1] if element[-1] == ',' else element for element in misspelled_list]
    
    # Process the text with spaCy's NLP model
    doc = nlp(text)
    text = text.title()  # Capitalize text for better name recognition
    
    # Extract named entities (places, people, etc.)
    lst = [word.text.lower() for word in doc.ents]
    
    # Find differences between misspelled words and recognized entities
    set1 = set(lst)
    set2 = set(cleaned_list)
    result = set1.union(set2)
    
    # Perform fuzzy matching on the result
    result_list = list(result)
    results = [fuzzy_match_location(location) for location in result_list]
    
    # Gather matches and retrieve additional info from the dataset
    first_index = [element[0] for element in results if element is not None]
    my_list = []
    for item in first_index:
        row = countries[countries["name"] == item].iloc[0]
        latitude = row["latitude"]
        longitude = row["longitude"]
        category = row["category"]
        my_list.append(f"{item} , {category} , {latitude}, {longitude}")
    
    return my_list

# Streamlit UI
st.title("Fuzzy Location Name Matching")

# Text input for user input
user_input = st.text_input("Enter a location or sentence:")

# Button to trigger the name correction
if st.button("Find Locations"):
    # If user input is given
    if user_input:
        corrected_locations = correct_names(user_input)

        # Display results
        if corrected_locations:
            st.write("Corrected locations with details:")
            for location in corrected_locations:
                st.write(location)
        else:
            st.write("No locations found.")
    else:
        st.write("Please enter a location or sentence.")
