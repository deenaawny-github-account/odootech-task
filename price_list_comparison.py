import pandas as pd
import fitz  # PyMuPDF
import os
import openai
from io import StringIO
from fpdf import FPDF

def read_text_from_file(file_path):
    """
    Reads text from CSV, Excel, or PDF files.
    """
    file_extension = os.path.splitext(file_path)[-1].lower()

    if file_extension == '.csv':
        df = pd.read_csv(file_path)
        text = df.to_string(index=False)
    elif file_extension in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path)
        text = df.to_string(index=False)
    elif file_extension == '.pdf':
        text = read_text_from_pdf(file_path)
        df = extract_table_from_text(text)
    else:
        raise ValueError("Unsupported file format. Supported formats: CSV, Excel, PDF.")
    
    return text, df

def read_text_from_pdf(file_path):
    """
    Reads text from a PDF file.
    """
    doc = fitz.open(file_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def extract_table_from_text(text):
    """
    Extracts a table from text.
    Placeholder function: Implement your table extraction logic.
    """
    # Placeholder: Implement your logic to convert text to a DataFrame
    # For now, return an empty DataFrame
    return pd.DataFrame()

def standardize_columns_with_llm(df_text):
    """
    Uses LLM to identify and standardize column names.
    """
    prompt_template = """
    The following is a table of product data. Standardize the column names that represent product item code and 
    product price to "Product Item Code" and "Product Price". Delete all other columns:

    {text}

    Provide the standardized table with only the new column names. Note: the separator is a comma between columns 
    and column data. 
    Make sure the returned data represents a two column table and not more, meaning remove unecessary comma seperators.
    Do not change product item code values.
    Product price values that are not a digit, none, empty or nan, place the integer zero for the product price value instead.                  
    """
    
    prompt = prompt_template.format(text=df_text)

    response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.7
        )

    return response.choices[0].text.strip()

def clean_data(df):
    """
    Cleans the DataFrame by removing unnecessary whitespace and handling missing values.
    """
    df.columns = [col.strip() for col in df.columns]  # Remove whitespace from column names

    if 'Product Item Code' not in df.columns or 'Product Price' not in df.columns:
        return df

    # Remove any leading or trailing whitespace from the values in the 'Product Item Code' column
    df.loc[:, 'Product Item Code'] = df['Product Item Code'].str.strip()

    # Convert the values in the 'Product Price' column to numeric (float) type
    df.loc[:, 'Product Price'] = pd.to_numeric(df['Product Price'], errors='coerce').fillna(0)

    # Remove rows with missing values in the 'Product Item Code' column
    df = df.dropna(subset=['Product Item Code'])

    # Remove rows with empty strings in the 'Product Item Code' column
    df = df[df['Product Item Code'].str.strip() != '']

    # Remove rows with string zero in the 'Product Item Code' column
    # ChatGPT changes NaN to zero
    df = df[df['Product Item Code'].str.strip() != '0']
  
    return df

def compare_price_lists(file1, file2):
    openai.api_key = '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'
    text1, df1 = read_text_from_file(file1)
    text2, df2 = read_text_from_file(file2)

    standardized_text1 = standardize_columns_with_llm(text1)
    standardized_text2 = standardize_columns_with_llm(text2)

    df1_standardized = pd.read_csv(StringIO(standardized_text1))
    df2_standardized = pd.read_csv(StringIO(standardized_text2))
    
    df1_cleaned = clean_data(df1_standardized)
    df2_cleaned = clean_data(df2_standardized)


    # Compare the price lists
    changed_prices = find_changed_price_products(df1_cleaned, df2_cleaned)
    new_products = find_new_products(df1_cleaned, df2_cleaned)
    obsolete_products = find_obsolete_products(df1_cleaned, df2_cleaned)

    return changed_prices, new_products, obsolete_products

def find_changed_price_products(df1, df2, price_column='Product Price', product_column='Product Item Code'):
    """
    This function takes two dataframes and returns a list of products where the product price has changed.
    """
    # Merge the dataframes on the common columns
    merged_df = pd.merge(df1, df2, on=product_column, suffixes=('_df1', '_df2'))

    # Find products where the price has changed
    changed_price_products = merged_df[merged_df[f'{price_column}_df1'] != merged_df[f'{price_column}_df2']][product_column].tolist()

    return changed_price_products

def find_new_products(df1, df2, product_column='Product Item Code'):
    """
    This function takes two dataframes and returns a list of new products based on the product item code.
    """
    # Convert the product column to sets for both dataframes
    df1_products = set(df1[product_column])
    df2_products = set(df2[product_column])

    # Find products that are in df2 but not in df1
    new_products = list(df2_products - df1_products)

    return new_products

def find_obsolete_products(df1, df2, product_column='Product Item Code'):
    """
    This function takes two dataframes and returns a list of obsolete products based on the product item code.
    """
    # Convert the product column to sets for both dataframes
    df1_products = set(df1[product_column])
    df2_products = set(df2[product_column])

    # Find products that are in df1 but not in df2 (obsolete products)
    obsolete_products = list(df1_products - df2_products)

    return obsolete_products

def generate_pdf(df, file_name):
    """
    Generates a PDF from a DataFrame.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add a title
    pdf.cell(200, 10, txt=file_name.split('.')[0], ln=True, align='C')

    # Add table headers
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size
    for col in df.columns:
        pdf.cell(col_width, row_height * 2, col, border=1)
    pdf.ln(row_height * 2)
    
    # Add table rows
    for row in df.itertuples(index=False):
        for item in row:
            pdf.cell(col_width, row_height * 2, str(item), border=1)
        pdf.ln(row_height * 2)
    
    # Save the PDF
    pdf.output(file_name)