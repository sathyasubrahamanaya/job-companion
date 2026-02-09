# JobCompanionAI Frontend

A modern SvelteKit frontend for the JobCompanionAI platform - an AI-powered job matching and recruitment system.

## Features

### For Candidates
- **Smart Resume Upload**: AI automatically extracts skills, experience, and education from PDFs
- **Semantic Job Search**: AI-powered search that understands context and intent
- **AI Interview Practice**: Chat with an AI interviewer to practice before real interviews
- **Profile Dashboard**: View and manage your profile, skills, and preferences

### For Employers
- **Company Onboarding**: Create rich company profiles to attract talent
- **Job Posting**: Post jobs with AI-powered candidate matching
- **Job Management**: Edit, delete, and track all your job postings
- **Candidate Search**: Find candidates using semantic search

## Tech Stack

- **Framework**: SvelteKit 2.0
- **Language**: TypeScript
- **Styling**: TailwindCSS 3.4
- **HTTP Client**: Axios
- **State Management**: Svelte Stores

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

\`\`\`bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
\`\`\`

The application will be available at `http://localhost:5173`

## Project Structure

\`\`\`
src/
├── lib/
│   ├── api/           # API client and endpoint functions
│   ├── components/    # Reusable Svelte components
│   └── stores/        # Svelte stores for state management
├── routes/            # SvelteKit file-based routing
│   ├── candidate/     # Candidate-specific pages
│   ├── employer/      # Employer-specific pages
│   ├── login/         # Authentication pages
│   └── signup/        # Registration pages
├── app.css            # Global styles and TailwindCSS
└── app.html           # HTML template
\`\`\`

## Environment Configuration

The frontend connects to the backend API at `http://localhost:8000` by default. To change this, modify the `API_BASE_URL` in `src/lib/api/client.ts`.

## Features Breakdown

### Authentication
- JWT-based authentication
- Role-based access control (Candidate/Employer)
- Persistent login with localStorage

### Candidate Features
- Resume upload with AI parsing
- AI-powered job search
- JobInterview chat interface
- Profile management

### Employer Features
- Company profile creation
- Job posting with skills tagging
- Job listing management
- AI-powered candidate matching

## API Integration

All API calls go through `src/lib/api/client.ts` which:
- Adds JWT tokens to requests automatically
- Handles authentication errors
- Provides consistent error handling

## Development Notes

- The app uses TypeScript for type safety
- All API types are defined in `src/lib/api/types.ts` based on the OpenAPI spec
- State is managed using Svelte stores in `src/lib/stores/`
- Toast notifications provide user feedback throughout the app

## License

MIT
