-- =========================
-- USERS
-- =========================
CREATE TABLE users (
    idUser INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- BOOKS
-- =========================
CREATE TABLE books (
    idBook INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    publisher TEXT,
    year INTEGER,
    synopsis TEXT NOT NULL,
    cover_url TEXT,
    is_available INTEGER DEFAULT 1 -- 1 = true, 0 = false
);

-- =========================
-- LOANS
-- =========================
CREATE TABLE loans (
    idLoan INTEGER PRIMARY KEY AUTOINCREMENT,
    idUserRef INTEGER NOT NULL,
    idBookRef INTEGER NOT NULL,
    loan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    return_date DATETIME,
    status TEXT DEFAULT 'active',

    FOREIGN KEY (idUserRef) REFERENCES users(idUser),
    FOREIGN KEY (idBookRef) REFERENCES books(idBook)
);

-- =========================
-- REVIEWS
-- =========================
CREATE TABLE reviews (
    idReview INTEGER PRIMARY KEY AUTOINCREMENT,
    idUserRef INTEGER NOT NULL,
    idBookRef INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,

    FOREIGN KEY (idUserRef) REFERENCES users(idUser),
    FOREIGN KEY (idBookRef) REFERENCES books(idBook)
);