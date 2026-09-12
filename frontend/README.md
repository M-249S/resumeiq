# ResumeIQ — Frontend (TypeScript)

A from-scratch TypeScript rewrite of the ResumeIQ landing experience,
built around one goal: **stop looking like a generic AI-generated SaaS
template.**

## Why this exists

The original frontend used the most common "AI-generated landing page"
pattern — a near-black background, a cyan-to-blue gradient glow behind the
headline, glassmorphism cards, and fabricated global stats ("12K+ resumes
analyzed"). None of that was a deliberate design decision; it was just the
default.

This rewrite starts over with an **editorial** direction instead — grounded
in what the product actually is (a document tool): a warm paper
background, ink-navy text, one precise forest-green accent used sparingly,
a distinctive serif display face (Fraunces) paired with Inter for body
text, and a hero visual built from real product mechanics (a before/after
resume line rewrite and match score) instead of an abstract gradient shape.

## Stack

- **React 19 + TypeScript**, strict compiler settings (`noUnusedLocals`,
  `noUnusedParameters`)
- **Vite 8** with the `@tailwindcss/vite` plugin
- **Tailwind CSS v4** (CSS-first `@theme` configuration, no
  `tailwind.config.js`)
- **React Router** for routing
- `clsx` + `tailwind-merge` for a standard `cn()` className utility

## Structure

```
src/
  components/
    ui/          Button, Card, Badge, Logo, Input — no business logic
    landing/     Navbar, Hero, Features, HowItWorks, Footer, DocumentPreview
    ProtectedRoute.tsx
  context/
    AuthContext.ts    Context object + types only (kept separate so
                      AuthProvider.tsx stays a component-only file —
                      required for Fast Refresh, enforced by oxlint)
    AuthProvider.tsx  Auth state, backed by the real /auth/* endpoints
  hooks/
    useAuth.ts   Consumes AuthContext
  services/
    auth.ts      Typed API calls matching the FastAPI backend's exact
                 request/response shapes (including the OAuth2 form-encoded
                 login quirk — see comments in the file)
  types/
    auth.ts      User, TokenResponse, RegisterPayload
  pages/
    Landing.tsx, Login.tsx, Signup.tsx, Dashboard.tsx (placeholder)
  layouts/
    AuthLayout.tsx
  styles/
    index.css    Design tokens (@theme) + base layer
  lib/
    api.ts       axios instance (baseURL from VITE_API_URL, bearer token
                 interceptor)
    cn.ts        className merge utility
```

## Design tokens

All color, font, and radius decisions live in `src/styles/index.css` under
`@theme`, not scattered across components:

| Token | Value | Use |
|---|---|---|
| `--color-paper` | `#faf9f6` | Page background |
| `--color-ink` | `#14213d` | Primary text |
| `--color-ink-muted` / `--color-ink-faint` | — | Secondary/tertiary text |
| `--color-accent` | `#1b4332` | The **one** accent color — CTAs, links, highlights |
| `--font-display` | Fraunces Variable | Headlines only |
| `--font-sans` | Inter Variable | Everything else |

## Running it

```bash
npm install
npm run dev       # http://localhost:5173
npm run build      # tsc -b && vite build — must pass with zero errors
npm run lint       # oxlint
npm run preview    # serve the production build locally
```

## Resume analysis flow

`pages/Dashboard.tsx` implements the real flow against the backend's
`/resume/*` endpoints:

- `POST /resume/upload` — multipart form (PDF + optional job description)
  → full `ResumeAnalysis` (overall score, job-match score, six sub-scores,
  strengths/weaknesses, matching/missing keywords, suggestions)
- `POST /resume/download` — re-sends the same file, gets back a rewritten
  PDF as a binary stream, saved via a Blob + temporary object URL (no
  full-page navigation)

Handled explicitly: non-PDF uploads (client-side, before any request goes
out), a 429 from the backend's per-IP AI rate limit (5/minute) shown as a
plain-language message rather than a raw error, and a generic fallback for
anything else.

## Auth flow

Wired up against the real backend contract (`backend/app/auth/router.py`
in the companion repo), not a mock:

- `POST /auth/register` — JSON `{ full_name, email, password }` → `201`
- `POST /auth/login` — **form-urlencoded**, not JSON (FastAPI's
  `OAuth2PasswordRequestForm` expects `username` + `password`) → returns
  `{ access_token, refresh_token, token_type }`
- `GET /auth/me` — Bearer token → current user, used to revalidate on
  every page load rather than trusting a cached copy

**Known trade-off, inherited and kept intentionally:** tokens are stored
in `localStorage`, which is readable by any script on the page (XSS
exposure) — same trade-off the original JSX version made, documented
rather than silently carried over. The safer alternative is an httpOnly
cookie set by the backend, which isn't implemented here yet.

## Cover letter flow

`CoverLetterPanel` reuses the same file + job description already in
memory from the analysis step — no re-upload needed:

- `POST /resume/cover-letter` — returns generated text, shown in an
  **editable** textarea (the AI draft is a starting point, not a final
  answer the user can't touch)
- `POST /resume/cover-letter/download` — same inputs, returns a `.docx`

## Status

Covers: landing page, `/login`, `/signup`, and a protected `/dashboard`
with the full flow — upload → analyze → results → download improved
resume → generate/edit/download cover letter — wired to the FastAPI
backend's actual contract throughout. Verified: `tsc -b` passes with zero
errors, `npm run build` succeeds, `oxlint` reports zero warnings, and
every page/state has been checked visually (including result and
cover-letter states, using temporarily injected fixture data that was
removed before this was packaged — not left in the shipped code).

## What's next

- Make `Navbar` auth-aware (it currently always shows "Log in / Get
  started", even on `/dashboard` where the user is already logged in)
- Consider httpOnly cookie-based auth instead of `localStorage`
- A resume/cover-letter history view, backed by the `ResumeAnalysis`
  rows the backend already persists per user
