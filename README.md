# BudgetWise 💰

An AI-powered personal finance assistant that helps you make smarter spending decisions, track expenses, and manage your budget intelligently.

This project was built for HackRU's Fall 2025 Hackathon!

## Features

- 🤖 **AI Financial Assistant** - Chat with an AI advisor for personalized financial guidance
- 📊 **Budget Tracking** - Monitor your spending across categories with smart limits
- 🎯 **Purchase Analysis** - Get AI recommendations before making purchases
- 📈 **Spending Insights** - Visualize patterns and receive actionable insights
- 🏷️ **Smart Categorization** - Automatic expense categorization with ML
- 🔐 **Secure Authentication** - Built with Supabase Auth

## Tech Stack

### Frontend
- **Next.js 15**
- **TypeScript**
- **Tailwind CSS**

### Backend
- **FastAPI** 
- **OpenAI API** 
- **Supabase** 
- **Docker** 

## Getting Started

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.12+**
- **Docker** and Docker Compose
- **Supabase Account** (for database & auth)
- **OpenAI API Key** (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/iddobarnoon/BudgetWise.git
   cd BudgetWise
   ```

2. **Set up environment variables**

   Create `.env` in the project root:
   ```bash
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   DATABASE_URL=your_database_connection_string

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key

   # Backend Configuration
   BACKEND_URL=http://localhost:8000
   ```

   Create `src/frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start the backend services with Docker**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - Auth Service (port 8001)
   - Budget Engine (port 8002)
   - Ranking System (port 8003)
   - AI Pipeline (port 8004)

4. **Install frontend dependencies**
   ```bash
   cd src/frontend
   npm install
   ```

5. **Start the frontend development server**
   ```bash
   npm run dev
   ```

6. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

## API Endpoints

### AI Pipeline Service (Port 8004)
- `POST /api/chat` - Chat with AI financial assistant
- `POST /api/analyze-purchase` - Get purchase recommendations
- `POST /api/extract-expense` - Extract expense details from text

### Budget Engine (Port 8002)
- `GET /api/budget/summary` - Get budget overview
- `POST /api/budget/allocate` - Allocate budget across categories
- `GET /api/budget/insights` - Get spending insights

### Auth Service (Port 8001)
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

## Database Schema

Key tables in Supabase:
- `users` - User profiles and preferences
- `conversations` - Chat message history
- `expenses` - User transactions
- `categories` - Spending categories
- `user_category_preferences` - Custom category priorities
- `budget_allocations` - Budget tracking

## Development

### Running Backend Services Individually

```bash
# Auth Service
cd src/backend/components/auth-service
python main.py

# Budget Engine
cd src/backend/components/budget-engine
python main.py

# AI Pipeline
cd src/backend/components/pipeline
python main.py
```

### Running Frontend in Development Mode

```bash
cd src/frontend
npm run dev
```

### Building for Production

```bash
# Frontend
cd src/frontend
npm run build
npm start

# Backend (Docker)
docker-compose up --build
```

## Environment Variables

### Backend (.env)
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon/service key
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for GPT-4
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)

### Frontend (.env.local)
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase URL (client-side)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key (client-side)
- `NEXT_PUBLIC_API_URL` - Backend API base URL

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for GPT-4 API
- FastAPI for high-performance backend framework


---

Built with ❤️ by [Iddo Barnoon](https://github.com/iddobarnoon), [Itamar Amsalem](https://github.com/itamaramsalem) & [Elad Litvin](https://github.com/Darthelad)