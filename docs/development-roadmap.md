# Development Roadmap

## Milestone 0: Repo Foundation

Goal: Create clean project skeleton.

Tasks:

- Create monorepo structure.
- Add frontend Next.js app.
- Add backend FastAPI app.
- Add `.env.example` files.
- Add common README.
- Add `.claude` folder and spec files.

Done when:

- Frontend runs on port 4002.
- Backend runs on port 4001.
- Health API returns `ok`.

## Milestone 1: Backend DB and Seed Data

Goal: SQLite database with doctors and availability.

Tasks:

- Create SQLAlchemy models.
- Create DB session dependency.
- Create seed script.
- Seed doctors and slots.
- Add doctors APIs.

Done when:

- `GET /api/doctors` returns seeded doctors.
- `GET /api/doctors/{id}/availability` returns slots.

## Milestone 2: Frontend Layout and Home Page

Goal: Match home page design at basic level.

Tasks:

- Header
- Footer
- Hero section
- Recommended doctor card
- Available doctors cards
- Booking summary placeholder

Done when:

- Home page visually resembles uploaded design.
- Doctor cards render from backend.

## Milestone 3: Doctor Listing and Filters

Goal: User can browse/filter doctors.

Tasks:

- `/doctors` page
- Specialty filters
- Appointment type filters
- Doctor list cards
- Booking summary card

Done when:

- Filtering works.
- User can select doctor and navigate to booking page.

## Milestone 4: Appointment Booking Form

Goal: User can select date/time and enter patient details.

Tasks:

- `/appointments/new` page
- Doctor summary
- Calendar-like date UI
- Slot buttons
- React Hook Form form
- Zod validation

Done when:

- Form validates.
- Submit creates appointment through backend.

## Milestone 5: Confirmation Page and Email

Goal: User sees confirmed appointment and email is sent/logged.

Tasks:

- Confirmation page
- Appointment details API
- Email service
- Email log

Done when:

- Confirmation page shows correct data.
- Console email/log email is created.

## Milestone 6: Testing and Cleanup

Goal: Stabilize v1.

Tasks:

- Backend unit tests for appointment service.
- API tests for doctor and appointment endpoints.
- Frontend component sanity checks if desired.
- Error/loading UI.
- README run instructions.

Done when:

- Manual full booking flow works end-to-end.

## Future Milestone 7: AI Chatbot and Browser Agent

Not part of first build, but reserve architecture.

Tasks:

- Chatbot page
- Natural-language command parser
- Playwright visible automation
- Agent asks user for missing required data
- Agent books appointment visibly through UI
