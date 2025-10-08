# BudgetWise Frontend

A simple, clean frontend for BudgetWise with user registration and AI-powered chat for budget management.

## Features

- 👤 User Registration & Authentication
- 💬 AI Chat Interface for budget questions and expense logging
- 📊 Real-time Budget Summary Display
- 💰 Expense Tracking & Categorization
- 💭 Purchase Decision Assistance

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Set Up Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
cp .env.example .env
```

Update the `.env` file with your backend service URLs (default values shown):

```env
NEXT_PUBLIC_AUTH_URL=http://localhost:8001
NEXT_PUBLIC_BUDGET_URL=http://localhost:8003
NEXT_PUBLIC_RANKING_URL=http://localhost:8002
NEXT_PUBLIC_API_URL=http://localhost:8004
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Home page (redirects to register/chat)
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Global styles with Tailwind
│   ├── register/
│   │   └── page.tsx          # User registration
│   ├── login/
│   │   └── page.tsx          # User login
│   └── chat/
│       └── page.tsx          # Main chat interface
├── components/
│   ├── BudgetSummary.tsx     # Budget overview card
│   ├── ChatMessage.tsx       # Individual chat message
│   └── ChatInput.tsx         # Message input with suggestions
└── lib/
    ├── api.ts                # API client functions
    └── types.ts              # TypeScript type definitions
```

## Usage

### 1. Register a New User

- Navigate to `/register` (or root `/`)
- Fill in:
  - Full Name
  - Email
  - Password
  - Monthly Income
- Click "Create account"
- You'll be automatically logged in and redirected to the chat

### 2. Chat Interface

Once logged in, you can:

#### Log Expenses
```
"I spent $50 on groceries"
"Bought gas for $40"
```

#### Get Purchase Advice
```
"Should I buy a $200 jacket?"
"Can I afford a $500 PlayStation?"
```

#### Check Budget
```
"Show me my budget summary"
"How much do I have left?"
```

## API Integration

The frontend connects to four backend services:

1. **Auth Service** (port 8001)
   - User registration
   - Login/logout
   - Token validation

2. **Ranking System** (port 8002)
   - Category classification
   - Expense categorization

3. **Budget Engine** (port 8003)
   - Budget creation
   - Purchase validation
   - Spending tracking

4. **AI Pipeline** (port 8004)
   - Chat interface
   - Natural language processing
   - Expense extraction
   - Purchase recommendations

## Build for Production

```bash
npm run build
npm start
```

## Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client for API calls

## Notes

- The app uses localStorage for authentication tokens
- Budget summary is fetched on page load
- Messages are sent to the AI service which orchestrates calls to other services
- The chat automatically refreshes the budget when expenses are logged
