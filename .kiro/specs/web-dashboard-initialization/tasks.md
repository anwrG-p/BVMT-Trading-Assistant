# Implementation Plan: Web Dashboard Initialization

## Overview

This implementation plan breaks down the initialization of the BVMT Trading Assistant web dashboard into discrete, actionable tasks. Each task builds incrementally on previous work, ensuring the project structure, Docker configuration, and UI foundation are properly established before moving forward.

## Tasks

- [ ] 1. Initialize Next.js project with TypeScript and Tailwind CSS
  - Create web-dashboard directory in project root
  - Run `npx create-next-app@latest` with TypeScript, Tailwind CSS, ESLint, and App Router options
  - Verify package.json contains Next.js 14+ and required dependencies
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 1.1 Write unit tests for project initialization
  - Test that web-dashboard directory exists
  - Test that package.json contains correct Next.js version
  - Test that tsconfig.json and tailwind.config.ts exist
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 2. Set up modular directory structure
  - [ ] 2.1 Create src directory structure
    - Create src/components/ directory for UI components
    - Create src/app/ directory (should exist from Next.js init)
    - Create src/lib/ directory for utilities and Prisma client
    - Create src/hooks/ directory for custom React hooks
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 2.2 Write property test for directory structure
    - **Property 1: Required project structure exists**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [ ] 3. Configure Prisma with PostgreSQL
  - [ ] 3.1 Install and initialize Prisma
    - Install @prisma/client and prisma as dev dependency
    - Run `npx prisma init` to create prisma directory and schema
    - Update schema.prisma with PostgreSQL datasource and placeholder User model
    - _Requirements: 3.3_
  
  - [ ] 3.2 Create Prisma client singleton
    - Create src/lib/prisma.ts with singleton pattern
    - Implement proper client instantiation for development and production
    - _Requirements: 2.3_
  
  - [ ]* 3.3 Write unit tests for Prisma configuration
    - Test that schema.prisma exists and is valid
    - Test that Prisma client can be imported
    - _Requirements: 3.3_

- [ ] 4. Set up Docker configuration
  - [ ] 4.1 Create Dockerfile for Next.js application
    - Create multi-stage Dockerfile with base, deps, builder, and runner stages
    - Configure for production builds with standalone output
    - Include Prisma generate step in builder stage
    - _Requirements: 3.4_
  
  - [ ] 4.2 Create docker-compose.yml
    - Define web service with build context pointing to web-dashboard
    - Define db service using postgres:16-alpine image
    - Configure environment variables for both services
    - Set up volumes for PostgreSQL data persistence
    - Configure networking between services
    - Expose ports 3000 (web) and 5432 (db)
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  
  - [ ]* 4.3 Write property tests for Docker configuration
    - **Property 2: Required configuration files exist**
    - **Property 5: Docker services are properly configured**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [ ] 5. Update Next.js configuration
  - [ ] 5.1 Configure next.config.js
    - Enable React strict mode
    - Configure output: 'standalone' for Docker
    - Set up image domains if needed
    - _Requirements: 1.2_
  
  - [ ] 5.2 Update tsconfig.json with path aliases
    - Ensure @/* alias points to ./src/*
    - Verify all TypeScript compiler options are correct
    - _Requirements: 1.3_

- [ ] 6. Install and configure shadcn/ui
  - [ ] 6.1 Initialize shadcn/ui
    - Run `npx shadcn-ui@latest init`
    - Configure with default style, slate base color, and CSS variables
    - Verify components.json is created with correct configuration
    - _Requirements: 4.1_
  
  - [ ] 6.2 Install required shadcn/ui components
    - Run `npx shadcn-ui@latest add button`
    - Run `npx shadcn-ui@latest add card`
    - Run `npx shadcn-ui@latest add input`
    - Verify components are created in src/components/ui/
    - _Requirements: 4.2, 4.3, 4.4, 4.6_
  
  - [ ] 6.3 Create custom Navbar component
    - Create src/components/navbar.tsx
    - Implement navigation using Button component and Next.js Link
    - Include branding and navigation links
    - _Requirements: 4.5_
  
  - [ ]* 6.4 Write property test for shadcn/ui components
    - **Property 4: shadcn/ui components are installed**
    - **Validates: Requirements 4.2, 4.3, 4.4, 4.5, 4.6**

- [ ] 7. Create utility functions
  - Create src/lib/utils.ts with cn() helper function
  - Import clsx and tailwind-merge
  - _Requirements: 2.3_

- [ ] 8. Implement root layout and home page
  - [ ] 8.1 Create root layout
    - Update src/app/layout.tsx with Navbar component
    - Configure Inter font from next/font/google
    - Set up metadata (title, description)
    - Add container wrapper for main content
    - _Requirements: 1.2, 2.2_
  
  - [ ] 8.2 Create home page
    - Update src/app/page.tsx with welcome content
    - Use Card and Button components from shadcn/ui
    - Implement basic responsive layout
    - _Requirements: 1.2, 2.2_
  
  - [ ] 8.3 Update global styles
    - Configure src/app/globals.css with Tailwind directives
    - Add CSS variables for shadcn/ui theming
    - _Requirements: 1.4_

- [ ] 9. Configure Git ignore rules
  - [ ] 9.1 Update .gitignore
    - Ensure node_modules is excluded
    - Ensure .env and .env.local are excluded
    - Ensure .next directory is excluded
    - Add other Next.js and IDE-specific exclusions
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 9.2 Write property test for gitignore configuration
    - **Property 6: Gitignore excludes required patterns**
    - **Validates: Requirements 5.2, 5.3, 5.4**

- [ ] 10. Create environment configuration
  - Create .env.example with DATABASE_URL and NODE_ENV
  - Document required environment variables
  - _Requirements: 3.2, 3.3_

- [ ] 11. Add package.json scripts
  - Add scripts for dev, build, start, lint
  - Add Prisma scripts (generate, migrate)
  - Add Docker scripts (docker:up, docker:down)
  - _Requirements: 1.2, 3.5_

- [ ] 12. Checkpoint - Verify project structure and configuration
  - Ensure all required directories exist
  - Ensure all configuration files are valid
  - Ensure no ML or NLP code exists in the project
  - Ask the user if questions arise

- [ ]* 12.1 Write property test for scope constraints
  - **Property 7: No ML or NLP implementation exists**
  - **Validates: Requirements 6.1, 6.2**

- [ ] 13. Test Docker setup
  - [ ] 13.1 Build Docker images
    - Run `docker-compose build` to build web service image
    - Verify build completes without errors
    - _Requirements: 3.4, 3.5_
  
  - [ ] 13.2 Start Docker services
    - Run `docker-compose up -d` to start services
    - Verify both web and db services are running
    - Check logs for any errors
    - _Requirements: 3.5_
  
  - [ ] 13.3 Verify application accessibility
    - Access http://localhost:3000 in browser
    - Verify home page renders correctly
    - Verify Navbar is displayed
    - _Requirements: 1.2, 3.5_

- [ ] 14. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify Docker services are running correctly
  - Ensure all requirements are met
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and configuration
- Docker testing is primarily manual verification during development
- The project focuses exclusively on infrastructure setup with no ML/NLP logic
