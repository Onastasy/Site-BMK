-- Скрипт для развёртывания базы данных БМК Чат на PostgreSQL
-- Запуск: psql -U bmk_user -d bmk_chat -f sql/create_tables_postgresql.sql


-- 1. ЧАТЫ (групповые чаты, каналы, личные переписки)
CREATE TABLE IF NOT EXISTS messaging_chatroom (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('PRIVATE', 'GROUP', 'CHANNEL', 'SUPPORT')),
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT DEFAULT '',
    avatar_url TEXT DEFAULT '',
    is_archived BOOLEAN DEFAULT FALSE,
    last_message_id INTEGER
);

-- Индекс для быстрого поиска чатов по создателю
CREATE INDEX IF NOT EXISTS idx_chats_created_by
    ON messaging_chatroom(created_by_id);

-- Индекс для фильтрации активных чатов
CREATE INDEX IF NOT EXISTS idx_chats_type_active
    ON messaging_chatroom(type, is_archived);


-- 2. УЧАСТНИКИ ЧАТОВ
CREATE TABLE IF NOT EXISTS messaging_chatmembership (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    chat_id INTEGER NOT NULL REFERENCES messaging_chatroom(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    role_in_chat VARCHAR(50) DEFAULT 'MEMBER' CHECK (role_in_chat IN ('OWNER', 'ADMIN', 'MODERATOR', 'MEMBER')),
    is_muted BOOLEAN DEFAULT FALSE,
    nickname_in_chat VARCHAR(100) DEFAULT '',
    last_read_message_id INTEGER,
    left_at TIMESTAMP WITH TIME ZONE NULL,
    UNIQUE(user_id, chat_id)
);

-- Индексы для быстрого получения чатов пользователя
CREATE INDEX IF NOT EXISTS idx_members_user
    ON messaging_chatmembership(user_id, left_at);
CREATE INDEX IF NOT EXISTS idx_members_chat
    ON messaging_chatmembership(chat_id);


-- 3. СООБЩЕНИЯ
CREATE TABLE IF NOT EXISTS messaging_chatmessage (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES messaging_chatroom(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    content TEXT NOT NULL DEFAULT '',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP WITH TIME ZONE NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    reply_to_id INTEGER REFERENCES messaging_chatmessage(id) ON DELETE SET NULL
);

-- Основной индекс для загрузки сообщений чата
CREATE INDEX IF NOT EXISTS idx_messages_chat_sent
    ON messaging_chatmessage(chat_id, sent_at DESC);

-- Индекс для поиска сообщений пользователя
CREATE INDEX IF NOT EXISTS idx_messages_sender
    ON messaging_chatmessage(sender_id, sent_at DESC);

-- GIN-индекс для полнотекстового поиска на русском языке
CREATE INDEX IF NOT EXISTS idx_messages_content_gin
    ON messaging_chatmessage USING gin(to_tsvector('russian', content));


-- 4. ПРОЧИТАВШИЕ СООБЩЕНИЕ (ManyToMany)
CREATE TABLE IF NOT EXISTS messaging_chatmessage_read_by (
    id SERIAL PRIMARY KEY,
    chatmessage_id INTEGER NOT NULL REFERENCES messaging_chatmessage(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    UNIQUE(chatmessage_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_read_message
    ON messaging_chatmessage_read_by(chatmessage_id);
CREATE INDEX IF NOT EXISTS idx_read_user
    ON messaging_chatmessage_read_by(user_id);


-- 5. ВЛОЖЕНИЯ К СООБЩЕНИЯМ
CREATE TABLE IF NOT EXISTS messaging_messageattachment (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messaging_chatmessage(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT DEFAULT 0,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_hash VARCHAR(64) DEFAULT '',
    download_count INTEGER DEFAULT 0,
    file VARCHAR(200) DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_attachments_message
    ON messaging_messageattachment(message_id);


-- 6. УВЕДОМЛЕНИЯ
CREATE TABLE IF NOT EXISTS messaging_chatnotification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    message_id INTEGER REFERENCES messaging_chatmessage(id) ON DELETE CASCADE,
    type VARCHAR(50) DEFAULT 'NEW_MESSAGE' CHECK (type IN ('NEW_MESSAGE', 'MENTION', 'TICKET_UPDATE', 'SYSTEM')),
    content VARCHAR(500) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    link VARCHAR(500) DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_notifications_user
    ON messaging_chatnotification(user_id, is_read, created_at DESC);


-- 7. ЗАКРЕПЛЁННЫЕ СООБЩЕНИЯ
CREATE TABLE IF NOT EXISTS messaging_pinnedmessage (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES messaging_chatroom(id) ON DELETE CASCADE,
    message_id INTEGER NOT NULL UNIQUE REFERENCES messaging_chatmessage(id) ON DELETE CASCADE,
    pinned_by_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    pinned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_pinned_chat
    ON messaging_pinnedmessage(chat_id, is_active);


-- 8. ИНТЕГРАЦИИ С ВНЕШНИМИ СИСТЕМАМИ
CREATE TABLE IF NOT EXISTS messaging_integration (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK (type IN ('JIRA', 'GITHUB', 'GITLAB', 'TELEGRAM')),
    name VARCHAR(100) NOT NULL,
    webhook_url VARCHAR(500) DEFAULT '',
    api_key VARCHAR(255) DEFAULT '',
    config JSONB DEFAULT '{}',
    created_by_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);



-- ПРИМЕРЫ ПОЛНОТЕКСТОВОГО ПОИСКА


-- Простой поиск по слову:
-- SELECT content, sent_at
-- FROM messaging_chatmessage
-- WHERE to_tsvector('russian', content) @@ to_tsquery('russian', 'собрание');

-- Поиск по нескольким словам:
-- SELECT content, sent_at
-- FROM messaging_chatmessage
-- WHERE to_tsvector('russian', content) @@ to_tsquery('russian', 'собрание & март');

-- Поиск с ранжированием по релевантности:
-- SELECT
--     content,
--     sent_at,
--     ts_rank(to_tsvector('russian', content), to_tsquery('russian', 'архитектура')) AS rank
-- FROM messaging_chatmessage
-- WHERE to_tsvector('russian', content) @@ to_tsquery('russian', 'архитектура')
-- ORDER BY rank DESC
-- LIMIT 20;