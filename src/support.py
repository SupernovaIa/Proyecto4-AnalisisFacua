import os
import json
import dotenv
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from bs4 import BeautifulSoup

import psycopg2
from psycopg2 import OperationalError, errorcodes

# Load environment variables from .env file
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv('token')

# 01 - Scraping

def get_soup(url: str):
    """
    Fetches and parses HTML content from a specified URL using BeautifulSoup.

    Parameters:
    - url (str): The URL from which to retrieve the HTML content.

    Returns:
    - (BeautifulSoup | None): Parsed HTML content as a BeautifulSoup object if the request is successful; otherwise, None.
    """
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    else:
        print(f"Error. Response code {response.status_code}")


def find_urls(soup: BeautifulSoup):
    """
    Extracts product names and URLs from a BeautifulSoup object containing structured HTML content.

    Parameters:
    - soup (BeautifulSoup): A BeautifulSoup object containing the parsed HTML content.

    Returns:
    - (list of dict): A list of dictionaries, each containing:
    - 'name' (str): The product name extracted from the HTML.
    - 'link' (str): The URL associated with the product.
    
    Each dictionary represents a product found within elements matching the specified structure. In case of missing data, an error is logged and that item is skipped.
    """

    items = soup.findAll('div', {'class': 'card h-100'})
    product_list = []

    for item in items:
        try:
            product_list.append({'name': item.find('p', {'class': 'fw-bolder'}).text, 
                                'link': item.find("a").get('href')}) 
        except Exception as e:
            print(f'Error {e}') 

    return product_list


def table_extraction(url: str):
    """
    Extracts data from the last HTML table in a specified URL and returns it as a pandas DataFrame.

    Parameters:
    - url (str): The URL from which to retrieve and parse HTML table data.

    Returns:
    - (pd.DataFrame): A DataFrame containing the extracted table data, with each column representing a table heading and rows containing respective values. An additional column 'url' stores the URL source of the data.
    """

    soup = get_soup(url)
    # Extract table from the soup
    table = soup.findAll('table')[-1] # The last table since there might be other tables above
    # Extract row from the table
    rows = table.findAll('tr')

    # List of list of lenght number of headings (columns)
    table_list = [ [] for _ in table.findAll('th')]

    for row in rows[1:]:
        data = row.findAll('td')

        for i in range(len(table_list)):
            table_list[i].append(data[i].text)

    df = pd.DataFrame(table_list).T
    df['url'] = url
    
    return df


def clean_df(df: pd.DataFrame, market: str, cat: str):
    """
    Cleans and formats a DataFrame containing price data, adding metadata for supermarket and product category.

    Parameters:
    - df (pd.DataFrame): DataFrame containing raw data with columns for date, price, and price delta.
    - market (str): Name of the supermarket, added as a column to the DataFrame.
    - cat (str): Product category, added as a column to the DataFrame.

    Returns:
    - (pd.DataFrame): A cleaned and formatted DataFrame with:
    - 'Date' column as datetime objects.
    - 'Price (€)' column converted to float.
    - 'Delta Price' column with gross difference as string.
    - Additional columns 'supermarket' and 'category' with provided metadata.
    """
    # Rename columns
    df = df.rename(columns={0: 'Date', 1: 'Price (€)', 2: 'Delta Price'})
    # Clean price
    df['Price (€)'] = df['Price (€)'].str.replace(',','.').astype(float)

    # Convert date
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")

    # Clean Delta price (get only gross difference)
    df['Delta Price'] = df['Delta Price'].str.replace('=', '0 (0%)').str.replace(',', '.').str.split(' ', expand=True)[0]

    # Clean <'>, <"> symbols
    df['product'] = df['product'].str.replace("'", "").str.replace('"', '')
    # Add supermarket and category columns
    df['supermarket'] = market
    df['category'] = cat

    return df


