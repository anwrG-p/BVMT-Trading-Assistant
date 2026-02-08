# Design Document: Web Dashboard Initialization

## Overview

This design outlines the initialization of a Next.js 14+ web dashboard for the BVMT Trading Assistant. The dashboard will use the App Router architecture, TypeScript for type safety, Tailwind CSS for styling, and shadcn/ui for UI components. The entire stack will be containerized using Docker with PostgreSQL as the database.

The design focuses exclusively on project scaffolding, directory structure, Docker configuration, and UI component setup. No business logic, ML models, or NLP functionality will be implemented at this stage.

## Architecture

### Technology Stack

- **Frontend Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.x
- **UI Components**: shadcn/ui (built on Radix UI)
- **Database**: PostgreSQL 16
- **ORM**: Prisma
- **Containerization**: Docker & Docker Compose
- **Code Quality**: ESLint

### Project Structure

```
web-dashboard/
├── src/
│   ├── app/                    # Next.js App Router pages and layouts
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   ├── components/             # React components
│   │   └── ui/                 # shadcn/ui components
│   ├── lib/                    # Utility functions and clients
│   │   ├── utils.ts            # Helper functions
│   │   └── prisma.ts           # Prisma client singleton
│   └── hooks/                  # Custom React hooks
├── prisma/
│   └── schema.prisma           # Database schema
├── public/                     # Static assets
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── Dockerfile                  # Next.js container definition
├── docker-compose.yml          # Multi-container orchestration
├── next.config.js              # Next.js configuration
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
├── components.json             # shadcn/ui configuration
└── package.json                # Dependencies and scripts
```

### Docker Architecture

The application will use a multi-container setup:

1. **Web Service (Next.js)**
   - Built from custom Dockerfile
   - Exposes port 3000
   - Connects to PostgreSQL via internal network
   - Hot-reload enabled for development

2. **Database Service (PostgreSQL)**
   - Uses official PostgreSQL 16 image
   - Exposes port 5432
   - Persistent volume for data storage
   - Environment-based configuration

## Components and Interfaces

### Next.js Configuration

**next.config.js**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable strict mode for better error handling
  reactStrictMode: true,
  // Optimize images
  images: {
    domains: [],
  },
}

module.exports = nextConfig
```

### TypeScript Configuration

**tsconfig.json**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Tailwind Configuration

**tailwind.config.ts**
```typescript
import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
```

### Docker Configuration

**Dockerfile**
```dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Generate Prisma Client
RUN npx prisma generate

# Build Next.js
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build:
      context: ./web-dashboard
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/bvmt_dashboard
      - NODE_ENV=development
    volumes:
      - ./web-dashboard:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - db
    networks:
      - bvmt-network

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=bvmt_dashboard
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - bvmt-network

volumes:
  postgres_data:

networks:
  bvmt-network:
    driver: bridge
```

### Prisma Configuration

**prisma/schema.prisma**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Placeholder model - to be expanded in future iterations
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

**src/lib/prisma.ts**
```typescript
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

### shadcn/ui Configuration

