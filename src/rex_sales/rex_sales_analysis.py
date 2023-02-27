"""
Function to leverage raw 7-eleven datasets and automatically create replica of sample report
Inputs: Raw_Sales Data.xlsb
        Raw_StoreList.xls
Output: "Analysis" page
"""
import numpy as np
import pandas as pd

def stores_columns():
    """
    Columns desired from stores raw dataset
    """
    return ['Store', 'Storename', 'Cluster', 'City/Province', 'District',
            'Dateopened', 'Address']

def all_sales_columns():
    """
    All the columns of sales
    """
    cols = ["supplier_code", "supplier_name", "store_code"
            "item_code", "long_name", "transactiondate", "quantity", "amount"]
    return cols

def sales_columns():
    """
    Columns desired from stores raw dataset
    """
    return ['store_code', 'store_name', 'item_code', 'long_name', 'quantity',
            'transactiondate', 'amount']

def detailed_sales_offtake_fields():
    """
    Fields asked for detailed sales offtake file
    """
    lst = ["AccountName", "store_code", "store_name", "District", "Dateopened",
           "Address", "City/Province", "Cluster", "offtakes" , "long_name",
           "year", "month", "sales_price", "list_sales_price", "amount"]

    return lst

def create_pivot_table(df_raw, x_cols, y_cols, v_col):
    """
    function to create pivot table of month sales
    """
    df_pivot = pd.pivot_table(df_raw, values=v_col, index=x_cols,
                              columns=y_cols, aggfunc="count")
    return df_pivot

def concat_sales_file(dict_df_sales, sales_cols):
    """
    Function to concat the dictionary of sales
    """
    df_sales = pd.DataFrame([], columns=sales_cols)
    for key in dict_df_sales.keys():
        df_new = pd.DataFrame(dict_df_sales[key])
        df_sales = pd.concat([df_sales, df_new], ignore_index=True)
    return df_sales

def split_by_month(df_raw, column, delim):
    """
    Function to read string date and split to new columns

    Output: df with new columns, list of years & list of months
    """
    df_raw[['year', 'month', 'day']] = df_raw[column].str.split(delim, expand=True)
    lst_year = df_raw['year'].values.tolist()
    lst_month = df_raw['month'].values.tolist()
    return df_raw, lst_year, lst_month

def join_mappings(sales = "../../data/raw/REX/7-Eleven/Raw Data/Raw_Sales Data.xls",
                  stores = "../../data/raw/REX/7-Eleven/Raw Data/stores.xlsx"):
    """
    Function to join both sales & store location raw datasets
    """
    sales_needed_columns = sales_columns()
    all_sales_cols = all_sales_columns()
    # Read all sheets and concat to one another
    sales_data = pd.read_excel(sales, sheet_name=None)
    df_sales = concat_sales_file(sales_data, all_sales_cols)
    df_sales = df_sales[sales_needed_columns]
    # split string data to multiple columns
    df_sales[['year', 'month', 'day']] = (df_sales['transactiondate'].str
                                          .split(pat="-", expand=True))

    # p tables are replaced by groupby but creating ptable for viewing
    # p_sales = create_pivot_table(df_sales, ["store_code", "store_name", "year", "month"],
    #                              ["long_name"], "amount")
    # p_sales.to_excel("../../data/interim/p_file.xlsx")
    ### Disclaimer: if price changes that month then salesprice is max & amount is skewed
    df_sales['sales_price'] = df_sales['amount'] / df_sales['quantity']
    df_sales['list_sales_price'] = df_sales['amount'] / df_sales['quantity']
    lst_groupby_cols = ["store_code", "store_name", "year", "month", "long_name"]
    df_groupby = (df_sales.groupby(lst_groupby_cols)
                  .agg({'amount':'sum', 'list_sales_price':'unique',
                        'sales_price':'max', 'quantity':'sum'})
                  .reset_index().rename(columns={"quantity": "offtakes"}))
    df_groupby.to_excel("../../data/interim/df_groupby.xlsx")

    df_stores = (pd.read_excel(stores).reset_index()
                 .rename(columns={"Storename": "store_name",
                                  "Store":"store_code"}))
    df_stores['AccountName'] = "7-11"

    df_results = (df_groupby.merge(df_stores, suffixes=('_sales','_stores'),
                                   how='outer', on=['store_code', 'store_name']))

    df_results = sales_offtake_details(df_results[detailed_sales_offtake_fields()])

    return df_results

