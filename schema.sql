CREATE TABLE chats (
    id BIGINT PRIMARY KEY NOT NULL UNIQUE,
    username VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    chat_id BIGINT REFERENCES chats(id),
    is_bot BOOLEAN,
    text TEXT,
    update_obj JSON
);

CREATE TABLE subscriptions (
    chat_id BIGINT REFERENCES chats(id),
    end_at DATE,
    panel_client_id VARCHAR,
    panel_key TEXT,
    is_active BOOLEAN DEFAULT TRUE
);


CREATE TABLE settings (
    key VARCHAR PRIMARY KEY,
    value TEXT
);