**components.json**
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui"
  }
}
```

### UI Components

The following shadcn/ui components will be installed:

1. **Button** - Interactive button component with variants
2. **Card** - Container component for content grouping
3. **Input** - Form input component with validation support
4. **Navbar** - Navigation component (custom implementation using shadcn primitives)

**Example Navbar Component (src/components/navbar.tsx)**
```typescript
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export function Navbar() {
  return (
    <nav className="border-b">
      <div className="flex h-16 items-center px-4 container mx-auto">
        <Link href="/" className="font-bold text-xl">
          BVMT Trading Assistant
        </Link>
        <div className="ml-auto flex items-center space-x-4">
          <Button variant="ghost" asChild>
            <Link href="/dashboard">Dashboard</Link>
          </Button>
          <Button variant="ghost" asChild>
            <Link href="/analytics">Analytics</Link>
          </Button>
        </div>
      </div>
    </nav>
  )
}
```

### Root Layout

**src/app/layout.tsx**
```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Navbar } from '@/components/navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'BVMT Trading Assistant',
  description: 'Web dashboard for BVMT Trading Assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar />
        <main className="container mx-auto py-6">
          {children}
        </main>
      </body>
    </html>
  )
}
```

### Home Page

**src/app/page.tsx**
```typescript
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold">Welcome to BVMT Trading Assistant</h1>
      <Card className="p-6">
        <h2 className="text-2xl font-semibold mb-4">Getting Started</h2>
        <p className="text-muted-foreground mb-4">
          This is the web dashboard for the BVMT Trading Assistant.
        </p>
        <Button>Explore Dashboard</Button>
      </Card>
    </div>
  )
}
```

### Utility Functions

**src/lib/utils.ts**
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## Data Models

At this initialization stage, only a placeholder User model is defined in Prisma. This establishes the database connection and ORM setup without implementing business logic.

**User Model**
- `id`: Unique identifier (CUID)
- `email`: Unique email address
- `name`: Optional user name
- `createdAt`: Timestamp of creation
- `updatedAt`: Timestamp of last update

Future iterations will expand the data models to include trading data, ML model results, and other domain-specific entities.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Required project structure exists

*For any* initialized web-dashboard project, all required directories (src/components/, src/app/, src/lib/, src/hooks/) SHALL exist at their expected paths.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

### Property 2: Required configuration files exist

*For any* initialized web-dashboard project, all required configuration files (package.json, tsconfig.json, tailwind.config.ts, next.config.js, components.json, docker-compose.yml, Dockerfile, .gitignore, prisma/schema.prisma) SHALL exist at their expected paths.

**Validates: Requirements 1.1, 1.3, 1.4, 1.5, 3.1, 3.4, 4.1, 5.1**

### Property 3: Next.js version and App Router configuration

*For any* initialized web-dashboard project, the package.json SHALL specify Next.js version 14 or higher, and the src/app directory SHALL exist indicating App Router is enabled.

**Validates: Requirements 1.2**

### Property 4: shadcn/ui components are installed

*For any* initialized web-dashboard project, the required shadcn/ui component files (button.tsx, card.tsx, input.tsx) and custom navbar component SHALL exist in the components directory.

**Validates: Requirements 4.2, 4.3, 4.4, 4.5, 4.6**

### Property 5: Docker services are properly configured

*For any* initialized web-dashboard project, the docker-compose.yml SHALL define both a "web" service with Next.js configuration and a "db" service with PostgreSQL image specification.

**Validates: Requirements 3.2, 3.3**

### Property 6: Gitignore excludes required patterns

*For any* initialized web-dashboard project, the .gitignore file SHALL contain exclusion patterns for node_modules, .env, and .next directories.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 7: No ML or NLP implementation exists

*For any* initialized web-dashboard project, the codebase SHALL NOT contain any files, imports, or dependencies related to machine learning models or natural language processing logic.

**Validates: Requirements 6.1, 6.2**

## Error Handling

### Configuration Errors

**Missing Dependencies**
- If required npm packages are not installed, the build process will fail with clear error messages
- Solution: Run `npm install` to install all dependencies from package.json

**Invalid TypeScript Configuration**
- If tsconfig.json is misconfigured, TypeScript compilation will fail
- Solution: Validate tsconfig.json against Next.js requirements

**Docker Build Failures**
- If Dockerfile has syntax errors or missing dependencies, docker build will fail
- Solution: Review Dockerfile syntax and ensure all required files are copied

### Database Connection Errors

**PostgreSQL Connection Failure**
- If DATABASE_URL is incorrect or PostgreSQL is not running, Prisma will fail to connect
- Solution: Verify docker-compose services are running and DATABASE_URL is correct

**Prisma Schema Errors**
- If schema.prisma has syntax errors, Prisma generate will fail
- Solution: Validate Prisma schema syntax

### Runtime Errors

**Port Conflicts**
- If port 3000 or 5432 is already in use, Docker services will fail to start
- Solution: Stop conflicting services or modify port mappings in docker-compose.yml

**Missing Environment Variables**
- If required environment variables are not set, the application may fail at runtime
- Solution: Create .env file based on .env.example

## Testing Strategy

### Unit Testing Approach

For this initialization phase, testing focuses on verifying the project structure and configuration rather than business logic. Unit tests will validate:

1. **File Existence Tests**: Verify all required files and directories exist
2. **Configuration Validation Tests**: Parse and validate configuration files (package.json, tsconfig.json, docker-compose.yml)
3. **Component Import Tests**: Verify shadcn/ui components can be imported without errors
4. **Prisma Client Tests**: Verify Prisma client can be instantiated

**Testing Framework**: Jest with TypeScript support

**Example Unit Test Structure**:
```typescript
describe('Project Structure', () => {
  it('should have all required directories', () => {
    expect(fs.existsSync('src/components')).toBe(true)
    expect(fs.existsSync('src/app')).toBe(true)
    expect(fs.existsSync('src/lib')).toBe(true)
    expect(fs.existsSync('src/hooks')).toBe(true)
  })
})
```

### Property-Based Testing Approach

Property-based testing will be used to verify universal properties across the project configuration. We will use **fast-check** as the property-based testing library for TypeScript/JavaScript.

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number

**Property Test Examples**:

```typescript
import fc from 'fast-check'

