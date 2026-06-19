# Feature 4 Frontend Analysis

## Scope

This document analyzes the current frontend implementation for the manual doctor booking flow and identifies what can be reused for the Feature 4 booking search work.

## 1. Existing Application Routing

Current App Router routes in `frontend/app/`:

- `/` from [`frontend/app/page.tsx`](../../../frontend/app/page.tsx)
- `/doctors` from [`frontend/app/doctors/page.tsx`](../../../frontend/app/doctors/page.tsx)
- `/appointments` from [`frontend/app/appointments/page.tsx`](../../../frontend/app/appointments/page.tsx)
- `/appointments/confirmation` from [`frontend/app/appointments/confirmation/page.tsx`](../../../frontend/app/appointments/confirmation/page.tsx)
- `/api/*` proxy route from [`frontend/app/api/[...path]/route.ts`](../../../frontend/app/api/%5B...path%5D/route.ts)

Route behavior notes:

- The booking flow is query-param driven. `doctorId` is read from `/appointments?doctorId=...`.
- The confirmation page reads `appointmentId` and `doctorId` from query params, then falls back to Zustand state if needed.
- The current frontend does not use the `/appointments/new` or `/appointments/[appointmentId]/confirmation` structure shown in the frontend spec.
- Both booking and confirmation pages are marked `dynamic = "force-dynamic"` and render as client components.

## 2. Existing Booking Confirmation Page

The confirmation page already exists at `/appointments/confirmation`.

Key implementation details:

- It fetches confirmation data with `getAppointmentConfirmation(appointmentId)` and doctor details with `getDoctor(doctorId)`.
- It renders loading, error, and missing-booking states.
- It uses `AppointmentSummary` for the confirmation details card.
- It shows the confirmation code, booking details, patient details, and visit reason.
- It provides two actions:
  - `Modify Appointment` links back to `/appointments?doctorId=...`
  - `Reset Booking` clears the Zustand booking store

Reusable pieces already present in this page:

- `AppointmentSummary`
- `ApiError` handling pattern
- `useBookingStore` fallback state
- shared button/card styling via Tailwind classes

## 3. Existing Appointment Booking Flow

The current manual booking flow is implemented in `/appointments`.

High-level flow:

1. Resolve the selected doctor from query params or Zustand store.
2. Load doctor details with `getDoctor`.
3. Load availability with `getDoctorAvailability(doctorId, { date })`.
4. Let the user pick a date using `AppointmentCalendar`.
5. Let the user pick a time using `AppointmentAvailability`.
6. Collect patient details with `PatientDetailsForm`.
7. Submit with `createAppointment`.
8. Persist booking state in Zustand.
9. Navigate to `/appointments/confirmation?appointmentId=...&doctorId=...`.

Important implementation details:

- Selected date, time, appointment type, patient details, appointment id, and confirmation code are stored in [`frontend/stores/booking-store.ts`](../../../frontend/stores/booking-store.ts).
- The page recalculates availability against the current time to prevent booking expired slots.
- If the selected slot has already elapsed, the form submission is blocked with a user-visible message.
- Doctor details and availability are fetched in parallel with `Promise.all`.

Reusable flow components already present:

- `AppointmentCalendar`
- `AppointmentAvailability`
- `DoctorSummaryCard`
- `PatientDetailsForm`
- `AppointmentTypeSelector`
- `AppointmentSummary`

## 4. Existing API Integration Patterns

The frontend uses a simple fetch-based API layer, not React Query or custom hooks.

### API client

[`frontend/lib/api-client.ts`](../../../frontend/lib/api-client.ts) provides:

- a base URL from `NEXT_PUBLIC_API_BASE_URL` with `/api` as fallback
- JSON request/response handling
- consistent `ApiError` parsing
- `get`, `post`, and `patch` helpers

### Feature API functions

Existing feature-level API functions:

- [`frontend/features/doctors/api.ts`](../../../frontend/features/doctors/api.ts)
  - `listDoctors`
  - `getDoctor`
- [`frontend/features/appointments/api.ts`](../../../frontend/features/appointments/api.ts)
  - `getDoctorAvailability`
  - `createAppointment`
  - `getAppointmentConfirmation`

### Backend proxy

[`frontend/app/api/[...path]/route.ts`](../../../frontend/app/api/%5B...path%5D/route.ts) proxies frontend requests to the backend base URL configured by `BACKEND_API_BASE_URL` or `http://localhost:4001`.

