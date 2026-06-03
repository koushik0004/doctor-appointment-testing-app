# Frontend Engineering Specification

## 1. Framework

Use:

- Next.js App Router
- TypeScript
- Tailwind CSS
- SCSS for global utility additions when needed
- Zustand for simple app state
- React Hook Form for form state
- Zod for validation

## 2. Suggested Folder Structure

```txt
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── doctors/
│   │   └── page.tsx
│   └── appointments/
│       ├── new/
│       │   └── page.tsx
│       └── [appointmentId]/
│           └── confirmation/
│               └── page.tsx
│
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   └── LoadingState.tsx
│   └── doctors/
│       ├── DoctorCard.tsx
│       ├── DoctorFilters.tsx
│       └── BookingSummary.tsx
│
├── features/
│   ├── doctors/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── components/
│   └── appointments/
│       ├── api.ts
│       ├── schema.ts
│       ├── types.ts
│       └── components/
│
├── lib/
│   ├── api-client.ts
│   ├── date-utils.ts
│   └── formatters.ts
│
├── stores/
│   └── booking-store.ts
│
└── styles/
    └── globals.scss
```

## 3. UI Design Principles

Match the provided CareNow-style screens:

- Clean white background
- Light cyan accent color
- Rounded cards
- Soft shadows
- Spacious layout
- Minimal form fields
- Left content + right summary layout on desktop
- Stack sections on mobile

Suggested design tokens:

```txt
Primary accent: cyan / sky
Background: #ffffff and #f8fafc
Text: near-black slate
Cards: white with border
Border radius: 12px to 20px
```

## 4. State Management

Use Zustand only for temporary booking state:

```ts
selectedDoctorId
selectedAvailabilityId
selectedDate
selectedTime
appointmentType
```

Do not store API cache manually in Zustand unless necessary.

## 5. Forms

Use React Hook Form + Zod.

Appointment form fields:

```txt
appointment_type
full_name
email
phone
health_description
```

Validation:

```txt
full_name: required, min 2
email: required, valid email
phone: optional in v1
health_description: optional, max 500
appointment_type: required enum
```

## 6. Frontend API Client

Create a simple fetch wrapper:

```txt
lib/api-client.ts
```

Responsibilities:

- Read `NEXT_PUBLIC_API_BASE_URL`
- Add JSON headers
- Parse errors consistently
- Return typed results

## 7. Page-Level Implementation Order

1. Layout, header, footer
2. Home page static UI
3. Doctor cards with mock data
4. Connect doctor cards to backend
5. Doctor listing page
6. Filters
7. Booking page
8. Confirmation page
9. Error/loading states
10. Responsive polish

