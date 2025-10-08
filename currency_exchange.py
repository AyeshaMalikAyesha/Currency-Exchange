import requests
import psycopg2
from datetime import date

# Config
API_KEY = 'ac1fec1cf38330e62088f737'  
BASE_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'
BASE_CURRENCIES = ['USD', 'GBP', 'PKR']
TARGET_CURRENCIES = ['USD', 'GBP', 'PKR']

# PostgreSQL connection config
DB_NAME = "aromatransact"
DB_USER = "ayesha"
DB_PASSWORD = "*postgressAyesha*"
DB_HOST = "65.108.37.94"
DB_PORT = "12020"

try:
    # Fetch exchange rates
    response = requests.get(BASE_URL)
    data = response.json()

    if data.get('result') != 'success':
        raise Exception("Failed to fetch exchange rate data")

    base_currency = data['base_code']
    today = date.today()

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    for base_currency in BASE_CURRENCIES:
        print(f"Fetching for base: {base_currency}")
        url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}'
        response = requests.get(url)
        data = response.json()

        if data.get('result') != 'success':
            print(f"Failed to fetch rates for base {base_currency}: {data}")
            continue

        for target_currency in TARGET_CURRENCIES:
            if target_currency == base_currency:
                continue  # Skip same-currency rates (e.g., USD to USD)

            rate = data['conversion_rates'].get(target_currency)
            if rate:
                cursor.execute("""
                    INSERT INTO exchange_rates (base_currency, target_currency, exchange_rate, date)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (base_currency, target_currency, date) DO NOTHING;
                """, (base_currency, target_currency, rate, today))

    conn.commit()
    print("Exchange rates inserted successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
