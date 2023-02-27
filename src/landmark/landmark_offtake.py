"""
Function to read landmark offtake
"""
import numpy as np
import pandas as pd

def replace_values(list_dates):
    """
    Function to replace row value with prior row value
    """
    new_list=[]
    date = ""
    for elem in list_dates:
        elem = str(elem)
        if elem == "Unnamed: 0":
            new_list.append("date")
        elif elem == "Unnamed: 1":
            new_list.append("config")
        elif "DATE" in elem:
            elem = elem.replace(",", " ").replace(".", " ").split(":")[-1]
            date = elem
            new_list.append(elem)
        else:
            new_list.append(date)
    return new_list

def standardize_format(df_data, index_name):
    """
    convert raw dataset to standard format
    """
    df_data = df_data.T.reset_index().rename(columns={'index':'date'})
    list_dates = df_data['date'].values.tolist()
    df_data['date'] = replace_values(list_dates)
    df_data.columns = df_data.iloc[0]
    df_data = df_data[1:]
    # df_data = df_data[df_data["date"].str.contains(' ')]

    df_data = df_data[df_data["date"].str.len()>4]
    # df_data.to_csv("data.csv")
    df_data = df_data.dropna(how='all').reset_index(drop=True)
    old_cols = list(df_data.columns)
    if old_cols[2] is not None:
        df_data.columns = old_cols[:2] + ["empty_col"] + old_cols[3:]
        df_data.index.names = [index_name]
    else:
        print("Error")
        print(old_cols[2])

    return df_data

def read_raw_files(path="../../data/raw/AJ/Landmark/LAND MARK OFFTAKE.xlsx"):
    """
    Function to read raw landmark files
    """
    bgc_sheet = "LANDMARK BGC"
    df_bgc = pd.read_excel(path, sheet_name=bgc_sheet, header=2)
    df_bgc = standardize_format(df_bgc, "bgc")

    trinoma_sheet = "LANDMARK TRINOMA"
    df_trinoma = pd.read_excel(path, sheet_name=trinoma_sheet, header=2)
    df_trinoma = standardize_format(df_trinoma, "trinoma")

    makati_sheet = "LANDMARK MAKATI"
    df_makati = pd.read_excel(path, sheet_name=makati_sheet, header=2)
    df_makati = standardize_format(df_makati, "makati")

    starosa_sheet = "LANDMARK STAROSA"
    df_starosa = pd.read_excel(path, sheet_name=starosa_sheet, header=2)
    df_starosa = standardize_format(df_starosa, "starosa")
    return df_bgc, df_trinoma, df_makati, df_starosa

def test_columns_count(list_cols):
    """
    Function to check if there are duplicate columns in df
    """
    df_test = pd.DataFrame(list(list_cols), columns=['cols'])
    df_test = pd.DataFrame(df_test.groupby(['cols'])['cols'].count())
    df_test.columns = ['count']
    result = df_test[df_test['count']>1]
    assert result.empty

def myfunc(row, n_datasets=4):
    #sample function
    return row.astype('int32')/n_datasets

def main():
    """
    Main function
    """
    datasets = read_raw_files()
    len_datasets = len(datasets)
    # Sheets have different products.. can't append info
    # print(df_bgc.columns == df_trinoma.columns)
    for data in datasets:
        test_columns_count(data.columns)

    try:
        df_concat = pd.concat(datasets, ignore_index=True, sort=True)
    except:
        print("Error caused because duplicate column names in dataset")
        print("Possibly 2 products pasted in 2 different rows")

    df_sum_concat = df_concat.groupby(['date', 'ITEM DESCRIPTION']).sum()
    groupby_cols = df_sum_concat.columns
    df_sum_concat = df_sum_concat.reset_index()
    mask = df_sum_concat['ITEM DESCRIPTION']=='CS CONFIG'
    df_sum_concat.loc[mask, groupby_cols] = (df_sum_concat[mask]
                                             .apply(lambda row:
                                                    myfunc(row[groupby_cols],
                                                           len_datasets),
                                                    axis=1))
    df_sum_concat = df_sum_concat.drop([0, np.nan,"empty_col"], axis=1)
    #print(df_sum_concat.columns)
    df_sum_concat = df_sum_concat.set_index(['date', 'ITEM DESCRIPTION']).T
    cols = list(df_sum_concat.columns)
    order = cols[-1:] + cols[:-1]
    print(order)

    df_sum_concat[order].to_excel("../../data/processed/landmark.xlsx")

main()
