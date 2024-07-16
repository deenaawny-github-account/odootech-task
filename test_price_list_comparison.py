import unittest
import os
import pandas as pd
from price_list_comparison import (
    read_text_from_file,
    read_text_from_pdf,
    extract_table_from_text,
    standardize_columns_with_llm,
    clean_data,
    compare_price_lists,
    find_changed_price_products,
    find_new_products,
    find_obsolete_products,
    generate_pdf
)

class TestPriceListComparison(unittest.TestCase):

    def setUp(self):
        self.create_sample_data()
        self.create_sample_pdfs()

    def create_sample_pdfs(self):
        # Create sample PDFs
        df_csv_15 = pd.DataFrame({
            "Product Item Code": ["P036", "P037", None, "P039", "P040"],
            "Product Price": [20.00, None, 29.50, None, 42.00],
            "Product Name": ["Widget", "Gadget", "Doodad", "Thingamajig", None],
            "Product Description": ["Useful widget", None, "An interesting doodad", "A thingamajig", "A unique gadget"],
            "Stock Quantity": [100, 50, None, 75, 200]
        })

        df_xlsx_16 = pd.DataFrame({
            "Product Item Code": [None, "P042", "P043", None, "P045"],
            "Product Price": [30.00, 35.00, None, 40.75, None],
            "Product Name": ["Contraption", "Device", None, "Apparatus", "Machine"],
            "Product Description": ["A handy contraption", "A useful device", "An apparatus", None, "A powerful machine"],
            "Stock Quantity": [None, 80, 60, 120, 150]
        })

        generate_pdf(df_csv_15, "price_list_15.pdf")
        generate_pdf(df_xlsx_16, "price_list_16.pdf")

    def create_sample_data(self):
        # Sample data for other files
        data_sets = [
            ("price_list_1.csv", {"Product Item Code": ["P001", "P002", "P003", "P004", "P005"], "Product Price": [10.00, 15.50, 20.00, 25.75, 30.00]}),
            ("price_list_2.xlsx", {"Product Item Name": ["P002", "P003", "P004", "P006", "P007"], "Product Price": [15.50, 22.00, 25.75, 35.00, 40.00]}),
            ("price_list_3.csv", {"Product Item Code": ["P008", "P009", "P010", "P011", "P012"], "Product Value": [12.00, 18.50, 23.00, 28.75, 33.00]}),
            ("price_list_4.xlsx", {"Product Item Code": ["P011", "P013", "P014", "P015", "P016"], "Product Price": [28.75, 31.00, 37.50, 45.00, 50.00]}),
            ("price_list_5.csv", {"Product Price": [17.00, 25.50, 33.00, 41.75, 49.00], "Product Item Code": ["P017", "P018", "P019", "P020", "P021"]}),
            ("price_list_6.xlsx", {"Product Item Code": ["P018", "P022", "P023", "P024", "P025"], "Product Price": [25.50, 30.00, 35.00, 40.00, 45.00]}),
            ("price_list_7.csv", {"Product Item Code": ["P026", "P027", "P028", None, "P030"], "Product Price": [None, 22.50, 27.00, 33.75, None]}),
            ("price_list_8.xlsx", {"Product Item Code": ["P031", None, "P033", "P034", "P035"], "Product Price": [19.75, 25.00, None, 38.50, 44.00]}),
            ("price_list_9.csv", {"Product Item Code": ["P036", "P037", None, "P039", "P040"], "Product Price": [20.00, None, 29.50, None, 42.00]}),
            ("price_list_10.xlsx", {"Product Item Code": [None, "P042", "P043", None, "P045"], "Product Price": [30.00, 35.00, None, 40.75, None]}),
            ("price_list_11.csv", {"Product Item Code": ["P036", "P037", None, "P039", "P040"], "Product Name": ["Widget", "Gadget", "Doodad", "Thingamajig", None], "Product Price": [20.00, None, 29.50, None, 42.00], "Product Description": ["Useful widget", None, "An interesting doodad", "A thingamajig", "A unique gadget"], "Stock Quantity": [100, 50, None, 75, 200]}),
            ("price_list_12.xlsx", {"Product Item Code": [None, "P042", "P043", None, "P045"], "Product Price": [30.00, 35.00, None, 40.75, None], "Product Name": ["Contraption", "Device", None, "Apparatus", "Machine"], "Product Description": ["A handy contraption", "A useful device", "An apparatus", None, "A powerful machine"], "Stock Quantity": [None, 80, 60, 120, 150]}),
            ("price_list_13.csv", {"Product Item Code": ["P036", "P037", None, "P039", "P040"], "Product Price": [20.00, None, 29.50, None, 42.00], "Product Name": ["Widget", "Gadget", "Doodad", "Thingamajig", None], "Product Description": ["Useful widget", None, "An interesting doodad", "A thingamajig", "A unique gadget"], "Stock Quantity": [100, 50, None, 75, 200]}),
            ("price_list_14.xlsx", {"Product Item Code": [None, "P042", "P043", None, "P045"], "Product Price": [30.00, 35.00, None, 40.75, None], "Product Name": ["Contraption", "Device", None, "Apparatus", "Machine"], "Product Description": ["A handy contraption", "A useful device", "An apparatus", None, "A powerful machine"], "Stock Quantity": [None, 80, 60, 120, 150]})
        ]

        for file_name, data in data_sets:
            df = pd.DataFrame(data)
            if file_name.endswith('.csv'):
                df.to_csv(file_name, index=False)
            elif file_name.endswith('.xlsx'):
                df.to_excel(file_name, index=False)

    def tearDown(self):
        # Clean up test files
        files_to_remove = [
            'price_list_1.csv', 'price_list_2.xlsx', 'price_list_3.pdf', 'price_list_4.pdf', 
            'price_list_3.csv', 'price_list_4.xlsx', 'price_list_5.csv', 'price_list_6.xlsx', 
            'price_list_7.csv', 'price_list_8.xlsx', 'price_list_9.csv', 'price_list_10.xlsx', 
            'price_list_11.csv', 'price_list_12.xlsx', 'price_list_13.csv', 'price_list_14.xlsx', 
            'price_list_15.pdf', 'price_list_16.pdf'
        ]
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)

    def test_compare_price_lists(self):
        test_cases = [
    ('price_list_1.csv', 'price_list_2.xlsx', ['P003'], ['P006', 'P007'], ['P001', 'P005']),
    ('price_list_3.csv', 'price_list_4.xlsx', [], ['P013', 'P014', 'P015', 'P016'], ['P008', 'P009', 'P010', 'P012']),
    ('price_list_5.csv', 'price_list_6.xlsx', [], ['P022', 'P023', 'P024', 'P025'], ['P017', 'P019', 'P020', 'P021']),
    ('price_list_7.csv', 'price_list_8.xlsx', [], ['P031', 'P033', 'P034', 'P035'], ['P026', 'P027', 'P028', 'P030']),
    ('price_list_9.csv', 'price_list_10.xlsx', [], ['P042', 'P043', 'P045'], ['P036', 'P037', 'P039', 'P040']),
    ('price_list_11.csv', 'price_list_12.xlsx', [], ['P042', 'P043', 'P045'], ['P036', 'P037', 'P039', 'P040']),
    ('price_list_13.csv', 'price_list_14.xlsx', [], ['P042', 'P043', 'P045'], ['P036', 'P037', 'P039', 'P040']),
    ('price_list_15.pdf', 'price_list_16.pdf', [], ['P042', 'P043', 'P045'], ['P036', 'P037', 'P039', 'P040'])
]


        total_tests = 0
        passed_tests = 0

        for file1, file2, expected_changed, expected_new, expected_obsolete in test_cases:
           changed_prices, new_products, obsolete_products = compare_price_lists(file1, file2)
    
          # Check changed prices
           for expected_price in expected_changed:
              total_tests += 1
              if isinstance(expected_price, str) and expected_price in changed_prices:
                 passed_tests += 1
           for actual_price in changed_prices:
              total_tests += 1
              if actual_price in expected_changed:
                 passed_tests += 1
    
          # Check new products
           for expected_product in expected_new:
              total_tests += 1
              if expected_product in new_products:
                 passed_tests += 1
           for actual_product in new_products:
              total_tests += 1
              if actual_product in expected_new:
                 passed_tests += 1
    
          # Check obsolete products
           for expected_product in expected_obsolete:
              total_tests += 1
              if expected_product in obsolete_products:
                 passed_tests += 1
           for actual_product in obsolete_products:
               total_tests += 1
               if actual_product in expected_obsolete:
                  passed_tests += 1

        accuracy_percentage = (passed_tests / total_tests) * 100
        print(f"Accuracy of ChatGPT prompt with cleaning rules: {accuracy_percentage:.2f}%")

if __name__ == '__main__':
    unittest.main()
