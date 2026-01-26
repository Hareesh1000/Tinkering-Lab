import os
import requests
import psycopg2
from psycopg2.extras import Json
from datetime import datetime


# -----------------------
# Load env.config file
# -----------------------
def load_env_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "env.config")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    with open(config_path) as file:
        for line in file:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

    print("Config loaded successfully")


# -----------------------
# Validate required vars
# -----------------------
def validate_env():
    required_vars = [
        "DB_HOST", "DB_NAME", "DB_USER",
        "DB_PASSWORD", "DB_PORT", "RAPIDAPI_KEY"
    ]

    missing = [v for v in required_vars if not os.getenv(v)]

    if missing:
        raise Exception(f"Missing config values: {missing}")


# -----------------------
# Connect to PostgreSQL
# -----------------------
def connect_db(db_config):
    try:
        conn = psycopg2.connect(**db_config)
        print("Database connected")
        return conn
    except Exception as e:
        print("DB Connection failed:", e)
        return None


# -----------------------
# Fetch Weather Data
# -----------------------
def fetch_weather_data(city):
    url = "https://yahoo-weather5.p.rapidapi.com/weather"

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "yahoo-weather5.p.rapidapi.com"
    }

    params = {
        "location": city,
        "format": "json",
        "u": "f"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except Exception as error:
        print("API Error:", error)
        return {"error": str(error)}


# -----------------------
# Save Weather Data
# -----------------------
def save_weather(conn, data):
    if not data:
        print("No data to save")
        return

    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO yh_weather (weather_info, generated_date)
                VALUES (%s, %s)
            """
            cur.execute(sql, (Json(data), datetime.now()))
            conn.commit()
            print("Weather data saved")

    except Exception as error:
        print("Error saving weather:", error)
        conn.rollback()
        save_error(conn, error, data)


# -----------------------
# Save Error Data
# -----------------------
def save_error(conn, error, response_data=None):
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO yh_weather_error
                (error_status, error_code, error_message, generated_date)
                VALUES (%s, %s, %s, %s)
            """

            cur.execute(
                sql,
                (
                    "FAILED",
                    type(error).__name__,
                    Json({"error": str(error), "response": response_data}),
                    datetime.now()
                )
            )
            conn.commit()
            print("Error logged")

    except Exception as db_error:
        print("Failed to log error:", db_error)
        conn.rollback()


# -----------------------
# Main Function
# -----------------------
def main():
    # Load config
    load_env_config()
    validate_env()

    # Build DB config AFTER loading env
    DB_CONFIG = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": int(os.getenv("DB_PORT"))
    }

    # Connect DB
    conn = connect_db(DB_CONFIG)
    if not conn:
        return

    # Business logic
    cities = ["chennai", "coimbatore"]

    for city in cities:
        print(f"Fetching weather for {city}...")

        weather_data = fetch_weather_data(city)

        if "error" in weather_data:
            save_error(conn, "API_ERROR", weather_data)
        else:
            save_weather(conn, weather_data)


    conn.close()
    print("Script finished")


if __name__ == "__main__":
    main()
