-- Add conversation_id to chat_messages table
-- This allows grouping messages by conversation for chat history

-- Add conversation_id column
ALTER TABLE chat_messages
ADD COLUMN IF NOT EXISTS conversation_id TEXT;

-- Create index for faster conversation history lookups
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation
ON chat_messages(user_id, conversation_id, timestamp DESC);

-- Add index for timestamp ordering
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp
ON chat_messages(timestamp DESC);