def sales_offtake_details(df_raw):
    """
    Additional details regarding sales are created here
    """
    print(df_ra.columns)
    df_item = (df_raw.groupby("long_name").agg({"amount":"sum", "offtakes":"sum"})
               .rename(columns={"amount": "sku_total_sales",
                                "offtakes":"sku_total_offtakes"}))

    df_item['grand_total_all_skus'] = df_item["sku_total_sales"].sum()
    df_item['offtakes_all_skus'] = df_item["sku_total_offtakes"].sum()
    print(df_raw.columns)

    df_avg = (df_raw.groupby(["year", "month"]).agg({"amount":"sum", "offtakes":"sum"})
              .rename(columns={"amount": "avg_month_sales",
                               "offtakes":"avg_offtake_sales"}))
    df_avg["avg_month_sales"] = df_avg['avg_month_sales'] / 30
    df_avg["avg_offtake_sales"] = df_avg['avg_offtake_sales'] / 30
    df_avg['total_sales_avg'] = df_avg["avg_month_sales"].sum()
    df_avg['total_offtakes_avg'] = df_avg["avg_offtake_sales"].sum()

    df_results = (df_raw.merge(df_item, suffixes=('_raw','_item'),
                                 how='outer', on=["long_name"]))

    df_results = (df_results.merge(df_avg, suffixes=('_raw','_avg'),
                                 how='outer', on=["year", "month"]))

    df_results.to_excel("../../data/interim/Detailed_Sales_Offtake.xlsx", index=False)

    return df_results

