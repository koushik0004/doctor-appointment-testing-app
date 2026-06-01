# Skill: React Hook Form + Zod + Zustand

## Purpose

Use this skill for frontend form and simple booking state.

## React Hook Form

Use for patient details form.

## Zod

Use for validation schema.

Example rules:

```txt
full_name: required
email: valid email
phone: optional
health_description: optional max 500
```

## Zustand

Use only for temporary booking selection:

```txt
selectedDoctorId
selectedAvailabilityId
selectedDate
selectedTime
appointmentType
```

Do not use Zustand as API cache.

