# Frontend Instructions

## NextJS

* Use App Router only
* Prefer server components
* Use loading.tsx and error.tsx

## Components

* Shared UI in components/ui
* Feature components in features/

## Styling

* Tailwind only
* Use clsx helper
* Avoid inline CSS

## State

* Zustand for global state
* Local state when possible

## Forms

* react-hook-form + zod

## API Calls

* Use centralized axios client
* Never call fetch inside components
