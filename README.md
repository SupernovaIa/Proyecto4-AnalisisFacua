# 🛒 Supermarket Price Analysis Project

![facua supermarkets](https://github.com/user-attachments/assets/94c04f0b-602a-484c-9889-73c542005257)

## 📜 Project Overview
This project aims to use data scraping, processing, and analysis tools to gather information on products and prices from various supermarkets in Spain. The primary data source is the **FACUA: Supermarket Prices** website. With the collected data, we create an SQL database, perform exploratory data analysis (EDA), and generate visualizations to uncover trends and price variability between supermarkets.

The FACUA website provides updated information on basic product prices across six major Spanish supermarkets: Alcampo, Carrefour, Dia, Eroski, Hipercor, and Mercadona. Users can compare prices for essential items like oil and milk, observe price changes over time, and see the latest significant price increases. The platform updates daily, allowing consumers to stay informed about price fluctuations and potential pricing issues.

### Specific Objectives
- **Data Scraping**: Extract detailed product information from the FACUA website for each listed supermarket.
- **Data Cleaning**: Clean and transform data properly. This is an AI-powered solution since we use **GPT-4o mini** to classify products based on their names. Given the inconsistent formatting of product names, traditional methods like regex are insufficient for accurate classification. The language model will help standardize and categorize the data efficiently.
- **Database Storage**: Create an SQL database to store the collected data in a structured manner.
- **Data Analysis**: Perform several analyses using Python and Pandas:
  - **Price Comparison Across Supermarkets**: Identify which supermarkets have the lowest or highest prices for each product.
  - **Price Trend Analysis**: Study how product prices have evolved over time across different supermarkets.
  - **Anomaly Detection**: Identify unusual price changes that may indicate price hikes or promotions.
  - **Price Dispersion Analysis**: Assess the variability in prices for the same product across different supermarkets.
  - **Average Price Comparison**: Calculate and compare average prices for each product across supermarkets.
- **Data Visualization**: Generate charts and visualizations to present the analysis results clearly and understandably.

## 💻 Project Structure
```plaintext
Proyecto4-AnalisisFacua
├── data/                               # Folder containing datasets
│   ├── categorias.csv                   # Categories of products
│   ├── historial.csv                    # Historical price data
│   ├── productos.csv                    # Product details
│   ├── supermercados.csv                # Supermarket information
├── notebooks/                          # Jupyter Notebooks for different project phases
│   ├── 01-scraping.ipynb                # Notebook for FACUA data scraping
│   ├── 02-database.ipynb                # Notebook for database creation and data loading
│   ├── 03-eda.ipynb                     # Notebook for exploratory data analysis
├── src/                                # Source code for project functions
│   ├── support.py                       # Python helper functions for data scraping and processing
├── .env                                # Environment variables file
├── .gitignore                          # Git ignore file
├── README.md                           # Project description and documentation
├── requirements.txt                    # Project dependencies
```

## 🔧 Installation and Requirements

This project was developed using **Python 3.12**. To set up the project environment, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/SupernovaIa/Proyecto4-AnalisisFacua 
   ```

2. Navigate to the project directory:
   ```bash
   cd Proyecto4-AnalisisFacua
   ```

3. Install the required libraries:
   The following libraries are needed for this project:

   - [**Matplotlib** (v3.9.2)](https://matplotlib.org/stable/contents.html): For data visualization and plotting.
   - [**Seaborn** (v0.13.2)](https://seaborn.pydata.org/): For statistical data visualization.
   - [**NumPy** (v1.26.4)](https://numpy.org/doc/stable/): For numerical data processing.
   - [**Pandas** (v2.2.2)](https://pandas.pydata.org/pandas-docs/stable/): For data manipulation and analysis.
   - [**psycopg2** (v2.9.10)](https://www.psycopg.org/docs/): To interact with PostgreSQL databases.
   - [**Beautiful Soup** (v4.12.3)](https://beautiful-soup-4.readthedocs.io/en/latest/): For parsing HTML and extracting information from web pages.
   - [**OpenAI** (v1.52.2)](https://platform.openai.com/docs/introduction): For accessing OpenAI API features.
   - [**python-dotenv** (v1.0.1)](https://saurabh-kumar.com/python-dotenv/): For loading environment variables from `.env` files.

   To install all dependencies, run:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Notebooks:
   Once the environment is set up, you can execute the Jupyter Notebooks in the specified order to perform data scraping, load data into SQL, and generate visual analyses.


## 📊 Results and Conclusions

The analysis of supermarket price data led to the following insights:

- **Focus on 1-liter format**: Products in the 1-liter format represent nearly half of our data, so our initial analysis is focused on this subset, leaving other formats for future stages.

- **Price comparison by product type**: We observed that a liter of olive oil is significantly more expensive than sunflower oil and milk across supermarkets. Among supermarkets:
  - `Mercadona` consistently offers the lowest prices across all product categories.
  - `Hipercor` and `Carrefour` tend to be the most expensive options.

- **Analysis of most recent day**: When we filtered the data to focus on the most recent day, the pricing trends remained consistent with the overall dataset, reinforcing the stability of our initial conclusions.

- **Influence of brand selection on price analysis**: Supermarkets carrying higher-priced brands can bias price comparisons. By analyzing only the cheapest products in each supermarket, we noticed:
  - Prices for sunflower oil are relatively aligned across supermarkets, though `Alcampo` offers the lowest price for milk.
  - For olive oil, `Hipercor` and `Mercadona` appear significantly more expensive. However, this is because the cheapest option at other supermarkets is olive pomace oil, which has a lower value compared to pure olive oil. To ensure a fair comparison, we focused on extra virgin olive oil (`AOVE`).

- **Extra virgin olive oil comparison**: When isolating extra virgin olive oil, we found that prices are more similar across supermarkets, with `Hipercor` offering the lowest average, about 30 cents less than others.

- **Price trends over time**: Over a 4-month period, we observed steady price trends without significant fluctuations, though extended monitoring may be needed for clearer trend identification.
  - **Sunflower oil**: `Alcampo` initially had the lowest prices, but a price increase brought it closer to competitors. `Carrefour` saw a notable price hike in early October, though limited data prevents us from assessing a gradual rise.
  - **Olive oil**: Olive oil prices remained stable, mirroring the trend in sunflower oil.
  - **Milk**: Milk prices showed consistent stability across all supermarkets with no major changes.

- **Brand availability and price range**: `Mercadona` has the most stable and narrow price range due to offering only one brand, `Hacendado`, across all categories. In contrast, other supermarkets with multiple brands exhibit more price variability and outliers, particularly in the milk category, which may reflect the variety of milk types offered.

These findings suggest that comparing individual brands rather than entire supermarkets could yield more accurate insights due to the impact of brand variety on pricing.

## 🔄 Next Steps

- **Efficient brand segmentation**: Given that segmentation by brand may provide more meaningful insights than by supermarket, future analysis could involve comparing popular brands across different supermarkets. Additionally, we could take a single brand and compare its prices across all supermarkets where it is available. Another valuable comparison could focus on each supermarket's own private-label products, providing a fairer analysis that avoids the influence of premium brands on overall results.

- **Expanding analysis to other product sizes**: Besides the 1-liter format, other popular sizes like 3 and 5 liters for oil and 1.5 liters for milk should be analyzed, calculating the price per liter to ensure comparability across formats.

- **Considering data from additional supermarkets**: To gain a more comprehensive overview of supermarket pricing, we could incorporate data from additional supermarkets not covered by FACUA. This would require sourcing data from alternative providers but would allow for a broader and more complete analysis of the market.

  
## 🤝 Contributions
Contributions to this project are welcome! Follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Submit a pull request when you're ready.

If you have suggestions or improvements, feel free to open an issue.

## ✍️ Author
- **Javier Carreira** - Lead Developer - [GitHub](https://github.com/SupernovaIa)

We thank the **FACUA** team for providing the data source and **Hack(io)** for the opportunity to work on this project.