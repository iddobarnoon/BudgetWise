import { ChatMessage as ChatMessageType } from '@/lib/types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {/* Role label */}
          <p className={`text-xs font-semibold mb-1 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}>
            {isUser ? 'You' : 'BudgetWise AI'}
          </p>

          {/* Message content */}
          <div className="text-sm whitespace-pre-wrap">
            {message.content}
          </div>

          {/* Timestamp */}
          <p className={`text-xs mt-2 ${
            isUser ? 'text-blue-100' : 'text-gray-400'
          }`}>
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>

        {/* Metadata display (optional - for debugging or showing category info) */}
        {message.metadata && !isUser && (
          <div className="mt-1 text-xs text-gray-500 px-2">
            {message.metadata.category && (
              <span className="inline-block bg-gray-200 rounded px-2 py-1 mr-1">
                {message.metadata.category}
              </span>
            )}
            {message.metadata.amount && (
              <span className="inline-block bg-green-100 text-green-700 rounded px-2 py-1">
                ${message.metadata.amount}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
