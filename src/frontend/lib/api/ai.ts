/**
 * AI Pipeline API Client
 * Handles chat, purchase analysis, and expense classification
 */

import { apiGet, apiPost } from './client';

// Types
export interface ChatRequest {
  user_id: string;
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  metadata?: Record<string, any>;
}

export interface PurchaseAnalysisRequest {
  user_id: string;
  item: string;
  amount: number;
  user_message?: string;
}

export interface PurchaseAnalysisResponse {
  decision: 'buy' | 'wait' | 'dont_buy';
  reason: string;
  alternatives: string[];
  impact: string;
  confidence: number;
  category?: string;
  budget_remaining?: number;
}

export interface ExpenseExtractionRequest {
  message: string;
  user_id: string;
}

export interface ExpenseExtractionResponse {
  amount?: number;
  description: string;
  merchant?: string;
  date?: string;
  item?: string;
  category?: string;
  category_confidence?: number;
}

export interface ClassifyExpenseRequest {
  user_id: string;
  description: string;
  amount: number;
  merchant?: string;
}

export interface ClassifyExpenseResponse {
  category_id: string;
  category_name: string;
  necessity_score: number;
  confidence: number;
  reasoning?: string;
}

export interface BudgetInsightsResponse {
  insights: string;
  total_budget: number;
  total_spent: number;
  total_remaining: number;
  month: string;
}

// API Functions

export const aiAPI = {
  /**
   * Send a chat message and get AI response
   */
  chat: (request: ChatRequest): Promise<ChatResponse> =>
    apiPost('ai', '/ai/chat', request),

  /**
   * Analyze a purchase decision
   */
  analyzePurchase: (request: PurchaseAnalysisRequest): Promise<PurchaseAnalysisResponse> =>
    apiPost('ai', '/ai/analyze-purchase', request),

  /**
   * Extract expense from natural language
   */
  extractExpense: (request: ExpenseExtractionRequest): Promise<ExpenseExtractionResponse> =>
    apiPost('ai', '/ai/extract-expense', request),

  /**
   * Classify an expense (AI-powered, high confidence)
   */
  classifyExpense: (request: ClassifyExpenseRequest): Promise<ClassifyExpenseResponse> =>
    apiPost('ai', '/ai/classify-expense', request),

  /**
   * Get budget insights for a month
   */
  getInsights: (userId: string, month?: string): Promise<BudgetInsightsResponse> =>
    apiGet('ai', `/ai/insights?user_id=${userId}${month ? `&month=${month}` : ''}`),

  /**
   * Health check
   */
  health: (): Promise<{ status: string }> =>
    apiGet('ai', '/ai/health'),
};
