'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import BudgetSummary from '@/components/BudgetSummary';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import { budgetService, aiService } from '@/lib/api';
import { BudgetSummary as BudgetSummaryType, ChatMessage as ChatMessageType } from '@/lib/types';

export default function ChatPage() {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // State
  const [userId, setUserId] = useState<string>('');
  const [userEmail, setUserEmail] = useState<string>('');
  const [budgetSummary, setBudgetSummary] = useState<BudgetSummaryType | null>(null);
  const [budgetLoading, setBudgetLoading] = useState(true);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [conversationId, setConversationId] = useState<string>('');
  const [sendingMessage, setSendingMessage] = useState(false);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check authentication and load data on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('user_id');
    const storedEmail = localStorage.getItem('user_email');

    if (!token || !storedUserId) {
      router.push('/register');
      return;
    }

    setUserId(storedUserId);
    setUserEmail(storedEmail || '');

    // Load budget summary
    loadBudgetSummary(storedUserId);

    // Add welcome message
    const welcomeMessage: ChatMessageType = {
      id: 'welcome',
      user_id: storedUserId,
      role: 'assistant',
      content: `Welcome to BudgetWise! 👋\n\nI'm your AI financial assistant. Here's what I can help you with:\n\n💰 Log expenses: "I spent $50 on groceries"\n💭 Purchase advice: "Should I buy a $200 jacket?"\n📊 Budget insights: "Show me my budget summary"\n\nHow can I help you today?`,
      timestamp: new Date().toISOString(),
    };
    setMessages([welcomeMessage]);
  }, [router]);

  const loadBudgetSummary = async (uid: string) => {
    setBudgetLoading(true);
    try {
      const currentMonth = new Date().toISOString().slice(0, 7); // "2025-10"
      const summary = await budgetService.getBudgetSummary(uid, currentMonth);
      setBudgetSummary(summary);
    } catch (error: any) {
      console.error('Failed to load budget:', error);
      // Budget might not exist yet - that's okay
      if (error.response?.status === 404) {
        setBudgetSummary(null);
      }
    } finally {
      setBudgetLoading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    if (!userId || sendingMessage) return;

    // Add user message to chat
    const userMessage: ChatMessageType = {
      id: `user-${Date.now()}`,
      user_id: userId,
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setSendingMessage(true);

    try {
      // Send to AI service
      const response = await aiService.chat(userId, messageText, conversationId);

      // Update conversation ID
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add AI response to chat
      const aiMessage: ChatMessageType = {
        id: `ai-${Date.now()}`,
        user_id: userId,
        role: 'assistant',
        content: response.message || 'I received your message!',
        timestamp: new Date().toISOString(),
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, aiMessage]);

      // Refresh budget summary if the message involved expenses
      if (
        messageText.toLowerCase().includes('spent') ||
        messageText.toLowerCase().includes('bought') ||
        response.message.toLowerCase().includes('logged')
      ) {
        setTimeout(() => loadBudgetSummary(userId), 1000);
      }
    } catch (error: any) {
      console.error('Chat error:', error);

      // Add error message
      const errorMessage: ChatMessageType = {
        id: `error-${Date.now()}`,
        user_id: userId,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message || 'Unknown error'}. Please try again.`,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    router.push('/register');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">BudgetWise</h1>
              <p className="text-sm text-gray-500">{userEmail}</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Budget Summary */}
        <BudgetSummary summary={budgetSummary} loading={budgetLoading} />

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-md flex flex-col" style={{ height: 'calc(100vh - 400px)' }}>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <ChatInput onSendMessage={handleSendMessage} disabled={sendingMessage} />
        </div>

        {/* Helper Text */}
        <div className="mt-4 text-center text-sm text-gray-500">
          <p>💡 Tip: Try asking "Should I buy..." or "I spent $... on..."</p>
        </div>
      </main>
    </div>
  );
}