def scrap_market_category(market: str, cat: str):
    """
    Scrapes product data for a specified supermarket and category, consolidating it into a cleaned DataFrame with historical pricing information.

    Parameters:
    - market (str): The identifier of the supermarket to scrape data from.
    - cat (str): The product category within the supermarket to target for data extraction.

    Returns:
    - (pd.DataFrame): A cleaned DataFrame containing historical data for products in the specified market and category, with columns for product name, date, price, delta price, supermarket, and category.
    
    The function constructs a URL based on the supermarket and category, extracts individual product URLs, retrieves and parses data tables from each product page, and aggregates the data into a unified DataFrame.
    """
    # We define the url considering market and category
    url = f'https://super.facua.org/{market}/{cat}/'

    # Cook the soup and extract all the product url and names
    soup = get_soup(url)
    products = find_urls(soup)

    # Empty list to store dataframes
    list_df = []

    # For each product extract the table and build a dataframe
    for product in tqdm(products):
        try:
            df = table_extraction(product['link'])
            df['product'] = product['name']
            list_df.append(df)
        except:
            pass

    df_historic = pd.concat(list_df)
    df_historic = clean_df(df_historic, market, cat)

    return df_historic


def bulk_scraping(supermarkets: list, categories: list):
    """
    Performs bulk scraping across multiple supermarkets and categories, consolidating the data into a single DataFrame.

    Parameters:
    - supermarkets (list of str): A list of supermarket identifiers to scrape data from.
    - categories (list of str): A list of product categories to target for each supermarket.

    Returns:
    - (pd.DataFrame): A concatenated DataFrame containing data from all specified supermarkets and categories, with columns for product name, date, price, delta price, supermarket, and category.
    
    The function iterates over each supermarket-category combination, scraping and processing data for each, then merges all resulting DataFrames.
    """

    df_list = []

    for sprmkt in supermarkets:

        for cat in categories:
            print(f'Scraping {cat} category in {sprmkt} supermarket')
            df_list.append(scrap_market_category(sprmkt, cat))
            # Clear console
            os.system('cls' if os.name == 'nt' else 'clear')

    df = pd.concat(df_list)
    return df


def extract_info_ai(prod: str):
    """
    Generates a structured JSON response with product details extracted from a given product description.

    The function sends a product description to a chat-based language model, which returns a JSON object with specific fields: "category", "subcategory", "brand", "volume", "weight", and "details". If a field is not present in the description, it is marked as `null`. The "category" field has restricted values, and unit conversions are applied for weight (grams) and volume (liters) if necessary. The function parses the JSON response and returns it as a dictionary.

    Parameters:
    - prod (str): Description of the product to be parsed.
 
    Returns:
    - (dict): Parsed JSON containing structured product details, or an error message if JSON decoding fails.
    """

    prompt = 'Para cada nombre de producto que recibas devolverás un JSON con los siguientes campos: "category", "subcategory", "brand", "volume", "weight", "details". Si alguno de los valores no está presente, debes marcarlo como null (sin comillas). "category" solo puede ser "leche", "aceite_oliva" o "aceite_girasol"; si no corresponde con ninguno de estos, debe ser null. El resto de campos deberán ir en minúsculas y sin abreviaturas. "weight" siempre será en gramos y "volume" en litros; realizarás las conversiones si es necesario. Devolverás únicamente el JSON en una sola línea sin saltos de línea, sin escribir nada adicional.\n\nEjemplo:\nProducto: Leche condensada desnatada Nestlé La Lechera sin lactosa 450 g.\nRespuesta:\n{"category": "leche", "subcategory": "condensada", "brand": "nestlé la lechera", "volume": null, "weight": 450, "details": "desnatada sin lactosa"}\nEjemplo 2:\nProducto: Aceite de oliva 0,4º CARBONELL, botella 1 litro\nRespuesta:\n{"category": "aceite_oliva", "subcategory": "0.4º", "brand": "carbonell", "volume": 1, "weight": null, "details": null}\nEjemplo 3:\nProducto: Leche Bruma Protectora Spf50 Broncea+ Ecran Sunnique 250 Ml.\nRespuesta:\n{"category": null, "subcategory": null, "brand": "ecran", "volume": 0.25, "weight": null, "details": "protector solar"}\nEjemplo 4:\nProducto: Aceite De Oliva 0,4º Carbonell, Garrafa 3 Litros\nRespuesta:\n{"category": "aceite_oliva", "subcategory": "0.4º", "brand": "carbonell", "volume": 3, "weight": null, "details": "garrafa"}'

    client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": prod}
        ]
    )
    
    try:
        return json.loads(completion.choices[0].message.content)
    
    except json.JSONDecodeError as e:
        print(e)

    
