/**
 * Ranking System API Client
 * Handles category management and priorities
 */

import { apiGet, apiPost, apiPut } from './client';

// Types
export interface Category {
  id: string;
  name: string;
  necessity_score: number;
  default_allocation_percent: number;
  parent_category?: string;
  custom_priority?: number;
  monthly_limit?: number;
}

export interface UpdatePriorityRequest {
  custom_priority: number;
  monthly_limit?: number;
}

export interface CorrectCategoryRequest {
  merchant: string;
  correct_category_id: string;
}

// API Functions

export const rankingAPI = {
  /**
   * Get all categories with user's custom priorities
   */
  getCategories: (userId: string): Promise<Category[]> =>
    apiGet('ranking', `/ranking/categories?user_id=${userId}`),

  /**
   * Get categories ordered by priority
   */
  getPriorities: (userId: string): Promise<Category[]> =>
    apiGet('ranking', `/ranking/priorities?user_id=${userId}`),

  /**
   * Update user's custom priority for a category
   */
  updatePriority: (
    categoryId: string,
    userId: string,
    request: UpdatePriorityRequest
  ): Promise<{ success: boolean }> =>
    apiPut('ranking', `/ranking/priorities/${categoryId}?user_id=${userId}`, request),

  /**
   * Save category correction for a merchant
   */
  correctCategory: (userId: string, request: CorrectCategoryRequest): Promise<{ message: string }> =>
    apiPost('ranking', `/ranking/correct?user_id=${userId}`, request),

  /**
   * Health check
   */
  health: (): Promise<{ status: string }> =>
    apiGet('ranking', '/ranking/health'),
};
