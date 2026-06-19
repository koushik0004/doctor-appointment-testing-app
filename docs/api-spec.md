# API Specification

Base URL:

```txt
http://localhost:4001/api
```

## 1. Health

### GET /health

Response:

```json
{
  "status": "ok"
}
```

## 2. Doctors

### GET /doctors

Query params:

```txt
specialty?: string
appointment_type?: IN_PERSON | TELEMEDICINE
search?: string
page?: number
limit?: number
```

Response:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Dr. Sarah Jenkins",
      "slug": "sarah-jenkins",
      "specialty": "Cardiology",
      "title": "Senior Cardiologist",
      "rating": 4.9,
      "review_count": 128,
      "clinic_name": "CareNow Central Clinic",
      "location": "London, UK",
      "fee_min": 120,
      "fee_max": 200,
      "appointment_types": ["IN_PERSON"],
      "next_available": {
        "date": "2024-10-24",
        "start_time": "10:30",
        "label": "Today, 10:30 AM"
      }
    }
  ],
  "total": 4,
  "page": 1,
  "limit": 10
}
```

### GET /doctors/{doctor_id}

Response:

```json
{
  "id": 1,
  "name": "Dr. Sarah Jenkins",
  "specialty": "Cardiology",
  "title": "Senior Cardiologist",
  "rating": 4.9,
  "review_count": 128,
  "clinic_name": "CareNow Central Clinic",
  "location": "London, UK",
  "address": "123 Medical Plaza, Health Heights",
  "fee_min": 120,
  "fee_max": 200,
  "languages": ["English", "Spanish"],
  "appointment_types": ["IN_PERSON"]
}
```

### GET /doctors/{doctor_id}/availability

Query params:

```txt
date: YYYY-MM-DD
```

Response:

```json
{
  "date": "2024-10-24",
  "doctor_id": 1,
  "available_slots": [
    {
      "id": 101,
      "available_date": "2024-10-24",
      "start_time": "10:30",
      "end_time": "11:00",
      "is_booked": false
    }
  ]
}
```

## 3. Specialties

### GET /specialties

Response:

```json
{
  "items": ["General Practice", "Cardiology", "Pediatrics", "Dermatology", "Internal Medicine"]
}
```

## 4. Appointments

### POST /appointments

Request:

```json
{
  "doctor_id": 1,
  "appointment_date": "2024-10-24",
  "start_time": "10:30",
  "appointment_type": "IN_PERSON",
  "patient": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "9999999999"
  },
  "health_description": "Regular follow-up for high blood pressure."
}
```

Response:

```json
{
  "id": 5001,
  "confirmation_code": "CN-99210-XB",
  "status": "CONFIRMED",
  "doctor_id": 1,
  "patient_id": 3001,
  "appointment_date": "2024-10-24",
  "start_time": "10:30",
  "end_time": "11:00"
}
```

### GET /appointments/{appointment_id}

Response:

```json
{
  "id": 5001,
  "confirmation_code": "CN-99210-XB",
  "status": "CONFIRMED",
  "doctor": {
    "name": "Dr. Sarah Jenkins",
    "specialty": "Cardiology",
    "clinic_name": "CareNow Central Clinic",
    "address": "123 Medical Plaza, Health Heights"
  },
  "patient": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "9999999999"
  },
  "appointment_date": "2024-10-24",
  "start_time": "10:30",
  "end_time": "11:00",
  "appointment_type": "IN_PERSON",
  "health_description": "Regular follow-up for high blood pressure."
}
```

### PATCH /appointments/{appointment_id}/cancel

Response:

```json
{
  "id": 5001,
  "status": "CANCELLED"
}
```

## 5. Error Format

Use a consistent error shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid appointment date.",
    "details": []
  }
}
```
