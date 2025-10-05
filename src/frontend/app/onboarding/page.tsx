"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Select } from "@/components/ui/select";
import { Check } from "lucide-react";

type OnboardingData = {
  monthlyIncome: string;
  riskTolerance: "conservative" | "moderate" | "aggressive";
  financialGoals: string[];
  budgetPreferences: { [key: string]: number };
};

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [data, setData] = useState<OnboardingData>({
    monthlyIncome: "",
    riskTolerance: "moderate",
    financialGoals: [],
    budgetPreferences: {},
  });

  const totalSteps = 3;
  const progress = (step / totalSteps) * 100;

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleComplete = async () => {
    // TODO: Save data to backend via API
    console.log("Onboarding data:", data);
    router.push("/dashboard");
  };

  const toggleGoal = (goal: string) => {
    setData((prev) => ({
      ...prev,
      financialGoals: prev.financialGoals.includes(goal)
        ? prev.financialGoals.filter((g) => g !== goal)
        : [...prev.financialGoals, goal],
    }));
  };

  const defaultGoals = [
    "Build emergency fund",
    "Pay off debt",
    "Save for house",
    "Save for retirement",
    "Travel more",
    "Invest in stocks",
  ];

  const categories = [
    { id: "housing", name: "Housing", default: 30 },
    { id: "groceries", name: "Groceries", default: 15 },
    { id: "transportation", name: "Transportation", default: 15 },
    { id: "dining", name: "Dining Out", default: 10 },
    { id: "entertainment", name: "Entertainment", default: 10 },
    { id: "savings", name: "Savings", default: 20 },
  ];

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-3xl p-8 space-y-6 bg-card border-border">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold">
            <span className="text-primary">Budget</span>
            <span className="text-foreground">Wise</span>
          </h1>
          <p className="text-muted-foreground">Let&apos;s set up your budget in 3 simple steps</p>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Step {step} of {totalSteps}</span>
            <span>{Math.round(progress)}% complete</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Step Content */}
        <div className="min-h-[300px]">
          {/* Step 1: Personal Info */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-semibold mb-2">Personal Information</h2>
                <p className="text-muted-foreground">Tell us about your financial situation</p>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="income">Monthly Income</Label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                    <Input
                      id="income"
                      type="number"
                      placeholder="5000"
                      value={data.monthlyIncome}
                      onChange={(e) => setData({ ...data, monthlyIncome: e.target.value })}
                      className="pl-7 bg-input border-border"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="risk">Risk Tolerance</Label>
                  <select
                    id="risk"
                    value={data.riskTolerance}
                    onChange={(e) =>
                      setData({ ...data, riskTolerance: e.target.value as any })
                    }
                    className="w-full h-10 px-3 rounded-md border border-border bg-input text-foreground"
                  >
                    <option value="conservative">Conservative - I prefer safety</option>
                    <option value="moderate">Moderate - Balanced approach</option>
                    <option value="aggressive">Aggressive - Higher growth potential</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Financial Goals */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-semibold mb-2">Financial Goals</h2>
                <p className="text-muted-foreground">What are you saving for? (Select all that apply)</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {defaultGoals.map((goal) => (
                  <button
                    key={goal}
                    onClick={() => toggleGoal(goal)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      data.financialGoals.includes(goal)
                        ? "border-primary bg-primary/10"
                        : "border-border bg-card hover:border-primary/50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{goal}</span>
                      {data.financialGoals.includes(goal) && (
                        <Check className="w-5 h-5 text-primary" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Budget Preferences */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-semibold mb-2">Budget Allocation</h2>
                <p className="text-muted-foreground">
                  Adjust the percentage of your income for each category
                </p>
              </div>

              <div className="space-y-4">
                {categories.map((cat) => (
                  <div key={cat.id} className="space-y-2">
                    <div className="flex justify-between">
                      <Label>{cat.name}</Label>
                      <span className="text-sm text-muted-foreground">
                        {data.budgetPreferences[cat.id] || cat.default}%
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="50"
                      value={data.budgetPreferences[cat.id] || cat.default}
                      onChange={(e) =>
                        setData({
                          ...data,
                          budgetPreferences: {
                            ...data.budgetPreferences,
                            [cat.id]: parseInt(e.target.value),
                          },
                        })
                      }
                      className="w-full accent-primary"
                    />
                  </div>
                ))}
              </div>

              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <p className="text-sm">
                  Total:{" "}
                  <span className="font-semibold text-primary">
                    {Object.values(data.budgetPreferences).reduce((a, b) => a + b, 0) ||
                      categories.reduce((a, b) => a + b.default, 0)}
                    %
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between pt-6 border-t border-border">
          <Button
            onClick={handleBack}
            variant="outline"
            disabled={step === 1}
          >
            Back
          </Button>
          <Button
            onClick={handleNext}
            className="bg-primary text-primary-foreground hover:bg-primary/90"
            disabled={step === 1 && !data.monthlyIncome}
          >
            {step === totalSteps ? "Complete Setup" : "Next"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
