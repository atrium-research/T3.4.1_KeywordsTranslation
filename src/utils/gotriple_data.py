"""
GoTriple API utility functions extracted from legacy codebase.
Provides functionality for querying the GoTriple research platform API.
"""

import json
import requests
from typing import List, Dict, Optional, Any, Union


def query_gotriple_api(
    language: str, 
    query_term: str, 
    size: int = 250,
    include_duplicates: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Execute a query using the GoTriple API.
    
    Args:
        language: Language of the articles to search for
        query_term: Search term/query
        size: Number of documents to retrieve (default: 250)
        include_duplicates: Whether to include duplicate results
        
    Returns:
        JSON data if successful, None otherwise
    """
    url = 'https://api.gotriple.eu/documents'
    params = {
        'q': query_term,
        'include_duplicates': str(include_duplicates).lower(),
        'fq': f'in_language={language}',
        'size': size
    }
    
    headers = {
        'accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'GoTriple API Error: {e}')
        return None


def get_gotriple_item_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific GoTriple document by its ID.
    
    Args:
        document_id: The ID of the document to retrieve
        
    Returns:
        Formatted document data or None if not found
    """
    url = f'https://api.gotriple.eu/documents/{document_id}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        document = response.json()
        
        # Extract keywords in original language
        keywords_original_language = [kw['text'] for kw in document.get("keywords", [])]
        
        if not keywords_original_language:
            print(f'No keywords found for article with id: {document_id}')
            return None
        
        # Format the document data
        item = {
            'Language': document['in_language'][0] if document.get('in_language') else None,
            'Id': document.get('id'),
            'Keywords': keywords_original_language,
            'Title_eng': None,
            'Title_or': None,
            'Abstract_eng': None,
            'Abstract_or': None
        }
        
        # Extract titles in different languages
        for headline in document.get('headline', []):
            if headline.get('lang') == 'en':
                item['Title_eng'] = headline.get('text')
            if headline.get('lang') == item['Language']:
                item['Title_or'] = headline.get('text')
        
        # Extract abstracts in different languages
        for abstract in document.get('abstract', []):
            if abstract.get('lang') == 'en':
                item['Abstract_eng'] = abstract.get('text')
            if abstract.get('lang') == item['Language']:
                item['Abstract_or'] = abstract.get('text')
        
        return item
        
    except requests.RequestException as e:
        print(f'Error retrieving document {document_id}: {e}')
        return None


def create_manual_gotriple_item() -> Dict[str, Any]:
    """
    Create a GoTriple-style item manually through user input.
    Interactive function for testing purposes.
    
    Returns:
        Dictionary with user-provided article data
    """
    item = {
        'Language': None, 
        'Id': None, 
        'Keywords': [], 
        'Title_eng': None, 
        'Title_or': None, 
        'Abstract_eng': None, 
        'Abstract_or': None
    }
    
    # Get language
    supported_languages = ['en', 'fr', 'pt', 'es', 'de', 'ru', 'ca', 'it', 'nl', 'el', 'hr']
    
    while True:
        language = input(f"Enter article language {supported_languages}: ").lower()
        if language in supported_languages:
            item['Language'] = language
            break
        print("Invalid language")
    
    # Get other fields
    keywords = input("Enter keywords (comma-separated): ")
    item['Keywords'] = [kw.strip() for kw in keywords.split(',')]
    
    item['Title_or'] = input("Enter title in original language (or 'unknown'): ")
    item['Title_eng'] = input("Enter title in English (or 'unknown'): ")
    item['Abstract_or'] = input("Enter abstract in original language (or 'unknown'): ")
    item['Abstract_eng'] = input("Enter abstract in English (or 'unknown'): ")
    
    # Convert 'unknown' to None
    for key in ['Title_or', 'Title_eng', 'Abstract_or', 'Abstract_eng']:
        if item[key].lower() == 'unknown':
            item[key] = None
    
    return item


def get_gotriple_sample(
    languages: List[str], 
    sample_size: int,
    query_terms_file: str = "query_terms.json"
) -> List[Dict[str, Any]]:
    """
    Get a sample of data from GoTriple API across multiple languages.
    
    Args:
        languages: List of language codes to sample from
        sample_size: Total number of keywords to collect
        query_terms_file: Path to JSON file with query terms
        
    Returns:
        List of formatted document items
    """
    total_items = []
    
    # Load query terms
    try:
        with open(query_terms_file, "r") as file:
            query_terms = json.load(file)
    except FileNotFoundError:
        print(f"Query terms file '{query_terms_file}' not found")
        return []
    except json.JSONDecodeError:
        print(f"Invalid JSON in query terms file '{query_terms_file}'")
        return []
    
    keywords_per_language = sample_size // len(languages)
    
    # Sample from each language
    for language in languages:
        items = []
        query_terms_iter = iter(query_terms)
        keywords_count = 0
        
        while keywords_count < keywords_per_language:
            try:
                next_query_term = next(query_terms_iter)
                
                # Get query term for this language
                if language not in next_query_term:
                    continue
                    
                data = query_gotriple_api(language, next_query_term[language])
                
                if not data:
                    print("Error in API query")
                    continue
                
                # Process documents
                for document in data:
                    keywords_original_language = [
                        kw['text'] for kw in document.get("keywords", []) 
                        if kw.get("lang") == language
                    ]
                    
                    if not keywords_original_language:
                        continue
                    
                    # Format document item
                    item = {
                        'Language': language,
                        'Id': document.get("id"),
                        'Keywords': keywords_original_language,
                        'Title_eng': None,
                        'Title_or': None,
                        'Abstract_eng': None,
                        'Abstract_or': None
                    }
                    
                    # Extract titles and abstracts
                    for headline in document.get("headline", []):
                        if headline.get("lang") == "en":
                            item['Title_eng'] = headline.get("text")
                        if headline.get("lang") == language:
                            item['Title_or'] = headline.get("text")
                    
                    for abstract in document.get("abstract", []):
                        if abstract.get("lang") == "en":
                            item['Abstract_eng'] = abstract.get("text")
                        if abstract.get("lang") == language:
                            item['Abstract_or'] = abstract.get("text")
                    
                    keywords_count += len(keywords_original_language)
                    items.append(item)
                    
            except StopIteration:
                print(f"Ran out of query terms for language {language}")
                break
        
        # Trim items to exact keyword count
        items_iter = iter(items)
        final_items = []
        keywords_count = 0
        
        try:
            while keywords_count < keywords_per_language:
                next_item = next(items_iter)
                final_items.append(next_item)
                keywords_count += len(next_item['Keywords'])
        except StopIteration:
            pass
        
        total_items.extend(final_items)
    
    return total_items


def format_gotriple_item_for_processing(item: Dict[str, Any]) -> Dict[str, str]:
    """
    Format a GoTriple item for use with LLM processing pipelines.
    
    Args:
        item: GoTriple item dictionary
        
    Returns:
        Formatted dictionary with standardized keys
    """
    return {
        'language': item.get('Language', ''),
        'title': item.get('Title_eng') or item.get('Title_or', ''),
        'abstract': item.get('Abstract_eng') or item.get('Abstract_or', ''),
        'keywords': ', '.join(item.get('Keywords', [])),
        'original_title': item.get('Title_or', ''),
        'original_abstract': item.get('Abstract_or', ''),
        'document_id': item.get('Id', '')
    }