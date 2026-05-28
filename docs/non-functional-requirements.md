# Non-Functional Requirements

## Performance

- Doctor list should load quickly from SQLite.
- Avoid unnecessary frontend global state.
- Keep API responses small.

## Accessibility

- Use semantic buttons for clickable actions.
- Ensure focus styles are visible.
- Use labels for all form fields.
- Do not hide focused elements with `aria-hidden`.

## Responsiveness

- Desktop: two-column layout where required.
- Mobile: stack sections vertically.
- Cards should not overflow.

## Security for V1

- Validate all backend inputs.
- Do not expose SMTP password in frontend.
- Use `.env` and `.env.local`.
- CORS should allow only frontend origin in local development.

## Maintainability

- Keep features separated.
- Avoid large components.
- Put API calls under feature folders.
- Put backend business logic in services.

