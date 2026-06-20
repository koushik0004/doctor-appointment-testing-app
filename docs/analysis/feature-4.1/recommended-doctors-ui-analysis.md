# Feature 4.1 Recommended Doctors UI Analysis

## Scope

This document analyzes the current frontend doctor-card related UI for Feature 4.1.

It identifies:

- doctor cards used on the home page
- doctor cards used on the doctor listing page
- the doctor summary card used on the booking page
- reusable doctor card patterns
- reusable badges
- reusable buttons
- reusable rating display patterns

No application code is modified in this step.

## High-Level Finding

There is no doctor card currently rendered on the home page.

The current reusable doctor-related UI is split across:

- `DoctorCard` on the doctor listing page
- `BookingSummary` on the doctor listing page sidebar
- `DoctorSummaryCard` on the booking page

These components share data shape and some visual patterns, but there is no single shared doctor-card primitive yet.

## Home Page

Source: [`frontend/app/page.tsx`](../../../frontend/app/page.tsx#L1)

Current state:

- the home page is still a project-foundation landing screen
- it contains CTA links and status text only
- it does not render any doctor list, doctor card, recommendation card, rating UI, or booking summary card

Implication for Feature 4.1:

- there is no existing home-page doctor card to reuse directly
- if recommended doctors are later added to the home page, the implementation will need to reuse an existing doctor-related component from another route or introduce a new shared card

## Doctor Listing Page

Page source: [`frontend/components/doctors/DoctorsPageClient.tsx`](../../../frontend/components/doctors/DoctorsPageClient.tsx#L221)

Card source: [`frontend/components/doctors/DoctorCard.tsx`](../../../frontend/components/doctors/DoctorCard.tsx#L31)

Sidebar summary source: [`frontend/components/doctors/BookingSummary.tsx`](../../../frontend/components/doctors/BookingSummary.tsx#L28)

### Primary list card: `DoctorCard`

`DoctorCard` is the main doctor browse card currently used in the app.

Rendered fields:

- avatar
- doctor name
- specialty
- numeric rating
- review count
- description
- languages
- clinic and location
- fee range
- next available text
- selection CTA

Interaction model:

- supports selected and unselected states
- calls `onSelect(doctor.id)` when the CTA is pressed
- uses `aria-pressed` for the selected state

Visual structure:

- large horizontal card
- detail-heavy content area on the left
- booking/availability action rail on the right

Reusability assessment:

- strong candidate if Feature 4.1 needs a full-width, detailed recommended doctor card
- weak candidate if the recommendation UI needs a compact horizontal card or a smaller sidebar card
- currently too coupled to selection behavior and "Choose time" CTA copy for direct reuse as a recommendation card without props expansion

### Sidebar summary: `BookingSummary`

`BookingSummary` is not a list card. It is a selected-doctor summary panel shown beside the doctor list.

Rendered fields:

- avatar
- doctor name
- specialty
- fee range
- next available text
- starting price
- proceed-to-booking CTA

Interaction model:

- empty state when no doctor is selected
- route navigation via `Link` to `/appointments?doctorId={backendId}`

Reusability assessment:

- useful as a pattern for compact doctor summary and booking CTA
- not suitable as the primary recommended-doctor card because it assumes a single selected doctor and sidebar placement

## Booking Page

Page source: [`frontend/app/appointments/page.tsx`](../../../frontend/app/appointments/page.tsx#L537)

Card source: [`frontend/features/appointments/components/DoctorSummaryCard.tsx`](../../../frontend/features/appointments/components/DoctorSummaryCard.tsx#L67)

### Doctor summary card: `DoctorSummaryCard`

`DoctorSummaryCard` is the doctor panel used on the booking page.

Rendered fields:

- avatar
- doctor name
- specialty
- pill-style label via `ratingLabel` prop
- clinic
- location
- wait time label via `waitTimeLabel` prop

Interaction model:

- display-only
- no CTA button

Visual structure:

- compact card
- strong header row
- two boxed info tiles below

Reusability assessment:

- good candidate if Feature 4.1 needs a compact summary-style recommendation card
- especially useful because the badge text is already prop-driven through `ratingLabel`
- limited because it does not currently show numeric rating, review count, next availability, or action buttons

## Reusable Doctor Card Components

### 1. `DoctorCard`

Source: [`frontend/components/doctors/DoctorCard.tsx`](../../../frontend/components/doctors/DoctorCard.tsx#L31)

Most reusable for:

- detailed recommendation cards
- list/grid recommendation sections
- situations where rating and availability must be visible immediately

Reuse constraints:

- hardcoded CTA labels: `Selected` and `Choose time`
- requires selection-state props
- embeds local icon helpers instead of using shared UI primitives

### 2. `DoctorSummaryCard`

Source: [`frontend/features/appointments/components/DoctorSummaryCard.tsx`](../../../frontend/features/appointments/components/DoctorSummaryCard.tsx#L67)

Most reusable for:

- compact recommendation panels
- right-rail cards
- summary-first doctor modules

Reuse constraints:

- no built-in CTA
- no numeric rating display
- no review count
- no next-available field

### 3. `BookingSummary`

Source: [`frontend/components/doctors/BookingSummary.tsx`](../../../frontend/components/doctors/BookingSummary.tsx#L28)

Most reusable for:

- selected-doctor pricing summaries
- booking handoff modules

Reuse constraints:

- tied to a nullable selected-doctor flow
- includes page-specific copy and guarantee content
- less suitable for rendering multiple recommended doctors

## Reusable Badges

### Existing badge-like patterns

1. Text rating badge in `DoctorSummaryCard`

Source: [`frontend/features/appointments/components/DoctorSummaryCard.tsx`](../../../frontend/features/appointments/components/DoctorSummaryCard.tsx#L98)

Pattern:

- rounded pill
- `bg-brand-100`
- `text-brand-600`
- label text such as `Highly Rated`

Assessment:

- best existing badge candidate for recommendation reasons like `Highly Rated` or `Same Specialty`
- already prop-driven through `ratingLabel`

2. Section/status badges on other pages

Source: [`frontend/app/page.tsx`](../../../frontend/app/page.tsx#L7)

Pattern:

- small rounded label with colored background

Assessment:

- stylistically reusable, but not doctor-card specific

### Missing shared badge abstraction

There is no standalone shared badge component in `frontend/components/ui/`.

Implication:

- any recommendation badge reuse today would mean reusing styling conventions, not importing a shared badge primitive

## Reusable Buttons

### 1. Doctor selection button in `DoctorCard`

Source: [`frontend/components/doctors/DoctorCard.tsx`](../../../frontend/components/doctors/DoctorCard.tsx#L126)

Pattern:

- full-width button
- selected and unselected variants
- rounded medium emphasis CTA

Assessment:

- strongest reusable doctor-card CTA
- good base for actions like `Book now` or `View availability`
- currently coupled to selection state and local button copy

### 2. Booking CTA in `BookingSummary`

Source: [`frontend/components/doctors/BookingSummary.tsx`](../../../frontend/components/doctors/BookingSummary.tsx#L97)

Pattern:

- full-width primary action
- navigational link styled as a button

Assessment:

- useful if recommendations should deep-link into booking directly
- not reusable as-is for multi-card sections because it lives inside a summary panel

### Missing shared button abstraction

There is no dedicated shared doctor-card action component.

Implication:

- button reuse is currently by copying Tailwind patterns or extracting a new shared UI component later

## Reusable Rating Display

### 1. Numeric rating display in `DoctorCard`

Source: [`frontend/components/doctors/DoctorCard.tsx`](../../../frontend/components/doctors/DoctorCard.tsx#L62)

Pattern:

- custom star icon
- numeric rating with one decimal place
- review count in parentheses

Assessment:

- this is the only complete doctor-rating display currently implemented
- best source for Feature 4.1 if the recommended doctors UI must show actual rating data

### 2. Qualitative rating label in `DoctorSummaryCard`

Source: [`frontend/features/appointments/components/DoctorSummaryCard.tsx`](../../../frontend/features/appointments/components/DoctorSummaryCard.tsx#L72)

Pattern:

- text-only badge
- no numeric score
- no review count

Assessment:

- works as supporting emphasis
- insufficient if recommendation ranking needs transparent rating evidence

## Recommendation For Feature 4.1 UI Reuse

If the recommended doctors UI needs a compact multi-card list:

- use `DoctorSummaryCard` as the visual baseline
- add numeric rating and CTA support in a shared follow-up component

If the recommended doctors UI needs a richer browseable list with visible availability:

- use `DoctorCard` as the stronger baseline
- generalize its CTA and selection props so it can support recommendation actions

If the requirement is to ship with minimal UI change risk:

- reuse the `DoctorCard` rating block pattern
- reuse the `DoctorSummaryCard` badge pattern
- avoid reusing `BookingSummary` as the main recommendation card because it is structurally a selected-doctor sidebar module, not a repeatable card

## Final Conclusion

Current doctor-related UI is reusable at the pattern level, but not yet unified into a shared recommendation-card system.

Best current assets:

- `DoctorCard` for detailed doctor presentation, rating, and CTA
- `DoctorSummaryCard` for compact summary layout and pill badge styling
- `BookingSummary` for booking handoff behavior

Current gap:

- no home-page doctor card exists
- no shared badge component exists
- no shared doctor rating component exists
- no shared recommendation-specific CTA exists
