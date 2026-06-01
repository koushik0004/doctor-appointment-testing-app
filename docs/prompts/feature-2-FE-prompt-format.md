You are a senior frontend engineer working on a spec-driven project.

PROJECT CONTEXT:

* Read all relevant docs from `/docs` and `.claude` before implementation.
* Follow spec-driven development strictly.
* Do not assume anything outside the specs or provided design.
* Reuse the existing project foundation already created.
* This task is frontend-only.

FEATURE:

* Implement the doctor listing page UI based on the provided design image.
* Treat this as the doctor discovery / selection screen for the appointment app.

PRIMARY REFERENCE:

* Use the provided doctor listing layout image as the source of truth for structure, spacing, sections, and visual hierarchy.

GOAL:
Build a static Next.js doctor listing page with minimal client-side interactivity only.
Do not add backend integration, real API calls, authentication, or production business logic.

TECH STACK:

* Next.js (App Router)
* Tailwind + SCSS
* Zustand
* React Hook Form + Zod only if truly needed
* TypeScript

ROUTE SCOPE:

* Implement `/doctors`
* Update `/` only if needed to link to `/doctors`
* Do not implement `/appointments` in this task except optional placeholder navigation target

PAGE REQUIREMENTS:

1. Build the doctor listing page layout matching the design as closely as practical:

   * Header
   * Left filter sidebar
   * Main doctor list section
   * Right booking summary sidebar
   * Footer

2. Doctor list content:

   * Use static mock doctor data stored locally in the frontend codebase
   * Render doctor cards with:

     * profile image/avatar
     * name
     * specialty
     * rating
     * review count
     * short description
     * languages
     * clinic/hospital name
     * fee range
     * next available slot
     * CTA button
   * One card can appear visually selected by default

3. Filter sidebar:

   * Add basic static filter groups:

     * Specialty
     * Appointment Type
   * Filter interactions should be frontend-only using local mock data
   * Keep filtering simple:

     * specialty single-select or multi-select
     * appointment type single-select or multi-select
   * No URL sync required unless already established in project foundation

4. Sort control:

   * Add a simple sort UI near the page title
   * Support basic frontend-only sort options such as:

     * Top Rated
     * Earliest Availability
   * Sorting should work on mock data only

5. Booking summary panel:

   * Show a static summary card on the right
   * When a doctor is selected, update summary from local state only
   * Include:

     * selected doctor
     * consultation fee
     * estimated duration
     * total estimate
     * primary CTA button
   * CTA can route to `/appointments` or remain a disabled placeholder based on current project scope

6. Pagination area:

   * Add static pagination UI matching the design style
   * Minimal functionality allowed:

     * either static pagination display only
     * or simple client-side page switching on mock data
   * No server pagination

STATE MANAGEMENT:

* Use Zustand only if needed for selected doctor and page-level UI state
* Keep state minimal and localized where possible
* Do not over-engineer global state

DATA RULES:

* Create local mock data only
* No backend calls
* No fetch to external/local APIs
* No repository pattern or async service implementation unless already required by project foundation
* If API client exists, do not use it for this feature

DESIGN RULES:

* Match the provided image closely for:

  * layout structure
  * spacing
  * card hierarchy
  * typography scale
  * soft borders
  * light medical/healthcare visual tone
* Keep the UI clean and simple
* Prefer reusable presentational components
* Use placeholders for avatars/images if needed
* Ensure responsive behavior at least for:

  * desktop
  * tablet
  * mobile stacked layout
* Do not spend effort on pixel-perfect animation

ACCESSIBILITY:

* Use semantic HTML
* Buttons and filters should be keyboard accessible
* Provide alt text for doctor images
* Ensure selected state is visually clear

IMPLEMENTATION BOUNDARY:

* Only implement the UI and minimal frontend interactions for doctor listing
* Do not build:

  * real booking flow
  * backend integration
  * auth
  * form submission
  * real search API
  * analytics
  * toasts/modals unless already required by spec

EXPECTED FILES / DELIVERABLES:

* route page for `/doctors`
* reusable components for:

  * doctor card
  * filter sidebar
  * booking summary
  * pagination
* local mock data file
* any minimal types/interfaces needed
* styling updates only if required

CODE QUALITY RULES:

* Keep components small and readable
* Use clear TypeScript types
* Avoid dead code and unnecessary abstractions
* Follow existing folder structure and conventions from project docs
* Do not modify unrelated files

OUTPUT FORMAT:

1. Generate code only
2. Mention created/updated files
3. Keep implementation limited to this feature only