describe('Property Tests', () => {
  it('Feature: web-dashboard-initialization, Property 1: Required project structure exists', () => {
    // This is an example-based test since we're checking a specific project
    const requiredDirs = ['src/components', 'src/app', 'src/lib', 'src/hooks']
    requiredDirs.forEach(dir => {
      expect(fs.existsSync(path.join(projectRoot, dir))).toBe(true)
    })
  })

  it('Feature: web-dashboard-initialization, Property 6: Gitignore excludes required patterns', () => {
    const gitignoreContent = fs.readFileSync('.gitignore', 'utf-8')
    const requiredPatterns = ['node_modules', '.env', '.next']
    
    requiredPatterns.forEach(pattern => {
      expect(gitignoreContent).toContain(pattern)
    })
  })
})
```

### Integration Testing

Integration tests will verify that the Docker services work together:

1. **Docker Compose Validation**: Verify docker-compose.yml is valid YAML and can be parsed
2. **Service Connectivity**: Verify web service can connect to database service (manual verification during development)
3. **Build Process**: Verify Docker images can be built successfully

### Testing Balance

For this initialization phase:
- **Unit tests** focus on file existence, configuration validation, and structural verification
- **Property tests** verify universal properties about the project structure
- **Integration tests** are primarily manual verification that Docker services start correctly

Since this is infrastructure setup rather than business logic, most tests will be example-based rather than property-based. Property-based testing will become more valuable in future iterations when implementing business logic and data transformations.

### Test Execution

Tests should be run:
- Before committing changes (pre-commit hook)
- In CI/CD pipeline
- After initial project setup to verify correctness

**Test Commands**:
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## Implementation Notes

### Development Workflow

1. Initialize Next.js project with TypeScript and Tailwind
2. Set up directory structure
3. Configure Docker and docker-compose
4. Initialize Prisma with PostgreSQL
5. Install and configure shadcn/ui
6. Add required UI components
7. Create basic layout and home page
8. Verify Docker services start correctly

### Environment Variables

**.env.example**
```
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/bvmt_dashboard"
NODE_ENV="development"
```

### Package.json Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "prisma:generate": "prisma generate",
    "prisma:migrate": "prisma migrate dev",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down"
  }
}
```

### Future Considerations

This initialization establishes the foundation for future development:

1. **Authentication**: Add NextAuth.js for user authentication
2. **API Routes**: Implement Next.js API routes for backend logic
3. **State Management**: Add state management (Zustand or Redux) if needed
4. **Data Fetching**: Implement data fetching patterns (React Query or SWR)
5. **Testing**: Expand test coverage as business logic is added
6. **CI/CD**: Set up GitHub Actions or similar for automated testing and deployment
7. **Monitoring**: Add error tracking (Sentry) and analytics
8. **Performance**: Optimize bundle size and implement code splitting

The modular structure established in this initialization phase will support these future enhancements without requiring significant refactoring.
