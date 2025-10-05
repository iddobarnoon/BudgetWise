import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sparkles, TrendingUp, MessageSquare, PieChart, Shield, Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold">
            <span className="text-primary">Budget</span>
            <span className="text-foreground">Wise</span>
          </div>
          <div className="flex gap-4">
            <Link href="/login">
              <Button variant="ghost">Log In</Button>
            </Link>
            <Link href="/signup">
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary/20 bg-primary/10">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm text-primary">AI-Powered Financial Intelligence</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            Make Smarter{" "}
            <span className="text-primary">Financial Decisions</span>
          </h1>

          <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
            Your AI-powered personal finance assistant that helps you budget wisely,
            track expenses, and make informed purchase decisions.
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <Link href="/signup">
              <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 text-lg px-8">
                Start Free Today
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="text-lg px-8">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20 bg-secondary/20">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Everything You Need to Take Control
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="p-6 space-y-4 bg-card border-border hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">AI Chat Assistant</h3>
              <p className="text-muted-foreground">
                Ask questions, log expenses, and get financial advice through natural conversation.
              </p>
            </Card>

            <Card className="p-6 space-y-4 bg-card border-border hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <PieChart className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Smart Budgeting</h3>
              <p className="text-muted-foreground">
                Automatically categorize expenses and allocate budgets based on your financial goals.
              </p>
            </Card>

            <Card className="p-6 space-y-4 bg-card border-border hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Purchase Recommendations</h3>
              <p className="text-muted-foreground">
                Get AI-powered advice on whether you should buy, wait, or save for later.
              </p>
            </Card>

            <Card className="p-6 space-y-4 bg-card border-border hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Expense Tracking</h3>
              <p className="text-muted-foreground">
                Track spending patterns and visualize where your money goes with beautiful charts.
              </p>
            </Card>

            <Card className="p-6 space-y-4 bg-card border-border hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Secure & Private</h3>
              <p className="text-muted-foreground">
                Your financial data is encrypted and protected with industry-standard security.
              </p>
            </Card>

            <Card className="p-6 space-y-4 bg-card border-border hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">Real-time Updates</h3>
              <p className="text-muted-foreground">
                See your budget adjust instantly as you log expenses and make financial decisions.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <h2 className="text-3xl md:text-5xl font-bold">
            Ready to Take Control of Your Finances?
          </h2>
          <p className="text-xl text-muted-foreground">
            Join thousands of users making smarter financial decisions with BudgetWise.
          </p>
          <Link href="/signup">
            <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 text-lg px-8">
              Get Started for Free
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>&copy; 2025 BudgetWise. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
