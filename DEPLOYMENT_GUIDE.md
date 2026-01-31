# Deployment Guide: AI Trip Planner

This guide outlines the steps to deploy your **React Frontend to Vercel** and **FastAPI Backend to Render**.

## Prerequisites

1.  **GitHub Repository**: Ensure your project is pushed to a GitHub repository.
2.  **Accounts**:
    *   [Render Account](https://render.com/) (for Backend)
    *   [Vercel Account](https://vercel.com/) (for Frontend)

---

## Part 1: Prepare Your Project

### 1. Backend Preparation
Ensure your `requirements.txt` is in the root directory (which it is).
Ensure your `backend/main.py` uses the `PORT` environment variable or defaults to 8000. Render provides the port in the `$PORT` env var.

**Action**: We need to make sure your `backend/main.py` listens on `0.0.0.0`. Uvicorn handles this via the start command, so no code changes are strictly necessary if we use the correct command.

### 2. Frontend Preparation
Your `frontend/package.json` currently has a `homepage` field set to a GitHub Pages URL:
`"homepage": "https://harshkr04.github.io/AI-Trip-Planner"`

**Action**: You should remove this line or clear it before deploying to Vercel, otherwise your assets might fail to load if Vercel serves them from the root.

---

## Part 2: Deploy Backend to Render

1.  **Log in to Render** and click **"New +"** -> **"Web Service"**.
2.  **Connect your GitHub repository**.
3.  **Configure the Service**:
    *   **Name**: `ai-trip-planner-backend` (or similar)
    *   **Region**: Choose one close to you (e.g., Singapore, Frankfurt, Ohio).
    *   **Branch**: `main` (or your working branch).
    *   **Root Directory**: Leave empty (defaults to repo root).
    *   **Runtime**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables** (Scroll down to "Advanced"):
    Add the following keys (values from your `.env` file):
    *   `OPENAI_API_KEY`: `sk-...`
    *   `JWT_SECRET`: `your_secret_key`
    *   `JWT_ALGORITHM`: `HS256`
    *   `FRONTEND_ORIGIN`: `https://your-vercel-app-name.vercel.app` (You will update this *after* deploying the frontend, for now you can put `*` or leave it blank if your CORS allows it).
5.  **Click "Create Web Service"**.
6.  **Wait for Deployment**: Render will install dependencies and start the server.
7.  **Copy the URL**: Once live, copy the backend URL (e.g., `https://ai-trip-planner-backend.onrender.com`).

> **Note on Database**: Your project uses SQLite (`sql_app.db`). On Render's free tier, the filesystem is ephemeral. This means **data will be lost every time the server restarts** (which happens frequently on free tier). For production, you should use Render's PostgreSQL service, but for a demo, SQLite is fine (just know data won't persist).

---

## Part 3: Deploy Frontend to Vercel

1.  **Log in to Vercel** and click **"Add New..."** -> **"Project"**.
2.  **Import your GitHub repository**.
3.  **Configure the Project**:
    *   **Framework Preset**: Create React App (should detect automatically).
    *   **Root Directory**: Click "Edit" and select `frontend`. **This is crucial.**
4.  **Environment Variables**:
    *   Expand "Environment Variables".
    *   Add `REACT_APP_API_URL` with the value of your **Render Backend URL** (from Part 2).
        *   Example: `https://ai-trip-planner-backend.onrender.com` (No trailing slash is usually best, depending on how you concatenated it in your code).
5.  **Click "Deploy"**.
6.  **Wait for Deployment**: Vercel will build your React app.

---

## Part 4: Final Configuration

1.  **Update Backend CORS**:
    *   Go back to your **Render Dashboard**.
    *   Go to "Environment" settings.
    *   Update `FRONTEND_ORIGIN` to your new **Vercel App URL** (e.g., `https://ai-trip-planner.vercel.app`).
    *   Render will automatically restart the service.

2.  **Test**:
    *   Open your Vercel URL.
    *   Try to Log In (remember, if the backend restarted, your user might be gone if using SQLite, so Register again).
    *   Test the features.

---

## Troubleshooting

*   **Frontend 404s**: If assets fail to load, check `frontend/package.json` and remove the `"homepage"` field.
*   **Backend Connection Failed**: Check the Network tab in browser dev tools.
    *   If requests go to `localhost:8000`, you didn't set `REACT_APP_API_URL` correctly in Vercel.
    *   If requests fail with CORS error, check `FRONTEND_ORIGIN` in Render.
*   **"Not Found" on Refresh**: In React Single Page Apps (SPA), refreshing a sub-page (like `/login`) might cause a 404 on Vercel.
    *   **Fix**: Create a `vercel.json` file in your `frontend` folder with this content:
        ```json
        {
          "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
        }
        ```
