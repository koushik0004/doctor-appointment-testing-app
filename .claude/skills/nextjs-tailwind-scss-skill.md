# Skill: Next.js + Tailwind + SCSS

## Purpose

Use this skill when building frontend UI.

## Standards

- Use Next.js App Router.
- Use server components by default unless client behavior is needed.
- Use `use client` only for interactive components.
- Use Tailwind for layout, spacing, typography, and responsive behavior.
- Use SCSS for global utilities or repeated advanced styles only.

## Component Pattern

```txt
Page component → feature component → shared UI component
```

Avoid putting all JSX in page files.

## Styling Pattern

- Cards: rounded corners, subtle border, soft shadow.
- Buttons: cyan primary, white secondary.
- Forms: clear labels and validation messages.
- Layout: responsive grid/flex.

