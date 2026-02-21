DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'apartment_type') THEN
        CREATE TYPE apartment_type AS ENUM ('Студія', 'Однокімнатна', 'Двокімнатна', 'Трикімнатна', 'Чотирикімнатна');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS apartments (
    id SERIAL PRIMARY KEY,
    number VARCHAR(10) UNIQUE NOT NULL,
    floor INTEGER NOT NULL CHECK (floor >= 0),
    type apartment_type NOT NULL,
    square_meters DECIMAL(5,2) CHECK (square_meters > 0),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS residents (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    birth_date DATE,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS residency (
    id SERIAL PRIMARY KEY,
    resident_id INTEGER REFERENCES residents(id) ON DELETE CASCADE,
    apartment_id INTEGER REFERENCES apartments(id) ON DELETE CASCADE,
    move_in_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(resident_id, apartment_id)
);