def change_id(df: pd.DataFrame, df_dict: pd.DataFrame, column: str):
    """
    Replaces the values in a specified column of a DataFrame with corresponding IDs from a reference dictionary DataFrame and renames the column.

    Parameters:
    - df (pd.DataFrame): The main DataFrame where values in the specified column will be changed to IDs.
    - df_dict (pd.DataFrame): A reference DataFrame containing mapping data with columns for values and their corresponding IDs.
    - column (str): The name of the column in both DataFrames that contains the values to be converted.

    Returns:
    - pd.DataFrame: The modified DataFrame with updated IDs and renamed column.
    """

    # Extract the id-value 
    values = df_dict[column].to_dict()
    ids = df_dict[f'{column}_id'].to_dict()
    # Build a ditionary
    dc = {values[i]: ids[i] for i in ids}
    # Convert values to ids and rename column
    df[column] = df[column].apply(lambda x: dc.get(x, np.nan))
    df.rename(columns={column: f'{column}_id'}, inplace=True)

    return df


# 02 - PostgreSQL Database

def table_creation(queries: list):
    """
    Creates tables in a PostgreSQL database by executing a series of SQL table creation queries.

    Parameters:
    - queries (list of str): List of SQL queries to execute, each defining a table structure.
    """
    # Set connection
    try:
        connection = psycopg2.connect(
            database='supermarkets',
            user='my_user',
            password='admin',
            host='localhost',
            port='5432'
        )

        # Queries execution
        with connection.cursor() as cursor:
            for query in queries:
                cursor.execute(query)
        
        # Commit the transaction
        connection.commit()
        print("Tables created successfully.")

    except OperationalError as e:
        if e.pgcode == errorcodes.INVALID_PASSWORD:
            print('Incorrect password')
        elif e.pgcode == errorcodes.CONNECTION_EXCEPTION:
            print('Connection error')
        elif e.pgcode == errorcodes.INVALID_CATALOG_NAME:
            print('Database does not exist')
        else:
            print(f"Database error: {e}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Ensure connection closure
        if connection:
            connection.close()
            print("Database connection closed.")


def data_insertion(query: str, values: list):
    """
    Inserts multiple rows of data into a PostgreSQL database based on a specified query and values.

    Parameters:
    - query (str): SQL query to execute, typically an INSERT statement with placeholders for data.
    - values (list of tuple): List of tuples containing values to insert, each tuple representing a row.
    """
    # Set connection
    try:
        connection = psycopg2.connect(
            database='supermarkets',
            user='my_user',
            password='admin',
            host='localhost',
            port='5432'
        )

        # Queries execution
        with connection.cursor() as cursor:
            cursor.executemany(query, values)
        
        # Commit the transaction
        connection.commit()
        print("Data inserted successfully.")

    except OperationalError as e:
        if e.pgcode == errorcodes.INVALID_PASSWORD:
            print('Incorrect password')
        elif e.pgcode == errorcodes.CONNECTION_EXCEPTION:
            print('Connection error')
        elif e.pgcode == errorcodes.INVALID_CATALOG_NAME:
            print('Database does not exist')
        else:
            print(f"Database error: {e}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Ensure connection closure
        if connection:
            connection.close()
            print("Database connection closed.")


def sql_query(query: str):
    """
    Executes a given SQL query on a PostgreSQL database and retrieves all results.

    Parameters:
    - query (str): The SQL query to be executed on the database.

    Returns:
    - result (list of tuples | None): A list of tuples containing the query results if the execution is successful, or `None` if an error occurs.
    """

    # Initialize result to avoid returning undefined variable
    result = None
    connection = None
    
    try:
        # Establish the connection
        connection = psycopg2.connect(
            database='supermarkets',
            user='my_user',
            password='admin',
            host='localhost',
            port='5432'
        )

        # Query execution
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        
        print("Query performed successfully.")

    except OperationalError as e:
        if e.pgcode == errorcodes.INVALID_PASSWORD:
            print('Incorrect password')
        elif e.pgcode == errorcodes.CONNECTION_EXCEPTION:
            print('Connection error')
        elif e.pgcode == errorcodes.INVALID_CATALOG_NAME:
            print('Database does not exist')
        else:
            print(f"Database error: {e}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Closing connection
        if connection:
            try:
                connection.close()
                print("Database connection closed.")
            except Exception as e:
                print(f"Error closing connection: {e}")

    return result
