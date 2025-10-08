import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'BudgetWise - Smart Budget Management',
  description: 'AI-powered budget management and expense tracking',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
