-- =============================================================
-- Neighborhood Library Service — Database Schema
-- PostgreSQL 15+
-- =============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================
-- ENUM TYPES
-- =============================================================

CREATE TYPE membership_status AS ENUM ('active', 'suspended', 'expired');
CREATE TYPE loan_status AS ENUM ('active', 'returned', 'overdue');

-- =============================================================
-- TABLE: books
-- Stores all books the library owns.
-- total_copies  → how many physical copies the library has
-- available_copies → how many are currently on the shelf (not lent out)
-- =============================================================

CREATE TABLE books (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn             VARCHAR(20)  UNIQUE,
    title            VARCHAR(255) NOT NULL,
    author           VARCHAR(255) NOT NULL,
    genre            VARCHAR(100),
    published_year   SMALLINT,
    total_copies     INTEGER      NOT NULL DEFAULT 1 CHECK (total_copies >= 1),
    available_copies INTEGER      NOT NULL DEFAULT 1 CHECK (available_copies >= 0),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    -- available_copies can never exceed total_copies
    CONSTRAINT chk_copies CHECK (available_copies <= total_copies)
);

CREATE INDEX idx_books_author ON books (author);
CREATE INDEX idx_books_title  ON books (title);

-- =============================================================
-- TABLE: members
-- Tracks library members / cardholders.
-- =============================================================

CREATE TABLE members (
    id                UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name        VARCHAR(100)    NOT NULL,
    last_name         VARCHAR(100)    NOT NULL,
    email             VARCHAR(255)    NOT NULL UNIQUE,
    phone             VARCHAR(20),
    address           TEXT,
    membership_status membership_status NOT NULL DEFAULT 'active',
    membership_date   DATE            NOT NULL DEFAULT CURRENT_DATE,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_members_last_name  ON members (last_name);

-- =============================================================
-- TABLE: loans
-- Records each borrow / return transaction.
-- One row = one loan event (one copy of one book to one member).
-- returned_at is NULL while the book is still out.
-- fine_amount  accumulates when the book is returned overdue.
-- =============================================================

CREATE TABLE loans (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id     UUID        NOT NULL REFERENCES books(id)   ON DELETE RESTRICT,
    member_id   UUID        NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    borrowed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due_date    TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '14 days'),
    returned_at TIMESTAMPTZ,
    status      loan_status NOT NULL DEFAULT 'active',
    fine_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (fine_amount >= 0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_loans_book_id   ON loans (book_id);
CREATE INDEX idx_loans_member_id ON loans (member_id);
CREATE INDEX idx_loans_status    ON loans (status);
-- Quickly find all open (active / overdue) loans for overdue checks
CREATE INDEX idx_loans_active    ON loans (status, due_date) WHERE status != 'returned';

-- =============================================================
-- TRIGGER: auto-update updated_at on any row change
-- =============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_books_updated_at
    BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_members_updated_at
    BEFORE UPDATE ON members
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_loans_updated_at
    BEFORE UPDATE ON loans
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
