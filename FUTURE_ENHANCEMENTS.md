## A2S (Aesthetics to Spaces) – Future Enhancements

This document describes recommended future enhancements for both backend and frontend to make the A2S website complete and production-ready.

---

## 1. Backend Enhancements

### 1.1 Architecture & Data Layer

### 1.2 Configuration Management

### 1.3 Authentication & User Management

- **Password lifecycle**
  - `POST /api/users/forgot-password` to request a reset link or token.
  - `POST /api/users/reset-password` to set a new password via a signed short-lived token.
  - Store only `password_hash` in DB and never expose it from APIs.
- **Email verification (optional but recommended)**
  - Add `email_verified` flag and verification tokens.
  - Require verification before certain actions (e.g., saving designs, creating layouts).
- **Roles & authorization**
  - Add `role` column to `users`.
  - Implement `requireAuth` and `requireAdmin` middlewares.
  - Restrict design management and administrative endpoints to admins.
- **Token strategy**
  - Use short-lived access tokens (e.g., 15–30 minutes).
  - Optionally introduce refresh tokens with rotation and revocation support.
  - Centralize token creation/verification in a dedicated auth service module.
- **Validation & typing**
  - Use a validation library (e.g., Zod/Joi) for request bodies (`register`, `login`, `toggleSavedDesign`, etc.).
  - Replace `// @ts-ignore` with a strongly typed `AuthenticatedRequest` interface adding `user` to `Request`.

### 1.4 Designs & Catalog APIs

- **CRUD for designs**
  - Extend `/api/designs` with:
    - `POST /` – create design (admin-only).
    - `PUT /:id` – update design (admin-only).
    - `DELETE /:id` – delete design (admin-only).
  - Validate payloads, especially `products` structure and `tags`.
- **Filtering, sorting, pagination**
  - Enhance `GET /api/designs` with query params:
    - `roomType`, `style`, `budgetMin`, `budgetMax`, `tags[]`, `search`, `sortBy`, `page`, `pageSize`.
  - Respond with:
    - `{ data: Design[], pagination: { page, pageSize, total, hasMore } }`.
- **Saved designs improvements**
  - Optionally move from `saved_designs (text[])` to a `user_saved_designs` table.
  - Add `GET /api/users/saved-designs` that returns full design objects rather than just IDs.
- **Optional product endpoints**
  - If products are normalized:
    - `GET /api/products` with category/brand/price filters.
    - `GET /api/products/:id` for details.

### 1.5 AI Consultant & Vastu Audit

- **Configuration**
  - Move AI configuration (model id, temperature, base prompts) into `config/ai.ts`.
  - Allow overriding model and temperature via environment variables.
- **Robustness & error handling**
  - Introduce structured error codes for AI failures:
    - `AI_UNCONFIGURED`, `AI_GENERATION_FAILED`, `AI_INVALID_OUTPUT`, etc.
  - Add retry logic with backoff for transient Gemini errors.
- **Context & personalization**
  - When authenticated, augment AI context with:
    - User location, style preferences, budget tier, recent activity.
  - Store chat sessions and messages in Supabase for history and analytics.
- **Vastu audit safety**
  - Validate AI JSON against a schema before returning to the client.
  - On invalid JSON:
    - Optionally re-prompt the model with a stricter instruction, or
    - Return a safe fallback payload with a clear error flag.
- **Rate limiting**
  - Apply rate limiting middleware to `/api/chat` and `/api/chat/vastu`:
    - Per-IP and/or per-user quotas.
    - Use in-memory or Redis-backed store depending on scale.

### 1.6 Cross-Cutting Backend Concerns

- **Central error handler**
  - Add an error-handling middleware that converts thrown errors to a consistent JSON format.
  - Refactor controllers to use `next(err)` instead of manually handling all errors inline.
- **Logging & monitoring**
  - Use structured logging (e.g., `pino` or `winston`) for:
    - Requests, responses (with minimal sensitive data).
    - Errors and AI requests (with masked inputs where needed).
  - Integrate Sentry or similar for error tracking in production.
- **Security**
  - Add `helmet` for security headers.
  - Restrict CORS to known frontend origins in production.
  - Sanitize all inputs before DB or AI calls.
  - Review and periodically rotate JWT secrets if feasible.
- **Testing**
  - Set up Jest or Vitest for:
    - Unit tests (controllers, middleware, util functions).
    - Integration tests for major flows (auth, designs, AI endpoints).
  - Replace the current placeholder `npm test` script with a real test runner configuration.

---

## 2. Frontend Enhancements (Planned)

> Note: The current repository does not contain a frontend implementation. The following is a proposed plan to build a complete frontend aligned with the backend and product goals.

### 2.1 Core Application Structure

- **Framework**
  - Use Next.js (recommended) or React SPA with a modern bundler.
  - Benefits: SEO for Gallery/design pages, file-based routing, good DX.