def create_analysis_sheet(df_data, path="../../data/processed/analysis_711.xlsx"):
    """
    Function for creating report analysis excel sheet
    """
    df_month_volume = (df_data.groupby(['year', 'month']).agg({'offtakes':'sum'})
                       .rename(columns={"offtakes": "total_month_volume"}))
    # Based on cluster
    ### Cluster_candycorner or Cluster_711
    df_cluster = (df_data.groupby(['Cluster', 'year', 'month'])
                  .agg({'offtakes':'sum', 'store_code':'nunique'})).reset_index()
    df_cluster = df_cluster.merge(df_month_volume, on=['month', 'year'])
    df_cluster["Share %"] = (df_cluster['offtakes'] / df_cluster['total_month_volume']) * 100
    df_cluster = (df_cluster.groupby(['Cluster', 'year', 'month'])
                  .agg({'offtakes':'max', 'store_code':'max', 'total_month_volume': 'max',
                        'Share %':'max'}))

    # Based on candy corner defined city
    df_city = (df_data.groupby(['District', 'City/Province', 'year', 'month'])
               .agg({'offtakes':'sum', 'store_code':'nunique'})).reset_index()
    df_city = df_city.merge(df_month_volume, on=['month', 'year'])
    df_city["Share %"] = (df_city['offtakes'] / df_city['total_month_volume']) * 100
    df_city = (df_city.groupby(['District', 'City/Province', 'year', 'month'])
               .agg({'offtakes':'max', 'store_code':'max', 'total_month_volume':'max',
                     'Share %':'max'}))

    # Based on candy corner defined city
    df_district = (df_data.groupby(['District', 'year', 'month'])
               .agg({'offtakes':'sum', 'store_code':'nunique'})).reset_index()
    df_district = df_district.merge(df_month_volume, on=['month', 'year'])
    df_district["Share %"] = (df_district['offtakes'] / df_district['total_month_volume']) * 100
    df_district = (df_district.groupby(['District', 'year', 'month'])
                   .agg({'offtakes':'max', 'store_code':'max', 'total_month_volume':'max',
                         'Share %':'max'}))

    # Avg selling colume per SKU
    df_sku = (df_data.groupby(['long_name', 'year', 'month'])
              .agg({'offtakes':['sum', 'mean'], 'store_code':'nunique'}))
    df_sku.columns = ['offtakes_sum', 'offtakes_avg', 'unique_stores']

    ###  assume each month is 30 days
    days_in_month = 30
    df_sku['avg_offtakes_district'] = df_sku['offtakes_sum'] / df_sku['unique_stores']
    df_sku['offtakes_month_avg'] = df_sku['offtakes_sum'] / days_in_month
    df_sku['0'] = np.where((df_sku['offtakes_month_avg'] >= 0) &
                           (df_sku['offtakes_month_avg'] < 0.01), 1, 0)
    df_sku['0.01'] = np.where((df_sku['offtakes_month_avg'] >= 0.01) &
                           (df_sku['offtakes_month_avg'] < 1), 1, 0)
    df_sku['1'] = np.where((df_sku['offtakes_month_avg'] >= 1) &
                           (df_sku['offtakes_month_avg'] < 2), 1, 0)
    df_sku['2'] = np.where((df_sku['offtakes_month_avg'] >= 2) &
                           (df_sku['offtakes_month_avg'] < 3), 1, 0)
    df_sku['3'] = np.where((df_sku['offtakes_month_avg'] >= 3 ) &
                            (df_sku['offtakes_month_avg'] < 4), 1, 0)
    df_sku['4'] = np.where((df_sku['offtakes_month_avg'] >= 4) &
                            (df_sku['offtakes_month_avg'] < 5), 1, 0)
    df_sku['5'] = np.where((df_sku['offtakes_month_avg'] >= 5), 1, 0)
    df_sku['20'] = np.where((df_sku['offtakes_month_avg'] >= 20), 1, 0)

    # Count SKUs meeting range
    df_month_ranges = (df_sku.reset_index().groupby(['year', 'month'])
                       .agg({'0':'sum', '0.01':'sum', '1':'sum', '2':'sum', '3':'sum',
                             '4':'sum', '5':'sum', '20':'sum'}))

    # Create excel file
    with pd.ExcelWriter(path) as writer:
        df_cluster.to_excel(writer, sheet_name="cluster_volume")
        df_city.to_excel(writer, sheet_name="city_volume")
        df_district.to_excel(writer, sheet_name="district_volume")
        df_sku.to_excel(writer, sheet_name="sku_offtakes")
        df_month_ranges.to_excel(writer, sheet_name="sku_month_ranges")

def summary_report_711(df_data, path="../../data/processed/summary_711.xlsx"):
    """
    Function to develop summary report of 711 offtakes
    """
    df_branches = df_data.groupby(['year', 'month']).agg({'store_code':'nunique'})
    df_sku = (df_data.groupby(['long_name', 'year', 'month'])
              .agg({'offtakes':'sum', 'store_code':'nunique'}))

    # Average sku per month
    df_month_avg = df_sku.reset_index().copy()

    ###  assume each month is 30 days
    df_month_avg['avg_offtake'] = df_month_avg['offtakes'] / df_month_avg['store_code']
    df_month_avg = (df_month_avg.groupby(['long_name', 'year', 'month'])
                    .agg({'avg_offtake':'max'}))

    with pd.ExcelWriter(path) as writer:
        df_branches.to_excel(writer, sheet_name="branches_w_offtake")
        df_sku.to_excel(writer, sheet_name="offtake_per_sku")
        df_month_avg.to_excel(writer, sheet_name="sku_avg_offtake")

def main():
    """
    Main function of script
    """
    df_mapping = join_mappings()
    # stores = df_mapping[df_mapping['Cluster']=='HOSPITAL']['store_code'].values.tolist()
    # path = "../../data/raw/REX/7-Eleven/Raw Data/sales.xls"
    # df_rj = pd.read_excel(path)
    # stores_2 = df_rj[(df_rj.Cluster == 'HOSPITAL')]['store_code'].values.tolist()
    # diff = set(stores) - set(stores_2)
    # print(diff)
    # diff = set(stores_2) - set(stores)
    # print(diff)
    create_analysis_sheet(df_mapping)
    summary_report_711(df_mapping)

main()
