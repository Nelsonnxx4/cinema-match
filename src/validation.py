"""Validation and regex utilities for Group 17.

Responsibility: Henry Mshelia

Purpose:
- Clean user input before it is stored or used in API calls.
- Validate genre choices, search terms, and other user-provided values.
- Reuse common validation functions across the app to reduce bugs.
"""
import re
from errors import ValidationError

#regex patterns

Genre_Pattern = re.compile(r"^[a-zA-Z\s\-]+$")

Search_Parren = re.compile(r"^[a-zA-Z0-9\s\-':]+$")

Search_Max_Length = 100

#approved genres

Valid_Genres = {"Action","Adventure","Animation","Comedy","Crime","Documentry","Drama","Family","Fantasy","History","Horror","Music","Mystery","Romance","Science Fiction","Sci-Fi","Tv Movie","Thriller","War","Western",}

def clear_text(value: str) -> bool:
    if not isinstance(value, str):
        return""

#to make multiple consecutives spaces fall down to a single space 
    return re.sub(r"\s+", " ", value).strip() 

#check if a gene is a recognized genre.
def validate_genre(value: str) -> bool:
    cleaned = clear_text(value)
    if not cleaned:
        return False 
    if not Genre_Pattern.fullmatch(cleaned):
        return False
    return cleaned.title() in Valid_Genres

