## News (16/06/2025)

- **Extensive Evaluation Results**: Completed evaluation on 30 records using OpenAI's GPT-4o with web search capabilities, providing detailed performance metrics
- **Code Refactoring**: Improved code organization by removing legacy implementations and consolidating functionality into the new structure
- **Enhanced Pipeline Architecture**: Moved LLM client initialization inside pipelines for better encapsulation and easier configuration management
- **OpenAI Web Search Integration**: Added support for OpenAI's GPT-4o with web search capabilities for more accurate and up-to-date entity linking
- **Enhanced Evaluation System**: Comprehensive evaluation outputs with support for multiple LLM providers (OpenAI, Groq, Anthropic)
- **Modular Architecture**: Moved evaluation notebooks to dedicated `notebooks/` directory for better organization

## News (24/03/2025)
Our methodology has been presented in a paper accepted at the MDTT 2025 Conference (https://mdtt2025.web.auth.gr/en/)! In the paper, we evaluated our methodology on a newly created dataset of keyword mappings from the GoTriple portal. The evaluation_files of the repo contains the dataset file and the notebook used for the evaluation. 


## News (04/11/2024)
The tool now integrates the Groq API to make the translation faster, cheaper and more efficient. The Groq API makes various small open LLM available.



## News (13/09/2024): 
This tool is now available as a workflow in the SSHOC Marketplace. You can find it at https://marketplace.sshopencloud.eu/workflow/rEet9L



## Description

This project provides a comprehensive framework for keyword translation and entity linking in academic research papers. The system supports multiple LLM providers and offers two main approaches for mapping keywords to Wikidata entities.

## Code Architecture

### Directory Structure

```
src/
├── clients/          # LLM client implementations
├── pipelines/        # Processing workflows
└── utils/           # Supporting utilities
    ├── prompt.py    # LLM prompt templates
    ├── wikidata_data.py  # Wikidata/DBpedia integration
    ├── gotriple_data.py  # GoTriple API integration
    ├── excel.py     # Excel dataset parsing
    └── eval.py      # Evaluation metrics
```

### Core Components

#### **LLM Clients (`src/clients/`)**
Unified interface supporting multiple LLM providers with built-in retry logic:

- **OpenAIClient**: Standard OpenAI API wrapper
- **OpenAIWebSearchClient**: Enhanced with web search capabilities and location context
- **GroqClient**: Fast, cost-effective open-source models
- **AnthropicClient**: Claude API wrapper

All clients implement the same `LLMClient` interface ensuring consistent behavior.

#### **Processing Pipelines (`src/pipelines/`)**
Two main approaches for keyword-to-entity mapping:

- **EntityExtractionPipeline**: Multi-step workflow
  1. Generate potential entity names using LLM
  2. Query Wikidata for candidate matches
  3. Use LLM to select best matches from candidates
  
- **DirectWikidataLinkingPipeline**: Single-step direct mapping
  - Uses OpenAI web search to directly map keywords to Wikidata URIs
  - Provides structured JSON output with entity metadata

#### **Utility Modules (`src/utils/`)**
Supporting functionality for the entire system:

- **Prompt Templates**: Structured prompts with schema validation
- **Wikidata Integration**: SPARQL queries and URI resolution
- **GoTriple Integration**: Research paper retrieval and processing
- **Excel Processing**: Evaluation dataset parsing
- **Evaluation Metrics**: Precision/recall calculations

## Usage Examples

### Pipeline Examples

#### **Multi-step Entity Extraction**
```python
from src.pipelines.pipelines import EntityExtractionPipeline

# Initialize pipeline with different LLM providers
pipeline = EntityExtractionPipeline(
    client_type="groq",  # Options: 'openai', 'groq', 'claude'
    model_name="llama-3.1-8b-instant",
    api_key="your-groq-api-key"
)

# Process research paper
entities = pipeline.run(
    language="English",
    title="Machine Learning in Digital Humanities",
    abstract="This paper explores the application of machine learning techniques...",
    keywords="machine learning, digital humanities, text analysis",
    num_entities=3  # Number of final entities to return
)

print("Selected entities:", entities)
```

#### **Direct Wikidata Linking**
```python
from src.pipelines.pipelines import DirectWikidataLinkingPipeline

# Uses OpenAI with web search capabilities
direct_pipeline = DirectWikidataLinkingPipeline(
    model_name="gpt-4o-search-preview",
    api_key="your-openai-api-key"
)

# Direct keyword-to-URI mapping
linked_entities = direct_pipeline.run(
    language="English",
    title="Digital Archaeology Methods",
    abstract="Contemporary approaches to archaeological documentation...",
    keywords="archaeology, digital methods, cultural heritage"
)

print("Linked entities:", linked_entities)
```

### Utility Functions

#### **Wikidata Integration**
```python
from src.utils.wikidata_data import query_wikidata, query_best_matches_wikidata

# Single best match
result = query_wikidata("machine learning", language="en")
print(f"Best match: {result}")

# Multiple candidates
matches = query_best_matches_wikidata("digital humanities", language="en", number_of_results=5)
for match in matches:
    print(f"Entity: {match['label']} - URI: {match['uri']}")
```

#### **GoTriple Research Data**
```python
from src.utils.gotriple_data import query_gotriple_api, get_gotriple_sample

# Search research papers
papers = query_gotriple_api(
    language="en",
    query_term="digital humanities",
    size=50
)

# Get multilingual sample for evaluation
sample_data = get_gotriple_sample(
    languages=["en", "fr", "de"],
    sample_size=100,
    query_terms_file="evaluation_files/query_terms.json"
)
```

#### **Evaluation and Metrics**
```python
from src.utils.eval import compute_precision, compute_recall
from src.utils.excel import parse_excel_file

# Load evaluation dataset
eval_data = parse_excel_file("evaluation_files/Dset_Eval_KW_Alignment_Eval_def.xlsx")

# Calculate performance metrics
correct_uris = ["http://www.wikidata.org/entity/Q123", "http://www.wikidata.org/entity/Q456"]
retrieved_uris = ["http://www.wikidata.org/entity/Q123", "http://www.wikidata.org/entity/Q789"]

precision = compute_precision(correct_uris, retrieved_uris)
recall = compute_recall(correct_uris, retrieved_uris)

print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")
```

### Configuration Examples

#### **Environment Variables**
```bash
# Set API keys
export OPENAI_API_KEY="your-openai-key"
export GROQ_API_KEY="your-groq-key"
export ANTHROPIC_API_KEY="your-claude-key"
```

#### **Supported Languages**
```python
# Available languages for processing
supported_languages = [
    'en', 'es', 'pt', 'fr', 'de', 'ru', 
    'ca', 'it', 'nl', 'el', 'hr', 'cz'
]
```

### Evaluation

Run `notebooks/evaluation.ipynb` to evaluate the system performance using the provided dataset `evaluation_files/Dset_Eval_KW_Alignment_Eval_def.xlsx`. 

The evaluation system supports multiple LLM providers and generates detailed performance metrics. Results are automatically saved to `evaluation_files/evaluation_output/` with both raw and adjusted evaluation scores.

## How to run the experiments

- You can run the code locally (in this case, refer to the instructions in the installation section for Python version and dependencies)
- Otherwise, you can use Binder. Binder creates for you a self-contained environment where all the dependencies specified in requirements.txt have been installed. While it does not interfere with your system, it should be noted that Binder takes long time to run and that 
changes you bring to the code are not saved when you do them in Binder. 
For running the code in Binder, go to the URL https://mybinder.org/v2/gh/atrium-research/T3.4.1_KeywordsTranslation/HEAD


## Installation

The project requires Python 3.11. Please check you have the correct version before installing dependencies.


1. Clone the repository:
    ```sh
    git clone https://github.com/atrium-research/T3.4.1_KeywordsTranslation
    cd /T3.4.1_KeywordsTranslation
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Python version

Please make sure you are using Python 3.11.x:
    ```sh
    python --version
    # It must show 3.11.x
    ```
