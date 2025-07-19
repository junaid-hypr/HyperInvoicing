# HyperInvoicing

## Group : In Turn, Sheep

HyperInvoicing is an advanced invoicing platform that automates customer invoice management, streamlines payment tracking, and enhances accuracy through AI-assisted validation. The system is composed of a FastAPI backend and a modern React (Vite + shadcn-ui + Tailwind CSS) frontend, working together to provide a seamless user experience for generating, tracking, and managing invoices.

## Project Architecture & How It Works

- **Backend (FastAPI + MongoDB):**
  - Exposes REST API endpoints for invoice management and analytics.
  - Connects to a MongoDB database to store and retrieve invoice data.
  - Fetches document counts (invoices, purchase requisitions, accruals) for different periods (monthly, quarterly, yearly) by integrating with external APIs.
  - Provides endpoints to:
    - Get document counts for a given period (`GET /{period}`)
  - Handles CORS to allow frontend communication during development.

- **Frontend (React + Vite + shadcn-ui):**
  - User interface for creating, previewing, and tracking invoices.
  - Allows users to select document types, billing periods, and enter customer details.
  - Fetches analytics and document counts from the backend to assist in invoice generation and pricing.
  - Displays a dashboard with invoice statuses (Pending, Sent, Paid, Overdue) and allows status updates.
  - Generates PDF previews of invoices and provides download links.
  - Uses modern UI components and responsive design for a smooth user experience.

- **Interaction Flow:**
  1. User interacts with the frontend to create or view invoices.
  2. Frontend calls backend API endpoints to fetch document counts, save new invoices, retrieve invoice lists, and update statuses.
  3. Backend processes requests, interacts with MongoDB and external APIs, and returns results to the frontend.
  4. Frontend displays real-time updates and analytics to the user.

## Main Features
- Animated loading screen with AI character (Vera)
- Invoice generation with customer details, document type, and billing period
- Analytics dashboard for invoice statuses and metrics
- Approval workflow and status management
- PDF invoice preview and download
- Modern, responsive UI with consistent branding

---

## How to Run the Project

### Backend (FastAPI)

1. Install dependencies:
   ```bash
   pip install motor fastapi uvicorn python-dotenv
   ```
2. Set up your `.env` file in the `backend/` directory with your MongoDB connection string:
   ```env
   MONGO_DETAILS=<your-mongodb-connection-string>
   ```
3. Add Hyperbots API Token in `backend\main.py` for the backend to function correctly:
   ```env
   COOKIE   = f"<Hyperbots Token>"
   ```
4. Add Org_ID and User_ID as well without which API wont work:
   ```env
   ORG_ID   = "<Org ID>"
   USER_ID  = "<User ID>"
   ```
4. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```
   The backend will be running at `http://localhost:8000/`.

### Frontend (React + Vite)

1. Go to the frontend directory:
   ```bash
   cd workspace/shadcn-ui
   ```
2. Install dependencies:
   ```bash
   npm install
   # or
   pnpm install
   ```
3. Start the frontend development server:
   ```bash
   npm run dev
   # or
   pnpm run dev
   ```
   The frontend will be available at `http://localhost:5173/`.

---

For more details, see the `workspace/shadcn-ui/README.md` file.
