CREATE TABLE users (
                       id         UUID PRIMARY KEY,
                       email      VARCHAR(254) UNIQUE NOT NULL,
                       first_name VARCHAR(64),
                       last_name  VARCHAR(64),
                       birthdate  DATE,
                       password   VARCHAR(255) NOT NULL,
                       role       VARCHAR(32) DEFAULT 'USER',
                       enabled    BOOLEAN DEFAULT TRUE
);