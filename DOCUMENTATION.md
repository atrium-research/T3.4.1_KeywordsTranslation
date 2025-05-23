# Keywords Translation Tool Documentation

## Overview

This tool provides automated mapping of keywords from multilingual academic articles to Wikidata entities. It supports multiple approaches including DBPedia Spotlight, various Large Language Models (LLMs), and hybrid methodologies. The tool was developed for social sciences and humanities research and has been presented at the MDTT 2025 Conference.

## Table of Contents

1. [Installation](#installation)
2. [Core Modules](#core-modules)
3. [API Reference](#api-reference)
4. [Usage Examples](#usage-examples)
5. [Evaluation](#evaluation)
6. [Data Formats](#data-formats)
7. [Configuration](#configuration)

## Installation

### Requirements
- Python 3.11.x (exact version required)
- Dependencies listed in `requirements.txt`

### Setup
```bash
git clone https://github.com/atrium-research/T3.4.1_KeywordsTranslation
cd T3.4.1_KeywordsTranslation
pip install -r requirements.txt
```

### Verify Installation
```python
python --version  # Should show 3.11.x
```

## Core Modules

### main_functions.py

Contains the primary keyword mapping functions.

#### `useDBPediaSpotlight(item, context)`
Maps keywords using DBPedia Spotlight API with optional SPARQL conversion to Wikidata.

**Parameters:**
- `item` (dict): Article data structure from `get_sample()` or `get_item_by_id()`
- `context` (bool): If True, includes title/abstract as context; if False, processes only keywords

**Returns:**
- List of dictionaries with keys: `'Form'`, `'DBPediaURI'`, `'WikidataURI'`

**Example:**
```python
item = data_utils.get_item_by_id("some_article_id")
results = useDBPediaSpotlight(item, context=True)
```

#### `useOpenAILLM(item, model, context, client)`
Uses OpenAI's API for keyword mapping.

**Parameters:**
- `item` (dict): Article data structure
- `model` (str): OpenAI model ID (e.g., "gpt-3.5-turbo")
- `context` (str): Context level - "Title", "All", or other
- `client`: OpenAI client object from authentication

**Returns:**
- List of dictionaries with keys: `'Keyword'`, `'URI'`

#### `useGroqLLM(item, model_name, context, client)`
Uses Groq API for faster open-source LLM inference.

**Parameters:**
- `item` (dict): Article data structure
- `model_name` (str): Groq model identifier
- `context` (str): Context level - "Title", "All", or other
- `client`: Groq client object from authentication

#### `useLLM_back_and_forth(original_language, title, abstract, keyword, client, model_name, num_entities=1, NUM_NAMES=10)`
Advanced two-step mapping process: entity generation followed by selection.

**Parameters:**
- `original_language` (str): Language code of the article
- `title` (str): Article title
- `abstract` (str): Article abstract
- `keyword` (str): Single keyword to map
- `client`: API client object
- `model_name` (str): Model identifier
- `num_entities` (int): Number of entities to return
- `NUM_NAMES` (int): Number of potential entity names to generate

### data_utils.py

Handles data retrieval and preprocessing from GoTriple API.

#### `query_api(language, query_term, size=10)`
Executes queries against the GoTriple API.

**Parameters:**
- `language` (str): Language code ('es', 'en', 'pt', 'fr', 'de', 'ru', 'ca', 'it', 'nl', 'el', 'hr')
- `query_term` (str): Search term
- `size` (int): Number of results to retrieve (max 250)

#### `get_sample(languages, sample_size)`
Retrieves a balanced multilingual sample of articles.

**Parameters:**
- `languages` (list): List of language codes
- `sample_size` (int): Total number of keywords across all languages

**Returns:**
- List of article dictionaries with standardized structure

#### `get_item_by_id(id)`
Retrieves a specific article by its GoTriple ID.

#### `get_item_from_user()`
Interactive function for manual article data entry.

#### `prompt_generator(item, context)`
Generates prompts for LLM-based keyword mapping.

**Parameters:**
- `item` (dict): Article data structure
- `context` (str): Context level - "Title", "All", or other

### tools_utils.py

Utility functions for API interactions and data processing.

#### `queryAPIDBpediaSpotlight(text, lang, confidence=0.5)`
Direct interface to DBPedia Spotlight API.

#### `get_wikidata_uri(dbpedia_uri)`
Converts DBPedia URIs to Wikidata URIs using SPARQL.

#### `query_wikidata(query_term)`
Searches Wikidata entities and returns best match.

#### `query_best_matches_wikidata(query_term, language="en", number_of_results=3)`
Returns top matching Wikidata entities with scores.

#### `openAI_authentication(key)` / `groq_authentication(key)`
Authentication wrappers for respective APIs.

### prompt_utils.py

Structured prompt management for LLM interactions.

#### `PotentialEntitiesGenerationPrompt`
Handles entity name generation prompts.

#### `EntitySelectionPrompt`  
Manages entity selection from candidates.

### eval_utils.py

Evaluation utilities for performance assessment.

#### `parse_excel_file(filepath)`
Parses Excel evaluation datasets into standardized format.

#### `compute_precision(correct_uris, retrieved_uris)` / `compute_recall(correct_uris, retrieved_uris)`
Calculate standard IR metrics.

## Usage Examples

### Basic DBPedia Spotlight Usage
```python
import data_utils
import main_functions

# Get sample data
items = data_utils.get_sample(['en', 'fr'], 20)

# Process first item
item = items[0]
results = main_functions.useDBPediaSpotlight(item, context=False)

for result in results:
    print(f"Keyword: {result['Form']}")
    print(f"DBPedia: {result['DBPediaURI']}")
    print(f"Wikidata: {result['WikidataURI']}")
```

### OpenAI LLM Usage
```python
import tools_utils
import main_functions

# Authenticate
client = tools_utils.openAI_authentication("your-api-key")

# Process item
results = main_functions.useOpenAILLM(item, "gpt-3.5-turbo", "Title", client)

for result in results:
    print(f"Keyword: {result['Keyword']}")
    print(f"Wikidata URI: {result['URI']}")
```

### Advanced Back-and-Forth Method
```python
# Single keyword processing with two-step approach
selected_entities = main_functions.useLLM_back_and_forth(
    original_language='en',
    title='Article Title',
    abstract='Article Abstract', 
    keyword='democracy',
    client=client,
    model_name='gpt-3.5-turbo',
    num_entities=1,
    NUM_NAMES=5
)
```

### Working with Custom Data
```python
# Manual data entry
item = data_utils.get_item_from_user()

# Or create item programmatically
item = {
    'Language': 'en',
    'Keywords': ['democracy', 'governance'],
    'Title_or': 'Political Systems Study',
    'Title_eng': 'Political Systems Study',
    'Abstract_or': 'Analysis of democratic institutions...',
    'Abstract_eng': 'Analysis of democratic institutions...'
}
```

## Data Formats

### Article Item Structure
```python
{
    'Language': 'en',           # Language code
    'Id': 'article_id',         # GoTriple article ID
    'Keywords': ['kw1', 'kw2'], # List of keywords
    'Title_eng': 'English title',
    'Title_or': 'Original title',
    'Abstract_eng': 'English abstract',
    'Abstract_or': 'Original abstract'
}
```

### Result Formats

#### DBPedia Spotlight Results
```python
{
    'Form': 'democracy',
    'DBPediaURI': 'http://dbpedia.org/resource/Democracy',
    'WikidataURI': 'http://www.wikidata.org/entity/Q7174'
}
```

#### LLM Results
```python
{
    'Keyword': 'democracy',
    'URI': 'http://www.wikidata.org/entity/Q7174'
}
```

## Configuration

### Supported Languages
The tool supports the following language codes:
- `'es'` (Spanish)
- `'en'` (English) 
- `'pt'` (Portuguese)
- `'fr'` (French)
- `'de'` (German)
- `'ru'` (Russian)
- `'ca'` (Catalan)
- `'it'` (Italian)
- `'nl'` (Dutch)
- `'el'` (Greek)
- `'hr'` (Croatian)

### API Endpoints
- **GoTriple API**: `https://api.gotriple.eu/documents`
- **DBPedia Spotlight**: `https://api.dbpedia-spotlight.org/{lang}/annotate`
- **Wikidata API**: `https://www.wikidata.org/w/api.php`
- **DBPedia SPARQL**: `http://dbpedia.org/sparql`

### Query Terms
The `query_terms.json` file contains multilingual search terms used for data sampling. Each entry provides translations across all supported languages.

## Evaluation

### Dataset Format
Evaluation datasets should be Excel files with columns:
- `language`, `id`, `title_or`, `title_eng`, `abstract_or`, `abstract_eng`
- `kw_0`, `Wikidata_url_kw_0`, `match_kw_0` (for first keyword)
- `kw_1`, `Wikidata_url_kw_1`, `match_kw_1` (for second keyword)
- etc.

### Running Evaluation
```python
import eval_utils

# Parse evaluation dataset
data = eval_utils.parse_excel_file('evaluation_files/dataset.xlsx')

# Compute metrics
precision = eval_utils.compute_precision(correct_uris, retrieved_uris)
recall = eval_utils.compute_recall(correct_uris, retrieved_uris)
```

## Troubleshooting

### Common Issues

1. **Python Version Mismatch**
   - Ensure exactly Python 3.11.x is installed
   - Use `python --version` to verify

2. **API Authentication Errors**
   - Verify API keys are correct
   - Check API quotas and rate limits

3. **DBPedia Spotlight Timeouts**
   - Reduce text length when using context=True
   - Implement retry logic for network issues

4. **Empty Results**
   - Check if keywords contain special characters
   - Verify language codes are supported
   - Try different confidence thresholds for DBPedia Spotlight

### Performance Considerations

- **DBPedia Spotlight**: Fast but quality varies by language
- **OpenAI/Groq APIs**: High quality but requires API keys and costs
- **Local LLMs**: No API costs but very slow inference
- **Back-and-forth method**: Highest quality but most expensive
