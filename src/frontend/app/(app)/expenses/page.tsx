"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { aiAPI, rankingAPI } from "@/lib/api";
import { Plus, Filter, Trash2, Edit, Calendar, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

interface Expense {
  id: string;
  amount: number;
  description: string;
  category: string;
  category_id: string;
  date: string;
}

export default function ExpensesPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Form state
  const [newExpense, setNewExpense] = useState({
    description: "",
    amount: "",
    date: new Date().toISOString().split("T")[0],
  });

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ["categories", user?.id],
    queryFn: () => rankingAPI.getCategories(user!.id),
    enabled: !!user,
  });

  // Fetch expenses (using AI service to extract/classify)
  const { data: expenses = [], isLoading } = useQuery<Expense[]>({
    queryKey: ["expenses", user?.id],
    queryFn: async () => {
      // In a real app, you'd have a dedicated expenses endpoint
      // For now, we'll use mock data structure
      // You would integrate with Supabase or a backend expenses API
      return [];
    },
    enabled: !!user,
  });

  // Add expense mutation
  const addExpenseMutation = useMutation({
    mutationFn: async (expense: typeof newExpense) => {
      if (!user) throw new Error("User not authenticated");

      // First, extract and classify the expense using AI
      const classification = await aiAPI.extractExpense({
        text: `${expense.description} for $${expense.amount}`,
      });

      // In a real app, you'd save to Supabase or backend
      return {
        id: Date.now().toString(),
        amount: parseFloat(expense.amount),
        description: expense.description,
        category: classification.category || "Other",
        category_id: classification.category_id || "unknown",
        date: expense.date,
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
      setIsAddDialogOpen(false);
      setNewExpense({
        description: "",
        amount: "",
        date: new Date().toISOString().split("T")[0],
      });
    },
  });

  // Filter expenses
  const filteredExpenses = expenses.filter((expense) => {
    const matchesCategory =
      categoryFilter === "all" || expense.category_id === categoryFilter;
    const matchesSearch = expense.description
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Calculate totals
  const totalSpent = filteredExpenses.reduce(
    (sum, expense) => sum + expense.amount,
    0
  );

  const handleAddExpense = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExpense.description || !newExpense.amount) return;
    addExpenseMutation.mutate(newExpense);
  };

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Expenses</h1>
          <p className="text-muted-foreground">
            Track and manage your spending
          </p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="mt-4 md:mt-0">
              <Plus className="mr-2 h-4 w-4" />
              Add Expense
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Expense</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddExpense} className="space-y-4">
              <div>
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  placeholder="e.g., Grocery shopping at Whole Foods"
                  value={newExpense.description}
                  onChange={(e) =>
                    setNewExpense({ ...newExpense, description: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="amount">Amount ($)</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={newExpense.amount}
                  onChange={(e) =>
                    setNewExpense({ ...newExpense, amount: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={newExpense.date}
                  onChange={(e) =>
                    setNewExpense({ ...newExpense, date: e.target.value })
                  }
                  required
                />
              </div>
              <Button
                type="submit"
                className="w-full"
                disabled={addExpenseMutation.isPending}
              >
                {addExpenseMutation.isPending ? "Adding..." : "Add Expense"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Card */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Expenses</p>
              <p className="text-2xl font-bold">{filteredExpenses.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Spent</p>
              <p className="text-2xl font-bold">${totalSpent.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Average per Expense</p>
              <p className="text-2xl font-bold">
                $
                {filteredExpenses.length > 0
                  ? (totalSpent / filteredExpenses.length).toFixed(2)
                  : "0.00"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="search">Search</Label>
              <Input
                id="search"
                placeholder="Search expenses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="category">Category</Label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger id="category">
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Expenses List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Expenses</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading expenses...
            </div>
          ) : filteredExpenses.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">
                {expenses.length === 0
                  ? "No expenses yet. Add your first expense to get started!"
                  : "No expenses match your filters."}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredExpenses.map((expense) => (
                <div
                  key={expense.id}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-secondary/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium">{expense.description}</h3>
                      <Badge variant="outline">{expense.category}</Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(expense.date).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-bold text-lg">
                        ${expense.amount.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
