"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { budgetAPI, rankingAPI } from "@/lib/api";
import { Plus, TrendingUp, TrendingDown, DollarSign, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function BudgetPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [monthlyIncome, setMonthlyIncome] = useState("");

  const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM

  // Fetch budget summary
  const { data: budgetSummary, isLoading } = useQuery({
    queryKey: ["budget-summary", user?.id, currentMonth],
    queryFn: () => budgetAPI.getSummary(user!.id, currentMonth),
    enabled: !!user,
  });

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ["categories", user?.id],
    queryFn: () => rankingAPI.getCategories(user!.id),
    enabled: !!user,
  });

  // Fetch suggestions
  const { data: suggestions = [] } = useQuery({
    queryKey: ["budget-suggestions", user?.id, currentMonth],
    queryFn: () => budgetAPI.getSuggestions(user!.id, currentMonth),
    enabled: !!user && !!budgetSummary,
  });

  // Create budget mutation
  const createBudgetMutation = useMutation({
    mutationFn: async (income: string) => {
      if (!user) throw new Error("User not authenticated");
      return budgetAPI.createBudget({
        user_id: user.id,
        month: currentMonth,
        monthly_income: parseFloat(income),
        financial_goals: user.financial_goals || [],
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budget-summary"] });
      setIsCreateDialogOpen(false);
      setMonthlyIncome("");
    },
  });

  const handleCreateBudget = (e: React.FormEvent) => {
    e.preventDefault();
    if (!monthlyIncome) return;
    createBudgetMutation.mutate(monthlyIncome);
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90) return "bg-red-500";
    if (percentage >= 70) return "bg-yellow-500";
    return "bg-green-500";
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="text-center py-8 text-muted-foreground">
          Loading budget...
        </div>
      </div>
    );
  }

  if (!budgetSummary) {
    return (
      <div className="container mx-auto px-6 py-8">
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>No Budget Found</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-6">
              You haven't created a budget for this month yet. Let's get started by
              creating one!
            </p>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Budget
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Monthly Budget</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateBudget} className="space-y-4">
                  <div>
                    <Label htmlFor="income">Monthly Income ($)</Label>
                    <Input
                      id="income"
                      type="number"
                      step="0.01"
                      placeholder="5000.00"
                      value={monthlyIncome}
                      onChange={(e) => setMonthlyIncome(e.target.value)}
                      required
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      We'll automatically allocate your income across categories based on
                      your priorities
                    </p>
                  </div>
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={createBudgetMutation.isPending}
                  >
                    {createBudgetMutation.isPending
                      ? "Creating..."
                      : "Create Budget"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>
      </div>
    );
  }

  const spentPercentage = budgetSummary.total_budget > 0
    ? (parseFloat(budgetSummary.total_spent.toString()) / parseFloat(budgetSummary.total_budget.toString())) * 100
    : 0;

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Budget Manager</h1>
          <p className="text-muted-foreground">
            {new Date().toLocaleDateString("en-US", {
              month: "long",
              year: "numeric",
            })}
          </p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Budget</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${parseFloat(budgetSummary.total_budget.toString()).toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${parseFloat(budgetSummary.total_spent.toString()).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              {spentPercentage.toFixed(1)}% of budget
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Remaining</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${parseFloat(budgetSummary.total_remaining.toString()).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              {(100 - spentPercentage).toFixed(1)}% available
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Overspent Alert */}
      {budgetSummary.overspent_categories &&
        budgetSummary.overspent_categories.length > 0 && (
          <Alert variant="destructive" className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              You're over budget in {budgetSummary.overspent_categories.length}{" "}
              {budgetSummary.overspent_categories.length === 1
                ? "category"
                : "categories"}
              :{" "}
              {budgetSummary.overspent_categories
                .map((id) => categories.find((c) => c.id === id)?.name || id)
                .join(", ")}
            </AlertDescription>
          </Alert>
        )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Budget Suggestions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className="p-4 border border-border rounded-lg bg-secondary/20"
                >
                  <p className="text-sm">{suggestion.suggestion}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Reason: {suggestion.reason}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Category Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Category Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {budgetSummary.categories.map((allocation) => {
              const category = categories.find(
                (c) => c.id === allocation.category_id
              );
              const percentage = parseFloat(allocation.allocated_amount.toString()) > 0
                ? (parseFloat(allocation.spent_amount.toString()) / parseFloat(allocation.allocated_amount.toString())) * 100
                : 0;
              const isOverBudget = percentage > 100;

              return (
                <div key={allocation.category_id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">
                        {category?.name || allocation.category_id}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        ${parseFloat(allocation.spent_amount.toString()).toFixed(2)} /{" "}
                        ${parseFloat(allocation.allocated_amount.toString()).toFixed(2)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p
                        className={`font-medium ${
                          isOverBudget ? "text-red-500" : ""
                        }`}
                      >
                        {percentage.toFixed(1)}%
                      </p>
                      <p className="text-sm text-muted-foreground">
                        ${parseFloat(allocation.remaining_amount.toString()).toFixed(2)}{" "}
                        left
                      </p>
                    </div>
                  </div>
                  <Progress
                    value={Math.min(percentage, 100)}
                    className={`h-2 ${getProgressColor(percentage)}`}
                  />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