API integration pattern summary:

- feature-specific API modules map raw backend records into frontend-friendly types
- query string construction happens in the feature API layer
- request cancellation uses `AbortController` in page components
- pages handle loading and error state manually

There are currently no dedicated API hooks such as `useDoctors` or `useAppointmentAvailability`.

## 5. Existing UI Component Library

The frontend has a small, reusable UI layer built mostly from Tailwind-styled components and feature components.

### Layout components

- [`frontend/components/layout/Header.tsx`](../../../frontend/components/layout/Header.tsx)
- [`frontend/components/layout/Footer.tsx`](../../../frontend/components/layout/Footer.tsx)

### UI primitives

- [`frontend/components/ui/calendar.tsx`](../../../frontend/components/ui/calendar.tsx)
- [`frontend/lib/utils.ts`](../../../frontend/lib/utils.ts) provides `cn(...)`

### Doctor feature components

- [`frontend/components/doctors/DoctorCard.tsx`](../../../frontend/components/doctors/DoctorCard.tsx)
- [`frontend/components/doctors/DoctorFilters.tsx`](../../../frontend/components/doctors/DoctorFilters.tsx)
- [`frontend/components/doctors/BookingSummary.tsx`](../../../frontend/components/doctors/BookingSummary.tsx)
- [`frontend/components/doctors/DoctorsPageClient.tsx`](../../../frontend/components/doctors/DoctorsPageClient.tsx)
- [`frontend/components/doctors/DoctorsPagination.tsx`](../../../frontend/components/doctors/DoctorsPagination.tsx)

### Appointment feature components

- [`frontend/features/appointments/components/AppointmentCalendar.tsx`](../../../frontend/features/appointments/components/AppointmentCalendar.tsx)
- [`frontend/features/appointments/components/AppointmentAvailability.tsx`](../../../frontend/features/appointments/components/AppointmentAvailability.tsx)
- [`frontend/features/appointments/components/AppointmentSummary.tsx`](../../../frontend/features/appointments/components/AppointmentSummary.tsx)
- [`frontend/features/appointments/components/AppointmentTypeSelector.tsx`](../../../frontend/features/appointments/components/AppointmentTypeSelector.tsx)
- [`frontend/features/appointments/components/DoctorSummaryCard.tsx`](../../../frontend/features/appointments/components/DoctorSummaryCard.tsx)
- [`frontend/features/appointments/components/PatientDetailsForm.tsx`](../../../frontend/features/appointments/components/PatientDetailsForm.tsx)

### Shared visual patterns

- rounded cards with light borders and soft shadows
- cyan / sky accent color
- spacious desktop layout with stacked mobile sections
- inline SVG icons rather than an icon package
- loading and error states are implemented locally inside pages

### Reusable components for Feature 4

Most reusable for booking search work:

- `Header` and `Footer`
- `DoctorCard`
- `DoctorFilters`
- `BookingSummary`
- `AppointmentCalendar`
- `AppointmentAvailability`
- `PatientDetailsForm`
- `AppointmentSummary`
- `Calendar`
- `apiClient`
- `ApiError`
- `useBookingStore`

## 6. Findings Relevant To Feature 4

- The current frontend already has a complete manual booking experience that can be referenced for the search flow.
- Route structure does not match the frontend spec exactly, so Feature 4 work should decide whether to preserve current routes or introduce the spec route shape later.
- The current codebase has reusable appointment and doctor components, but no generic design-system primitives like `Button`, `Card`, `Input`, or `Badge`.
- API access is centralized and consistent enough to support search and booking extensions without adding a new networking layer.
- State persistence is already handled with Zustand for booking continuity across booking and confirmation pages.

## 7. Recommended Reuse Strategy

For the booking search feature, reuse the current primitives instead of rebuilding them:

- route shell and global layout from `Header`, `Footer`, and `RootLayout`
- doctor presentation from `DoctorCard` and `BookingSummary`
- booking workflow pieces from `AppointmentCalendar`, `AppointmentAvailability`, and `PatientDetailsForm`
- API client pattern from `apiClient` plus feature API modules
- booking continuity from `useBookingStore`

If the search feature needs a distinct route structure, it should be layered on top of the existing booking implementation rather than replacing these components wholesale.
