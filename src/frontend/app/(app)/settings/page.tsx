"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rankingAPI } from "@/lib/api";
import { Save, UserCircle, Target, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/hooks/use-toast";

export default function SettingsPage() {
  const { user, updateUser } = useAuth();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || "",
    monthly_income: user?.monthly_income?.toString() || "",
    risk_tolerance: user?.risk_tolerance || "moderate",
  });

  // Fetch categories with user preferences
  const { data: categories = [] } = useQuery({
    queryKey: ["categories", user?.id],
    queryFn: () => rankingAPI.getCategories(user!.id),
    enabled: !!user,
  });

  const [categoryPriorities, setCategoryPriorities] = useState<
    Record<string, number>
  >({});

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (updates: typeof profileForm) => {
      if (!user) throw new Error("User not authenticated");
      await updateUser({
        full_name: updates.full_name,
        monthly_income: parseFloat(updates.monthly_income),
        risk_tolerance: updates.risk_tolerance as "conservative" | "moderate" | "aggressive",
      });
    },
    onSuccess: () => {
      toast({
        title: "Profile updated",
        description: "Your profile has been successfully updated.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update profile. Please try again.",
        variant: "destructive",
      });
    },
  });

  // Update category priority mutation
  const updatePriorityMutation = useMutation({
    mutationFn: async ({
      categoryId,
      priority,
    }: {
      categoryId: string;
      priority: number;
    }) => {
      if (!user) throw new Error("User not authenticated");
      return rankingAPI.updatePriority(categoryId, user.id, {
        custom_priority: priority,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      toast({
        title: "Priority updated",
        description: "Category priority has been updated.",
      });
    },
  });

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate(profileForm);
  };

  const handlePriorityChange = (categoryId: string, priority: number) => {
    setCategoryPriorities((prev) => ({ ...prev, [categoryId]: priority }));
    updatePriorityMutation.mutate({ categoryId, priority });
  };

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Manage your profile and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <UserCircle className="h-5 w-5" />
              <CardTitle>Profile Information</CardTitle>
            </div>
            <CardDescription>
              Update your personal details and financial information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <div>
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  value={profileForm.full_name}
                  onChange={(e) =>
                    setProfileForm({ ...profileForm, full_name: e.target.value })
                  }
                  placeholder="John Doe"
                />
              </div>

              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={user?.email || ""}
                  disabled
                  className="bg-muted"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Email cannot be changed
                </p>
              </div>

              <div>
                <Label htmlFor="monthly_income">Monthly Income ($)</Label>
                <Input
                  id="monthly_income"
                  type="number"
                  step="0.01"
                  value={profileForm.monthly_income}
                  onChange={(e) =>
                    setProfileForm({
                      ...profileForm,
                      monthly_income: e.target.value,
                    })
                  }
                  placeholder="5000.00"
                />
              </div>

              <div>
                <Label htmlFor="risk_tolerance">Risk Tolerance</Label>
                <Select
                  value={profileForm.risk_tolerance}
                  onValueChange={(value) =>
                    setProfileForm({ ...profileForm, risk_tolerance: value })
                  }
                >
                  <SelectTrigger id="risk_tolerance">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="conservative">Conservative</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                    <SelectItem value="aggressive">Aggressive</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground mt-1">
                  This affects budget recommendations and financial advice
                </p>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={updateProfileMutation.isPending}
              >
                {updateProfileMutation.isPending ? (
                  "Saving..."
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save Changes
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Financial Goals */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              <CardTitle>Financial Goals</CardTitle>
            </div>
            <CardDescription>
              Set your financial objectives and savings targets
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border border-border rounded-lg bg-secondary/20">
                <p className="text-sm text-muted-foreground">
                  Financial goals customization coming soon! This feature will
                  allow you to set and track specific savings targets.
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Current Goals:</h4>
                <ul className="space-y-1">
                  {user?.financial_goals && user.financial_goals.length > 0 ? (
                    user.financial_goals.map((goal, idx) => (
                      <li
                        key={idx}
                        className="text-sm text-muted-foreground flex items-center gap-2"
                      >
                        <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                        {goal}
                      </li>
                    ))
                  ) : (
                    <li className="text-sm text-muted-foreground">
                      No goals set yet
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Category Priorities */}
      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            <CardTitle>Category Priorities</CardTitle>
          </div>
          <CardDescription>
            Customize how important each spending category is to you. Higher
            priority categories get more budget allocation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {categories.map((category) => {
              const priority =
                categoryPriorities[category.id] ?? category.necessity_score ?? 5;

              return (
                <div key={category.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>{category.name}</Label>
                      <p className="text-xs text-muted-foreground">
                        Default priority: {category.necessity_score}/10
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-lg">{priority}</span>
                      <span className="text-muted-foreground">/10</span>
                    </div>
                  </div>
                  <Slider
                    value={[priority]}
                    onValueChange={(value) =>
                      handlePriorityChange(category.id, value[0])
                    }
                    min={1}
                    max={10}
                    step={1}
                    className="w-full"
                  />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Account Section */}
      <Card className="mt-6 border-destructive/50">
        <CardHeader>
          <CardTitle>Danger Zone</CardTitle>
          <CardDescription>
            Irreversible actions for your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 border border-destructive/50 rounded-lg bg-destructive/10">
              <h4 className="font-medium mb-2">Delete Account</h4>
              <p className="text-sm text-muted-foreground mb-4">
                This will permanently delete your account and all associated data.
                This action cannot be undone.
              </p>
              <Button variant="destructive" disabled>
                Delete Account
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
