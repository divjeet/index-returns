import streamlit as st
import requests
import openpyxl
from datetime import datetime
import pandas as pd
from st_pages import Page, Section, show_pages, add_page_title

def fetch_data():
    url = "https://www.ndtvprofit.com/feapi/markets/historical-returns/all"
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        annualization_factors = {f"{i}Y": i for i in range(2, 11)}
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        headers = ["Index", "1M", "3M", "YTD", "1Y", "2Y", "3Y", "4Y", "5Y", "10Y"]
        worksheet.append(headers)
        excluded_entries = {"", "-", "NIFTYTR2X", "NIFTYPR2X", "NIFTYTR1X", "NIFTYPR1X"}

        for entry in json_data['data']:
            if entry["name"] in excluded_entries:
                continue

            row_data = [entry["name"]]

            for period in ["1M", "3M", "YTD", "1Y"]:
                if period in entry["returns"]:
                    row_data.append(round(entry["returns"][period], 0))
                else:
                    row_data.append(None)

            for year in ["2Y", "3Y", "4Y", "5Y", "10Y"]:
                if year in annualization_factors and year in entry["returns"] and entry["returns"][year] != 'NA':
                    row_data.append(round(float(entry["returns"][year]) / annualization_factors[year], 0))
                else:
                    row_data.append(None)

            worksheet.append(row_data)

        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f'output_annual_ret_{today_date}_M_Y.xlsx'
        workbook.save(filename)
        
        # Streamlit App
        st.set_page_config(page_title='Index Returns' , page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items={"About": 'Text'})

        st.header('Index Returns Anualised:')

        st.write(f"Data has been successfully fetched, processed, and saved to {filename}.")
            
        # Optional -- adds the title and icon to the current page
        #add_page_title()

        # Specify what pages should be shown in the sidebar, and what their titles and icons
        # should be
        show_pages(
            [
                Page("Hello.py", "Index Returns"),
                Page("pages/0_about.py", "About"),
            ]
        )

        # Create a data table from the worksheet
        data = worksheet.values
        columns = next(data)
        df = pd.DataFrame(data, columns=columns)

        # Remove decimals from the dataframe
        df = df.astype(str).replace('\.0', '', regex=True)

        # Display the data table
        st.table(df)

        # Add a download button for the file
        st.download_button("Download Excel File", filename)
        
        st.text('''For Indepth analysis of Nse Indexes Check out the link Below !''')
        st.write("https://allindexanalysis.streamlit.app",unsafe_allow_html=True)

    else:
        st.write(f"Failed to fetch data. Status code: {response.status_code}")
        
        st.text('''For Indepth analysis of Nse Indexes Check out the link Below !''')
        st.write("https://allindexanalysis.streamlit.app",unsafe_allow_html=True)

# Fetch data when the app starts
fetch_data()





