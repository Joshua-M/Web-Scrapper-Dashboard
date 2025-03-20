import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
import time

# Set up Streamlit page
st.set_page_config(page_title="Web Scraper Dashboard", layout="wide")
st.title("📊 Automated Web Scraper for Market Research")

# Sidebar Inputs
st.sidebar.header("🔍 Configure Web Scraping")
url = st.sidebar.text_input("Enter Website URL (e.g., Amazon, eBay, etc.)")
tag = st.sidebar.text_input("Enter HTML Tag (e.g., div, span, p)", value="div")
class_name = st.sidebar.text_input("Enter Class Name (if applicable)")
num_pages = st.sidebar.slider("Number of Pages to Scrape", 1, 10, 1)

# Scraping Function
def scrape_data(url, tag, class_name, num_pages):
    scraped_data = []
    for page in range(1, num_pages + 1):
        page_url = f"{url}?page={page}" if "?page=" not in url else url
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code != 200:
            st.error(f"Failed to retrieve data from {page_url}")
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.find_all(tag, class_=class_name) if class_name else soup.find_all(tag)
        
        for element in elements:
            scraped_data.append(element.text.strip())
        
        time.sleep(2)  # Avoid rate limiting
    
    return scraped_data

# Run Scraper
if st.sidebar.button("Start Scraping"):
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("Scraping data..."):
            data = scrape_data(url, tag, class_name, num_pages)
            if data:
                df = pd.DataFrame(data, columns=["Extracted Data"])
                st.success(f"Scraped {len(df)} items successfully!")
                
                # Display Table
                st.subheader("📋 Scraped Data")
                st.dataframe(df)
                
                # Word Frequency Analysis
                st.subheader("📊 Word Frequency Analysis")
                word_series = pd.Series(" ".join(data).split()).value_counts().reset_index()
                word_series.columns = ["Word", "Frequency"]
                fig = px.bar(word_series.head(20), x="Word", y="Frequency", title="Top 20 Most Frequent Words")
                st.plotly_chart(fig, use_container_width=True)
                
                # Download Data
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Data as CSV", data=csv, file_name="scraped_data.csv", mime="text/csv")
