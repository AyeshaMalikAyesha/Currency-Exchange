import requests
import psycopg2
from datetime import date
import os

# API Configuration
API_KEY = os.getenv("API_KEY")
BASE_CURRENCIES = ['USD', 'GBP', 'PKR']
TARGET_CURRENCIES = ['USD', 'GBP', 'PKR']

# PostgreSQL connection configuration (from environment variables)
DB_NAME = os.getenv("DB_NAME") 
DB_USER = os.getenv("DB_USER") 
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = "65.108.37.94"
DB_PORT = "12020"

def fetch_exchange_rates(base_currency):
    url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}'
    response = requests.get(url)
    return response.json()

def main():
    print("Connecting to *******:", DB_NAME, DB_HOST, DB_PORT)

    today = date.today()

    try:
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
            data = fetch_exchange_rates(base_currency)

            if data.get('result') != 'success':
                print(f"Failed to fetch rates for base {base_currency}: {data}")
                continue

            for target_currency in TARGET_CURRENCIES:
                if target_currency == base_currency:
                    continue  # Skip same-currency conversion

                rate = data['conversion_rates'].get(target_currency)
                if rate:
                    cursor.execute("""
                        INSERT INTO exchange_rates (base_currency, target_currency, exchange_rate, date)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (base_currency, target_currency, date) DO NOTHING;
                    """, (base_currency, target_currency, rate, today))

        conn.commit()
        print("✅ Exchange rates inserted successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
