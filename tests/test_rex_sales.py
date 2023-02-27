"""
Function to test files
"""
import os
import sys
import pandas as pd
sys.path.insert(0, "../src/rex_sales")
from rex_sales_analysis import location_mapping_columns, stores_columns, sales_columns

def test_location_mapping_columns():
    """
    Function containing columns names needed from location mapping file
    """
    results = location_mapping_columns()
    expected = ['Cluster', 'City/Province', 'Region', 'NCR City']
    assert expected == results

def check_711_mapping_file_exists():
    """
    Function to check if mapping files exist w/ desired columns
    """
    path = '../data/raw/REX/7-Eleven/Reports/1) 711 OFFTAKE 2022 binary.xlsb'
    sheet = "Detailed Sales Offtake"
    file_exists = os.path.isfile(path)
    df_columns = pd.read_excel(path, sheet_name=sheet, header=3).columns.tolist()
    needed_columns = location_mapping_columns()
    results = set(needed_columns).issubset(set(df_columns))
    assert file_exists is True
    assert results is True

def test_stores_columns():
    """
    Columns desired from stores raw dataset
    """
    expected = ['Store', 'Storename', 'Cluster', 'City/Province', 'District']
    results = stores_columns()
    assert expected == results

def test_sales_columns():
    """
    Columns desired from stores raw dataset
    """
    expected = ['store_code', 'store_name', 'item_code', 'long_name', 'quantity',
                'transactiondate', 'amount']
    results = sales_columns()
    assert expected == results

def check_711_raw_files_exist():
    """
    Function to check if raw files exist and contain desired columns
    """
    sales = "../data/raw/REX/7-Eleven/Raw Data/Raw_Sales Data.xls"
    stores = "../data/raw/REX/7-Eleven/Raw Data/Raw_StoreList.xls"
    sales_file_exists = os.path.isfile(sales)
    stores_file_exists = os.path.isfile(stores)
    column_sales = pd.read_excel(sales).columns.tolist()
    sales_needed_columns = sales_columns()
    sales_results = set(sales_needed_columns).issubset(set(column_sales))
    column_stores = pd.read_excel(stores, header=2).columns.tolist()
    stores_needed_columns = stores_columns()
    stores_results = set(stores_needed_columns).issubset(set(column_stores))
    assert sales_file_exists is True
    assert stores_file_exists is True
    assert sales_results is True
    assert stores_results is True

test_location_mapping_columns()
check_711_mapping_file_exists()
test_stores_columns()
test_sales_columns()
check_711_raw_files_exist()
