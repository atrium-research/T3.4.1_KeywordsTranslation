## Description

The first commit contains functions for experimenting with different tools.

- The notebook "main" contains function for obtaining WikiData URIs from GoTriple keywords. With the first commit, two functions were introduced: a function that uses DBPedia Spotlight and a function that uses Large Language Models. Please refer to the code for further details on how to use the functions.
- The files data_utils.py and tools_utils.py contain utility functions. They are useful for various purposes, such as obtaining a sample
of keywords from the GoTriple platform in different languages. They can be used autonomously. Please refer to the code for further detail.

## How to run the experiments

- You can run the code locally (in this case, refer to the instructions in the installation section for Python version and dependencies)
- Otherwise, you can use Binder. Binder creates for you a self-contained environment where all the dependencies specified in requirements.txt have been installed. While it does not interfere with your system, it should be noted that Binder takes long time to run and that 
changes you bring to the code are not saved when you do them in Binder. 
For running the code in Binder, follow the instructions at https://the-turing-way.netlify.app/communication/binder/zero-to-binder.html


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