# AI Procurement Assistant — Frontend Chat Interface

A modern, premium conversational chat interface for an AI-powered procurement data assistant. The app helps California state procurement professionals ask natural language questions about purchase order data (2012–2015) and get instant insights.

## Tech Stack
- React + TypeScript + Vite
- Tailwind CSS for styling
- shadcn/ui components
- Lucide React icons

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```
2. **Set up environment**
   Create a `.env` file:
   ```env
   VITE_API_URL=http://localhost:8000
   ```
3. **Run development server**
   ```bash
   npm run dev
   ```

## Pages & Layout

### Chat Interface
A full-screen chat application featuring:

1. **Sidebar**
   - Collapsible navigation
   - "Suggested Questions" chips for quick queries
   - Logo and subtitle

2. **Main Chat Area**
   - Threaded message view
   - Markdown rendering for AI responses
   - Typing indicators
   - Auto-scroll to latest message

3. **Input Area**
   - Sticky bottom bar
   - Enter to send, Shift+Enter for new lines

## API Integration

The frontend communicates with the FastAPI backend via:

- **POST /chat**: Sends user message, receives streaming-like response
- **GET /health**: Checks backend status

## Design System

- **Theme**: Dark mode default ("Deep Navy" palette)
- **Typography**: Inter (Google Fonts)
- **Styling**: Tailwind CSS with custom animations (slide-in, pulse)
- **Components**: Glassmorphism effects, responsive layout

## Development

The project uses Vite for fast HMR.
- `src/components`: UI components
- `src/lib`: API client and utilities
- `src/pages`: Main application views
