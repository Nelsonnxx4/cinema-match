"""Validation and regex utilities for Group 17.

Responsibility: Henry Mshelia

Purpose:
- Clean user input before it is stored or used in API calls.
- Validate genre choices, search terms, and other user-provided values.
- Reuse common validation functions across the app to reduce bugs.
"""
import re
from src.errors import ValidationError

#regex patterns

Genre_Pattern = re.compile(r"^[a-zA-Z\s\-]+$")

Search_Pattern = re.compile(r"^[a-zA-Z0-9\s\-':]+$")

Search_Max_Length = 100

# approved genres

VALID_GENRES = (
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Music",
    "Mystery",
    "Romance",
    "Science Fiction",
    "TV Movie",
    "Thriller",
    "War",
    "Western",
)

Valid_Genres = set(VALID_GENRES) | {"Documentry", "Sci-Fi", "Tv Movie"}

def clean_text(value: str) -> bool:
    if not isinstance(value, str):
        return""

#to make multiple consecutives spaces fall down to a single space 
    return re.sub(r"\s+", " ", value).strip() 

#check if a gene is a recognized genre.
def validate_genre(value: str) -> bool:
    cleaned = clean_text(value)
    if not cleaned:
        return False 
    if not Genre_Pattern.fullmatch(cleaned):
        return False
    return cleaned.title() in Valid_Genres

def validate_movie_search(query: str) -> str:
#Validates and cleans a movie search term.
    cleaned = clean_text(query)
 
    if not cleaned:
        raise ValidationError("Search query cannot be empty.")
 
    if len(cleaned) > Search_Max_Length:
        raise ValidationError(
            f"Search query is too long (max {Search_Max_Length} characters)."
        )
 
    if not Search_Pattern.fullmatch(cleaned):
        raise ValidationError("Search query contains invalid characters.")
 
    return cleaned

def normalize_genre_list(genres: list[str]) -> list[str]:
#Cleans a list of genres, discards invalid/unrecognized/empty values
    
    if not isinstance(genres, list):
        return []
 
    normalized = []
    seen = set()
 
    for item in genres:
        cleaned = clean_text(item).title()
        if cleaned and validate_genre(cleaned):
            if cleaned not in seen:
                seen.add(cleaned)
                normalized.append(cleaned)
 
    return normalized
