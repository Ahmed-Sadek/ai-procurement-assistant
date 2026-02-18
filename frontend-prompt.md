# AI Procurement Assistant — Frontend Chat Interface

Build a modern, premium conversational chat interface for an AI-powered procurement data assistant. The app helps California state procurement professionals ask natural language questions about purchase order data (2012–2015) and get instant insights.

## Tech Stack
- React + TypeScript + Vite
- Tailwind CSS for styling
- No authentication needed

## API Integration

The backend is a FastAPI server running at `http://localhost:8000`. CORS is enabled.

### Endpoints

**POST /chat**
```json
// Request
{ "message": "What are the top 5 departments by spending?" }

// Response
{ "reply": "The top 5 departments by spending are:\n1. Corrections and Rehabilitation — $2.1B\n2. ..." }
```

**GET /health**
```json
// Response
{ "status": "ok" }
```

## Pages & Layout

### Single Page App — Chat Interface

A full-screen chat application with:

1. **Left Sidebar (collapsible)**
   - App logo/title: "Procurement AI Assistant"
   - Subtitle: "California State Purchase Orders 2012–2015"
   - Section: "Suggested Questions" with clickable chips:
     - "How many total purchase orders are there?"
     - "What are the top 10 vendors by spending?"
     - "Which quarter had the highest spending?"
     - "What are the most frequently ordered items?"
     - "Show IT Goods orders from 2014"
     - "Which departments use CalCard the most?"
   - Clicking a chip sends it as a message immediately

2. **Main Chat Area**
   - Clean message thread with user messages (right-aligned, accent color) and assistant messages (left-aligned, neutral card)
   - Assistant messages should render markdown (bold, lists, numbers, tables)
   - Show a typing indicator (animated dots) while waiting for the API response
   - Auto-scroll to latest message
   - Empty state: Show a welcome message with the app name and a brief description: "Ask me anything about California state procurement data — spending trends, top vendors, department analysis, and more."

3. **Chat Input Bar (bottom, sticky)**
   - Full-width text input with placeholder: "Ask about procurement data..."
   - Send button (icon) on the right
   - Submit on Enter key, Shift+Enter for new line
   - Disable send while waiting for response

## Design Requirements

- **Dark mode by default** with a sleek, professional feel
- Color palette: Deep navy/slate background, subtle blue-purple accent for user messages, clean white/light gray for assistant messages
- Modern typography — use Inter or similar clean sans-serif from Google Fonts
- Smooth animations: messages slide in, typing indicator pulses
- Glassmorphism effect on the sidebar
- Responsive: works on desktop and tablet (sidebar collapses on smaller screens)
- The overall look should feel like a premium enterprise analytics tool, not a toy chatbot

## Key Behaviors

- On first load, display the welcome empty state
- When user sends a message, immediately show it in the thread and show the typing indicator
- Call `POST /chat` with the message, then display the reply
- If the API call fails, show an inline error message: "Something went wrong. Please try again."
- Maintain chat history in component state (no persistence needed)
- The sidebar suggested questions should always be accessible for quick queries

## Environment

Add a `.env` file with:
```
VITE_API_URL=http://localhost:8000
```

Use this throughout the app for API calls.
