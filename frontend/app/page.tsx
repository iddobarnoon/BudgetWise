'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('user_id');

    if (token && userId) {
      // User is logged in, go to chat
      router.push('/chat');
    } else {
      // User is not logged in, go to register
      router.push('/register');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">BudgetWise</h1>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
