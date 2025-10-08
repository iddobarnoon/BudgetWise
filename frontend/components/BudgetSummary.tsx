import { BudgetSummary as BudgetSummaryType } from '@/lib/types';

interface BudgetSummaryProps {
  summary: BudgetSummaryType | null;
  loading: boolean;
}

export default function BudgetSummary({ summary, loading }: BudgetSummaryProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 mb-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-8 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="bg-yellow-50 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
        <p className="font-medium">No budget found</p>
        <p className="text-sm">Create a budget by chatting with the AI assistant!</p>
      </div>
    );
  }

  const percentageSpent = summary.total_budget > 0
    ? (summary.total_spent / summary.total_budget) * 100
    : 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Budget Overview</h2>

      {/* Total Budget Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <p className="text-sm text-gray-500">Budget</p>
          <p className="text-2xl font-bold text-blue-600">
            ${summary.total_budget.toFixed(2)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500">Spent</p>
          <p className="text-2xl font-bold text-orange-600">
            ${summary.total_spent.toFixed(2)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500">Remaining</p>
          <p className={`text-2xl font-bold ${
            summary.total_remaining >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            ${summary.total_remaining.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Spent {percentageSpent.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${
              percentageSpent > 90 ? 'bg-red-500' :
              percentageSpent > 70 ? 'bg-orange-500' :
              'bg-green-500'
            }`}
            style={{ width: `${Math.min(percentageSpent, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Overspent Warning */}
      {summary.overspent_categories && summary.overspent_categories.length > 0 && (
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-medium">⚠️ Overspent Categories:</p>
          <p className="text-sm">{summary.overspent_categories.join(', ')}</p>
        </div>
      )}

      {/* Top Categories (optional - show top 3) */}
      {summary.categories && summary.categories.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Top Categories:</p>
          <div className="space-y-2">
            {summary.categories.slice(0, 3).map((cat, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <span className="text-gray-600">{cat.category_name || 'Unknown'}</span>
                <span className={cat.remaining_amount >= 0 ? 'text-green-600' : 'text-red-600'}>
                  ${cat.remaining_amount.toFixed(2)} left
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
