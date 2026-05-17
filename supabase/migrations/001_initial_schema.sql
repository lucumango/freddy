-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enums
CREATE TYPE user_role AS ENUM ('participant', 'admin');
CREATE TYPE question_type AS ENUM (
    'short_text', 'long_text', 'number', 'likert',
    'single_choice', 'multiple_choice', 'date'
);
CREATE TYPE notification_type AS ENUM ('reminder', 'edit_alert', 'deadline');
CREATE TYPE notification_status AS ENUM ('sent', 'failed');
CREATE TYPE notification_channel AS ENUM ('email');

-- Users (linked to Supabase Auth)
CREATE TABLE users (
    id          uuid PRIMARY KEY,  -- equals auth.users.id
    dni         varchar(8) UNIQUE NOT NULL,
    full_name   varchar,
    emails      text[] DEFAULT '{}',
    primary_email varchar,
    phone       varchar,
    role        user_role NOT NULL DEFAULT 'participant',
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

-- Forms
CREATE TABLE forms (
    id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    title       varchar NOT NULL,
    description text,
    is_active   boolean NOT NULL DEFAULT false,
    opens_at    timestamptz,
    closes_at   timestamptz,
    created_by  uuid REFERENCES users(id),
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

-- Questions
CREATE TABLE questions (
    id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id     uuid NOT NULL REFERENCES forms(id) ON DELETE CASCADE,
    order_index integer NOT NULL DEFAULT 0,
    label       text NOT NULL,
    type        question_type NOT NULL,
    required    boolean NOT NULL DEFAULT true,
    options     jsonb,
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Submissions (one per user per form)
CREATE TABLE submissions (
    id                      uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id                 uuid NOT NULL REFERENCES forms(id) ON DELETE CASCADE,
    user_id                 uuid NOT NULL REFERENCES users(id),
    submitted_at            timestamptz NOT NULL DEFAULT now(),
    last_edited_at          timestamptz,
    edit_count              integer NOT NULL DEFAULT 0,
    admin_notified_of_edit  boolean NOT NULL DEFAULT false,
    UNIQUE (form_id, user_id)
);

-- Responses (one per answer per question)
CREATE TABLE responses (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id   uuid NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    question_id     uuid NOT NULL REFERENCES questions(id),
    value           text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

-- Notifications log
CREATE TABLE notifications_log (
    id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     uuid REFERENCES users(id),
    type        notification_type NOT NULL,
    sent_at     timestamptz NOT NULL DEFAULT now(),
    channel     notification_channel NOT NULL DEFAULT 'email',
    status      notification_status NOT NULL
);

-- Indexes
CREATE INDEX idx_submissions_form_user ON submissions(form_id, user_id);
CREATE INDEX idx_responses_submission ON responses(submission_id);
CREATE INDEX idx_questions_form ON questions(form_id, order_index);
CREATE INDEX idx_notifications_user_type ON notifications_log(user_id, type, sent_at);
CREATE INDEX idx_users_dni ON users(dni);

-- Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications_log ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS (used by backend)
-- Participant policies (enforced via API layer, service role used by backend)

-- Updated_at auto-trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_forms_updated_at
    BEFORE UPDATE ON forms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
