import pandas as pd

start_time="14:00"
soldout_time="15:29"
diff = 89

def read_file(file = "C:/Users/andre/OneDrive/Desktop/taylor_venues.xlsx"):
    """
    Function to read venues data
    """
    df_raw = pd.read_excel(file)
    return df_raw

def analyze(df_raw, allocation_presale=0.60):
    """
    """
    df_filter = df_raw[(df_raw['Selling_Platform']!="SeatGeek")]
    total_seats = df_raw['Capacity'].sum()
    print("Total seats all ticketmaster venues: %i" % total_seats)
    presale_tickets = total_seats*allocation_presale
    print("Presale ticketmaster: %i" % presale_tickets)
    tickets_day2= total_seats*(1-allocation_presale)
    print("Estimate tickets being sold day 2: %i" % tickets_day2)

    df_filter = df_raw[(df_raw['Selling_Platform']!="SeatGeek") &
                       (df_raw['Timezone']!="UTC-06:00")]

    total_capacity = df_filter['Capacity'].sum()
    print("Total Capacity of central timezone: %i" % total_capacity)

    tickets_day2= total_capacity*(1-allocation_presale)
    print("Estimate tickets being sold day 2 of central timezone: %i" % tickets_day2)

    users_per_minute = tickets_day2/diff
    print("Tickets sold per minute: %i" % users_per_minute)

    return df_filter

def main():
    df_raw = read_file()
    print(df_raw.columns)
    analyze(df_raw)

main()
