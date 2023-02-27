"""
Function to create report of Rustans data
"""
import os
import pandas as pd

def read_raw_files(dir_path="../../data/raw/Mark/Rustans/Raw Data/"):
    """
    Function to read raw datasets
    """
    files = []
    for (dir_path, dir_names, file_names) in os.walk(dir_path):
        files.extend(file_names)

    files = [dir_path + elem for elem in file_names]
    inventory = [elem for elem in files if "inventory" in elem]
    offtake = [elem for elem in files if "offtake" in elem]

    df_inventory = pd.DataFrame()
    for elem in inventory:
        df_file = pd.read_excel(elem, header=16)
        print(df_file)
        df_inventory = df_inventory.append(df_file, ignore_index=True)
        print(df_inventory)

    df_offtake = pd.DataFrame()
    for elem in offtake:
        df_sales = pd.read_excel(elem, header=18)
        df_offtake = df_offtake.append(df_sales, ignore_index=True)

    return df_offtake, df_inventory

def main():
    """
    Main function
    """
    df_offtake, df_inventory = read_raw_files()
    print(df_offtake)

main()
