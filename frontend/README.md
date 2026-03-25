# FireGuard - Frontend

This is the frontend for the FireGuard project, a web application for monitoring and managing fire alerts. It is built with React, TypeScript, and Vite.

## Table of Contents

- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [Available Scripts](#available-scripts)
- [Linting and Formatting](#linting-and-formatting)
- [Building for Production](#building-for-production)
- [Deployment (Nginx)](#deployment-nginx)

## Project Structure

The project follows a standard structure for a Vite-based React application.

```
/
├── public/               # Static assets
├── src/                  # Source code
│   ├── components/       # Reusable UI components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # API clients, utilities, etc.
│   ├── pages/            # Top-level page components
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Main application component
│   └── main.tsx          # Application entry point
├── .env.example          # Example environment variables
├── .eslintrc.js          # ESLint configuration
├── .gitignore            # Git ignore file
├── .prettierrc           # Prettier configuration
├── Dockerfile            # Docker configuration
├── index.html            # Main HTML file
├── nginx.conf            # Nginx configuration for development
├── nginx.prod.conf       # Nginx configuration for production
├── package.json          # Project dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── vite.config.ts        # Vite configuration
```

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
3.  Install the dependencies:
    ```bash
    npm install
    ```

### Environment Variables

Create a `.env` file in the root of the `frontend` directory by copying the `.env.example` file.

```bash
cp .env.example .env
```

Update the variables in the `.env` file as needed.

- `VITE_API_URL`: The base URL for the backend API.
- `VITE_KEYCLOAK_URL`: The URL for the Keycloak authentication server.

## Available Scripts

- `npm run dev`: Starts the development server.
- `npm run build`: Builds the application for production.
- `npm run lint`: Lints the codebase using ESLint.
- `npm run format`: Formats the codebase using Prettier.
- `npm run typecheck`: Checks for TypeScript errors.
- `npm run preview`: Serves the production build locally.
- `npm run test`: Runs tests using Vitest.

## Linting and Formatting

This project uses ESLint for linting and Prettier for code formatting.

- **ESLint**: The configuration is in `.eslintrc.js`. It uses the recommended rules for JavaScript, TypeScript, and React.
- **Prettier**: The configuration is in `.prettierrc`. It is set up to format TypeScript and TSX files. The `.prettierignore` file lists files and directories that should not be formatted.

## Building for Production

To build the application for production, run:

```bash
npm run build
```

This will create a `dist` directory with the optimized and minified production build.

## Deployment (Nginx)

The project includes Nginx configuration files for both development (`nginx.conf`) and production (`nginx.prod.conf`).

The Nginx configuration is set up to:

- Serve the static files from the `dist` directory.
- Proxy API requests to the backend server.
- Proxy authentication requests to the Keycloak server.
- Handle client-side routing for the single-page application (SPA).
- Enable Gzip compression for better performance.
