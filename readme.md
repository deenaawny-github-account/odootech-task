# Price List Comparison

This project provides a tool to read, clean, and compare price lists from various file formats (CSV, Excel, PDF), and generate reports in PDF format. The comparison identifies changed prices, new products, and obsolete products between two price lists.

## Features

- Read text from CSV, Excel, and PDF files.
- Extract and clean data from these files.
- Standardize column names using OpenAI's GPT-3.5 API.
- Compare price lists to find changed prices, new products, and obsolete products.
- Unit tests to ensure functionality.
- **High accuracy**: The algorithm demonstrates a high accuracy rate in identifying changed prices, new products, and obsolete products, ensuring reliable comparisons.


## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd price_list_comparison
    ```

2. **Create and activate a virtual environment** (recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the OpenAI API key**:
    - Create a `.env` file in the root directory of the project.
    - Add your OpenAI API key to the `.env` file:
      ```
      OPENAI_API_KEY=your_openai_api_key
      ```
     - Run
       ```
       pip install python-dotenv
       ```
## Usage

1. **Compare Price Lists**:
    - There are two sample files file1.csv and file2.csv
    - Run the script:
      ```sh
      python price_list_comparison.py file1.csv file2.cvs
      ```

2. **Generate PDF Reports**:
    - Use the `generate_pdf` function with a DataFrame and desired file name to generate PDF reports.

## Running Tests

1. **Run the tests**:
    ```sh
    python -m unittest test_price_list_comparison.py
    ```
    Note: the test data creation functions in `test_price_list_comparison.py` correctly generate the necessary sample files.

## Project Structure

