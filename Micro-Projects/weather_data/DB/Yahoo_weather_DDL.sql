CREATE TABLE weather (
    id SERIAL PRIMARY KEY,
    weather_info JSONB NOT NULL,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE weather_error (
    id SERIAL PRIMARY KEY,
    error_status TEXT,
    error_code TEXT,
    error_message JSONB,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


