# JobCheck - Frontend UI

This is the frontend application for **JobCheck**, an advanced, AI-powered web application designed to combat recruitment fraud by detecting fake job postings in real-time. This frontend provides a modern, interactive, and user-friendly interface built with **React** and **Vite**.

## ✨ Features

- **Modern UI/UX**: Built with React for a fast, responsive, and seamless user experience.
- **Real-Time Integration**: Connects with the JobCheck Flask backend API to process job descriptions and display prediction results.
- **Image Scanning (OCR)**: UI components to upload job advertisement screenshots for instant text extraction and analysis.
- **Admin & User Dashboards**: Interfaces for viewing classification confidence scores, system traffic, and model performance.
- **Secure Authentication**: Frontend forms and state management for user login, registration, and role-based access control.

## 🛠️ Tech Stack

- **Framework**: React 19
- **Build Tool**: Vite 8
- **Styling**: Modern CSS
- **Routing**: Client-side routing for seamless navigation

## 🚀 Getting Started

### Prerequisites

Ensure you have [Node.js](https://nodejs.org/) installed on your machine.

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the necessary dependencies:
   ```bash
   npm install
   ```

### Development Server

Start the Vite development server with Hot Module Replacement (HMR):

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or the port specified in your terminal).

### Building for Production

To create an optimized production build:

```bash
npm run build
```

This will generate a `dist` folder with the static assets that can be served by any static file server or integrated with your backend.

## 🔗 Backend Integration

This frontend is designed to work in tandem with the JobCheck Flask backend. Ensure the backend server is running (typically on `http://127.0.0.1:5000`) for full functionality including AI predictions, OCR, and database interactions. See the `backend/Readme.md` for backend setup instructions.
