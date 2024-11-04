## News (04/11/2024)
The tool now integrates the Groq API to make the translation faster, cheaper and more efficient. The Groq API makes various small open LLM available.



## News (13/09/2024): 
This tool is now available as a workflow in the SSHOC Marketplace. You can find it at https://marketplace.sshopencloud.eu/workflow/rEet9L



## Description

The current commit contains functions for experimenting with different tools.

- Run the notebook test_notebook if you want to start experimenting with the currently available tools (actually, three functions are available: a function that uses DBPedia Spotlight, a function that uses quantized versions of open-source Large Language Models (and so that can be run on a laptop without specialized hardware and without access keys for proprietary models, and a function that uses OpenAI LLMs). Please refer to the code main_functions.py (where the functions are defined) for further details about the functions.
- The files data_utils.py and tools_utils.py contain utility functions. They are useful for various purposes, such as obtaining a sample
of keywords from the GoTriple platform in different languages. They can be used autonomously. Please refer to the code for further detail.

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