- **Primary pages**
  - **Home**
    - High-level intro to A2S.
    - CTAs to Gallery, 3D Studio, Style Quiz, and AI Consultant.
  - **Gallery**
    - Displays designs from `/api/designs` using filters for room, style, budget, and tags.
    - Shows design cards (image, title, room, style, total cost, tags, save button).
  - **Design Detail**
    - Uses `/api/designs/:id` to show:
      - Large hero image, description, meta (room, style, budget).
      - Product list with “Shop the look” (names, brands, prices, links).
      - Actions: save design, open in 3D Studio, ask AI about this design.
  - **3D Studio**
    - Room layout editor for placing furniture/decor.
    - MVP: 2D top-down editor (canvas or SVG) with drag-and-drop items.
    - “Run Vastu audit” button integrates with `/api/chat/vastu`.
  - **Style Quiz**
    - Multi-step wizard:
      - Room type → Budget tier → Style preferences.
    - On completion, redirects to Gallery with filters applied.
  - **AI Consultant**
    - Chat interface using `/api/chat`.
    - Injects contextual information from current page or quiz/profile.
  - **Auth (Login/Register)**
    - Login → `/api/users/login`.
    - Register → `/api/users`.
  - **Profile**
    - Uses `/api/users/profile` to show:
      - Basic user info, saved designs, possibly saved layouts and quiz preferences.

### 2.2 Frontend Architecture & State

- **Data fetching**
  - Use Axios or a typed `fetch` wrapper with:
    - Automatic `Authorization: Bearer <token>` header when user is logged in.
  - Use React Query/TanStack Query for:
    - Caching server state from `/api/designs`, `/api/users/profile`, `/api/chat`, etc.
- **Global state**
  - Minimal global store (e.g., Zustand/Redux):
    - Auth token & user snapshot.
    - 3D Studio layout state and transient UI preferences.
- **Auth UX**
  - After login:
    - Store token (preferably in memory, optionally in localStorage with care).
    - Preload profile data and redirect to the last-intended page or Profile.
  - Protect routes:
    - Saved designs, Profile, and advanced 3D Studio features should require authentication.

### 2.3 3D Studio & Vastu Integration

- **Layout editor MVP**
  - Implement:
    - A 2D grid showing room outline and cardinal directions.
    - Drag-and-drop furniture elements (bed, sofa, table, door, window, etc.).
    - Ability to move, rotate, and delete elements.
  - Data model for each element:
    - `id`, `type`, `x`, `y`, `rotation`, `width`, `height`, `metadata`.
  - Vastu audit flow:
    - Convert layout JSON into a text description listing items and positions.
    - Call `/api/chat/vastu` and render:
      - Score and high-level advice.
      - Per-item analysis (e.g., color-code compliant/non-compliant items on the canvas).

- **Future upgrades**
  - Upgrade rendering to 3D using Three.js or Babylon.js.
  - Support multiple rooms/floor plans and different apartment templates.
  - Save layouts to backend (e.g., `/api/layouts` endpoints) for later editing and sharing.

### 2.4 Style Quiz & Personalization

- **Quiz implementation**
  - Client-side configuration for quiz questions and options.
  - On submit:
    - Map responses to Gallery filters (`roomType`, `style[]`, `budget range`).
    - Optionally send preferences to backend (e.g., `POST /api/users/preferences`).
- **Using quiz data**
  - Apply as default filters on Gallery.
  - Feed into AI context for `/api/chat`.
  - Show “Recommended for you” sections on Home/Profile.

### 2.5 UI/UX, Performance & SEO

- **Design system**
  - Create a cohesive component library:
    - Buttons, cards, inputs, pills/chips, filter controls, modals, toasts.
  - Optionally integrate Tailwind CSS + headless UI or Chakra/MUI.
- **Responsiveness & accessibility**
  - Ensure all pages are fully responsive (mobile-first).
  - Use semantic HTML and ARIA roles; ensure keyboard navigability.
- **Performance**
  - Lazy-load heavy components (3D Studio, AI chat section).
  - Use responsive images and `loading="lazy"` where appropriate.
  - Implement code splitting and route-based chunking.
- **SEO & analytics**
  - Add per-page metadata (title, description, Open Graph tags).
  - Use descriptive, human-readable URLs for designs (e.g., `/designs/urban-zen-sanctuary`).
  - Integrate analytics to track:
    - Gallery usage, design views, quiz completions, AI and Vastu feature usage.

---

## 3. Documentation & Developer Experience

- **Project documentation**
  - Keep this file updated as features are implemented.
  - Maintain a top-level `README` explaining:
    - Project structure, setup instructions, env variables, and common workflows.
- **API documentation**
  - Provide API docs via OpenAPI/Swagger or a dedicated docs page.
  - Describe request/response formats for all endpoints, including error cases.
- **Developer tooling**
  - Add scripts:
    - `dev`, `build`, `start`, `test`, `lint`, `seed`.
  - Consider adding pre-commit hooks for linting and tests to maintain quality.
