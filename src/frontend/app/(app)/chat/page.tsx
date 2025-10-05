"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/context/AuthContext";
import { aiAPI } from "@/lib/api";
import { Send, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    if (messages.length === 0) {
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content:
            "👋 Hi! I'm your AI financial assistant. I can help you with:\n\n• Analyzing purchase decisions\n• Tracking expenses\n• Managing your budget\n• Providing financial insights\n\nWhat would you like to know?",
          timestamp: new Date(),
        },
      ]);
    }
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !user || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiAPI.chat({
        user_id: user.id,
        message: userMessage.content,
        context: {
          conversation_history: messages.slice(-5).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        },
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      setError(
        "Failed to get response from AI assistant. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <h1 className="text-2xl font-bold">AI Financial Assistant</h1>
        <p className="text-sm text-muted-foreground">
          Ask me anything about your finances
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <Card
              className={`max-w-[80%] md:max-w-[60%] p-4 ${
                message.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-card"
              }`}
            >
              <div className="whitespace-pre-wrap break-words">
                {message.content}
              </div>
              <div
                className={`text-xs mt-2 ${
                  message.role === "user"
                    ? "text-primary-foreground/70"
                    : "text-muted-foreground"
                }`}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </div>
            </Card>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <Card className="max-w-[80%] md:max-w-[60%] p-4 bg-card">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-muted-foreground">Thinking...</span>
              </div>
            </Card>
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="border-t border-border bg-card px-6 py-4">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me about your finances..."
            disabled={isLoading}
            className="flex-1"
            autoFocus
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-2">
          Try: "Should I buy a new laptop for $1500?" or "Show me my spending
          this month"
        </p>
      </div>
    </div>
  );
}
