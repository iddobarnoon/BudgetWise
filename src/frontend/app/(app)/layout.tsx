"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Home, MessageSquare, Receipt, Settings, PieChart, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { ProtectedRoute } from "@/components/protected-route";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Expenses", href: "/expenses", icon: Receipt },
  { name: "Budget", href: "/budget", icon: PieChart },
  { name: "Settings", href: "/settings", icon: Settings },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        {/* Desktop Sidebar */}
        <aside className="hidden md:fixed md:inset-y-0 md:flex md:w-64 md:flex-col">
          <div className="flex flex-col flex-grow border-r border-border bg-card">
            {/* Logo */}
            <div className="flex items-center h-16 px-6 border-b border-border">
              <h1 className="text-2xl font-bold">
                <span className="text-primary">Budget</span>
                <span className="text-foreground">Wise</span>
              </h1>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-4 space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                    }`}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>

            {/* Logout */}
            <div className="p-4 border-t border-border">
              <Button
                onClick={handleLogout}
                variant="ghost"
                className="w-full justify-start text-muted-foreground hover:text-foreground"
              >
                <LogOut className="mr-3 h-5 w-5" />
                Logout
              </Button>
            </div>
          </div>
        </aside>

        {/* Mobile Top Bar */}
        <div className="md:hidden fixed top-0 left-0 right-0 z-10 flex items-center justify-between h-16 px-4 border-b border-border bg-card">
          <h1 className="text-xl font-bold">
            <span className="text-primary">Budget</span>
            <span className="text-foreground">Wise</span>
          </h1>
          <Button onClick={handleLogout} variant="ghost" size="sm">
            <LogOut className="h-5 w-5" />
          </Button>
        </div>

        {/* Main Content */}
        <main className="md:pl-64 pt-16 md:pt-0 pb-16 md:pb-0 min-h-screen">
          {children}
        </main>

        {/* Mobile Bottom Navigation */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 z-10 flex items-center justify-around h-16 border-t border-border bg-card">
          {navigation.slice(0, 4).map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex flex-col items-center justify-center flex-1 h-full ${
                  isActive ? "text-primary" : "text-muted-foreground"
                }`}
              >
                <item.icon className="h-6 w-6" />
                <span className="text-xs mt-1">{item.name}</span>
              </Link>
            );
          })}
          <Link
            href="/settings"
            className={`flex flex-col items-center justify-center flex-1 h-full ${
              pathname === "/settings" ? "text-primary" : "text-muted-foreground"
            }`}
          >
            <Settings className="h-6 w-6" />
            <span className="text-xs mt-1">Settings</span>
          </Link>
        </nav>
      </div>
    </ProtectedRoute>
  );
}
