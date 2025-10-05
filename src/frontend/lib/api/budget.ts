/**
 * Budget Engine API Client
 * Handles budget creation, management, and validation
 */

import { apiGet, apiPost, apiPut } from './client';

// Types
export interface CreateBudgetRequest {
  user_id: string;
  month: string;
  income: number;
  goals?: string[];
}

export interface BudgetPlan {
  id: string;
  user_id: string;
  month: string;
  total_income: number;
  allocations: CategoryAllocation[];
  created_at: string;
  updated_at: string;
}

export interface CategoryAllocation {
  category_id: string;
  category_name?: string;
  allocated_amount: number;
  spent_amount: number;
  remaining_amount: number;
}

export interface CheckPurchaseRequest {
  user_id: string;
  amount: number;
  category_id: string;
  month: string;
}

export interface CheckPurchaseResponse {
  fits_budget: boolean;
  remaining_in_category: number;
  percentage_of_category: number;
  warning?: string;
  alternative_options: string[];
}

export interface BudgetSummary {
  total_budget: number;
  total_spent: number;
  total_remaining: number;
  categories: CategoryAllocation[];
  overspent_categories: string[];
}

export interface UpdateSpentRequest {
  user_id: string;
  category_id: string;
  amount: number;
  month: string;
}

export interface ReallocationSuggestion {
  from_category: string;
  to_category: string;
  amount: number;
  reason: string;
}

// API Functions

export const budgetAPI = {
  /**
   * Create a new monthly budget
   */
  createBudget: (request: CreateBudgetRequest): Promise<BudgetPlan> =>
    apiPost('budget', '/budget/create', request),

  /**
   * Check if a purchase fits the budget
   */
  checkPurchase: (request: CheckPurchaseRequest): Promise<CheckPurchaseResponse> =>
    apiPost('budget', '/budget/check-purchase', request),

  /**
   * Get budget summary for a month
   */
  getSummary: (userId: string, month: string): Promise<BudgetSummary> =>
    apiGet('budget', `/budget/summary?user_id=${userId}&month=${month}`),

  /**
   * Update spent amount for a category
   */
  updateSpent: (request: UpdateSpentRequest): Promise<CategoryAllocation> =>
    apiPut('budget', '/budget/update-spent', request),

  /**
   * Get reallocation suggestions
   */
  getSuggestions: (userId: string, month: string): Promise<ReallocationSuggestion[]> =>
    apiGet('budget', `/budget/suggestions?user_id=${userId}&month=${month}`),

  /**
   * Health check
   */
  health: (): Promise<{ status: string }> =>
    apiGet('budget', '/budget/health'),
};
