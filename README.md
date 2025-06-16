## News (16/06/2025)

The system has been enhanced with web search capabilities and improved evaluation framework:
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

### New Architecture (src/ directory)

The project has been restructured with a modular architecture:

- **LLM Clients (`src/clients/`)**: Unified interface supporting multiple LLM providers:
  - OpenAI (standard and web search enabled)
  - Groq (fast, cost-effective open models)
  - Anthropic Claude
  - All clients implement retry logic and consistent interfaces

- **Processing Pipelines (`src/pipelines/`)**: Two main approaches for entity extraction:
  - **EntityExtractionPipeline**: Multi-step process that generates potential entities, queries Wikidata, and selects best matches
  - **DirectWikidataLinkingPipeline**: Direct keyword-to-URI mapping using OpenAI LLM websearch API

- **Prompt System (`src/prompt.py`)**: Structured prompt templates for different tasks:
  - Entity generation prompts
  - Entity selection prompts  
  - Direct Wikidata linking prompts
  - Schema validation for LLM responses

## Usage Examples

### Using the scripts

```python
from src.clients.clients import GroqClient, OpenAIClient
from src.pipelines.pipelines import EntityExtractionPipeline, DirectWikidataLinkingPipeline

# Initialize LLM client
client = GroqClient(api_key="your-api-key", model_name="llama-3.1-8b-instant")

# Option 1: Multi-step Entity Extraction
pipeline = EntityExtractionPipeline(client)
entities = pipeline.run(
    language="English",
    title="Your paper title",
    abstract="Your paper abstract", 
    keywords="keyword1, keyword2",
    num_entities=3
)

# Option 2: Direct Wikidata Linking
direct_pipeline = DirectWikidataLinkingPipeline(client)
linked_entities = direct_pipeline.run(
    language="English",
    title="Your paper title",
    abstract="Your paper abstract",
    keywords="keyword1, keyword2"
)
```

### Evaluation

Run `notebooks/evaluation.ipynb` to evaluate the system performance using the provided dataset `data/Dset_Eval_KW_Alignment_Eval_def.xlsx`. 

The evaluation system supports multiple LLM providers and generates detailed performance metrics. Results are automatically saved to `data/evaluation_output/` with both raw and adjusted evaluation scores.

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
