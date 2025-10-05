"use client";

import { Card } from "@/components/ui/card";
import { TrendingUp, TrendingDown, DollarSign, Target } from "lucide-react";

export default function DashboardPage() {
  // Mock data - will be replaced with real data from API
  const stats = [
    {
      name: "Total Budget",
      value: "$5,000",
      change: "+12%",
      trend: "up",
      icon: DollarSign,
    },
    {
      name: "Spent This Month",
      value: "$3,240",
      change: "+8%",
      trend: "up",
      icon: TrendingUp,
    },
    {
      name: "Remaining",
      value: "$1,760",
      change: "-5%",
      trend: "down",
      icon: TrendingDown,
    },
    {
      name: "Savings Goal",
      value: "72%",
      change: "+15%",
      trend: "up",
      icon: Target,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here&apos;s your financial overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.name} className="p-6 bg-card border-border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{stat.name}</p>
                <p className="text-2xl font-bold mt-1">{stat.value}</p>
                <p
                  className={`text-sm mt-1 ${
                    stat.trend === "up" ? "text-primary" : "text-destructive"
                  }`}
                >
                  {stat.change} from last month
                </p>
              </div>
              <div className={`p-3 rounded-full ${
                stat.trend === "up" ? "bg-primary/10" : "bg-destructive/10"
              }`}>
                <stat.icon className={`w-6 h-6 ${
                  stat.trend === "up" ? "text-primary" : "text-destructive"
                }`} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Budget Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 bg-card border-border">
          <h3 className="text-lg font-semibold mb-4">Budget by Category</h3>
          <div className="space-y-4">
            {[
              { name: "Housing", spent: 1500, budget: 1500, color: "bg-primary" },
              { name: "Groceries", spent: 650, budget: 750, color: "bg-blue-500" },
              { name: "Transportation", spent: 400, budget: 750, color: "bg-green-500" },
              { name: "Dining", spent: 350, budget: 500, color: "bg-yellow-500" },
              { name: "Entertainment", spent: 340, budget: 500, color: "bg-purple-500" },
            ].map((category) => (
              <div key={category.name}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{category.name}</span>
                  <span className="text-muted-foreground">
                    ${category.spent} / ${category.budget}
                  </span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div
                    className={`h-full ${category.color} transition-all`}
                    style={{ width: `${(category.spent / category.budget) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 bg-card border-border">
          <h3 className="text-lg font-semibold mb-4">Recent Expenses</h3>
          <div className="space-y-3">
            {[
              { name: "Whole Foods", amount: 120, category: "Groceries", date: "Today" },
              { name: "Uber", amount: 25, category: "Transportation", date: "Yesterday" },
              { name: "Netflix", amount: 15.99, category: "Entertainment", date: "2 days ago" },
              { name: "Chipotle", amount: 18, category: "Dining", date: "2 days ago" },
            ].map((expense, i) => (
              <div key={i} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{expense.name}</p>
                  <p className="text-sm text-muted-foreground">{expense.category} • {expense.date}</p>
                </div>
                <p className="font-semibold">${expense.amount}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="p-6 bg-card border-border">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-border rounded-lg hover:border-primary transition-colors text-left">
            <p className="font-medium">Log Expense</p>
            <p className="text-sm text-muted-foreground">Track a new purchase</p>
          </button>
          <button className="p-4 border border-border rounded-lg hover:border-primary transition-colors text-left">
            <p className="font-medium">Ask AI</p>
            <p className="text-sm text-muted-foreground">Get financial advice</p>
          </button>
          <button className="p-4 border border-border rounded-lg hover:border-primary transition-colors text-left">
            <p className="font-medium">View Budget</p>
            <p className="text-sm text-muted-foreground">See detailed breakdown</p>
          </button>
        </div>
      </Card>
    </div>
  );
}
