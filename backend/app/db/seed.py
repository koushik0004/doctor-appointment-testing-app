from datetime import date

from sqlalchemy.orm import Session

from app.models.availability import DoctorAvailability
from app.models.doctor import Doctor


DOCTOR_SEED_DATA = [
    {
        "name": "Dr. Sarah Jenkins",
        "specialty": "Cardiology",
        "rating": 4.9,
        "review_count": 128,
        "clinic_name": "CareNow Central Clinic",
        "location": "London, UK",
        "consultation_fee_min": 120,
        "consultation_fee_max": 200,
        "next_available_slot": "Today, 10:30 AM",
        "appointment_types": ["IN_PERSON"],
        "languages": ["English", "Spanish"],
        "description": "Senior cardiologist focused on preventive care, blood pressure management, and long-term heart health.",
        "image_url": "/avatars/doctor-sarah.svg",
    },
    {
        "name": "Dr. Marcus Chen",
        "specialty": "Pediatrics",
        "rating": 4.8,
        "review_count": 94,
        "clinic_name": "Green Valley Pediatrics",
        "location": "London, UK",
        "consultation_fee_min": 80,
        "consultation_fee_max": 150,
        "next_available_slot": "Tomorrow, 9:00 AM",
        "appointment_types": ["IN_PERSON"],
        "languages": ["English", "Mandarin", "Cantonese"],
        "description": "Pediatrician providing compassionate care for infants, children, and adolescents.",
        "image_url": "/avatars/doctor-marcus.svg",
    },
    {
        "name": "Dr. Elena Rodriguez",
        "specialty": "Dermatology",
        "rating": 5.0,
        "review_count": 215,
        "clinic_name": "Skin & Beauty Clinic",
        "location": "Downtown",
        "consultation_fee_min": 150,
        "consultation_fee_max": 250,
        "next_available_slot": "Wednesday, Oct 25",
        "appointment_types": ["IN_PERSON", "TELEMEDICINE"],
        "languages": ["English", "Spanish", "Portuguese"],
        "description": "Board-certified dermatologist specializing in medical and cosmetic skin treatments.",
        "image_url": "/avatars/doctor-elena.svg",
    },
    {
        "name": "Dr. James Wilson",
        "specialty": "Internal Medicine",
        "rating": 4.7,
        "review_count": 82,
        "clinic_name": "City Health Partners",
        "location": "London, UK",
        "consultation_fee_min": 100,
        "consultation_fee_max": 180,
        "next_available_slot": "Today, 4:45 PM",
        "appointment_types": ["IN_PERSON", "TELEMEDICINE"],
        "languages": ["English"],
        "description": "Adult medicine specialist focused on diagnostics, prevention, and coordinated care.",
        "image_url": "/avatars/doctor-james.svg",
    },
    {
        "name": "Dr. Aisha Khan",
        "specialty": "General Practice",
        "rating": 4.9,
        "review_count": 171,
        "clinic_name": "Riverside Family Clinic",
        "location": "Canary Wharf",
        "consultation_fee_min": 70,
        "consultation_fee_max": 120,
        "next_available_slot": "Today, 6:15 PM",
        "appointment_types": ["IN_PERSON", "TELEMEDICINE"],
        "languages": ["English", "Urdu"],
        "description": "Family physician offering preventive checkups and same-day consultation support.",
        "image_url": "/avatars/doctor-sarah.svg",
    },
    {
        "name": "Dr. Daniel Park",
        "specialty": "Cardiology",
        "rating": 4.6,
        "review_count": 67,
        "clinic_name": "Harbor Heart Institute",
        "location": "Soho",
        "consultation_fee_min": 130,
        "consultation_fee_max": 210,
        "next_available_slot": "Thursday, 11:15 AM",
        "appointment_types": ["TELEMEDICINE"],
        "languages": ["English", "Korean"],
        "description": "Cardiologist supporting blood pressure management and long-term monitoring.",
        "image_url": "/avatars/doctor-james.svg",
    },
    {
        "name": "Dr. Lucy Bennett",
        "specialty": "Pediatrics",
        "rating": 4.8,
        "review_count": 143,
        "clinic_name": "Little Oaks Pediatric Hub",
        "location": "Westminster",
        "consultation_fee_min": 90,
        "consultation_fee_max": 140,
        "next_available_slot": "Friday, 8:45 AM",
        "appointment_types": ["IN_PERSON"],
        "languages": ["English", "French"],
        "description": "Pediatric specialist known for calm, parent-friendly visits and practical guidance.",
        "image_url": "/avatars/doctor-elena.svg",
    },
    {
        "name": "Dr. Noah Turner",
        "specialty": "Internal Medicine",
        "rating": 4.7,
        "review_count": 109,
        "clinic_name": "North Bridge Medical",
        "location": "London, UK",
        "consultation_fee_min": 110,
        "consultation_fee_max": 170,
        "next_available_slot": "Monday, 10:30 AM",
        "appointment_types": ["IN_PERSON", "TELEMEDICINE"],
        "languages": ["English", "German"],
        "description": "Internal medicine doctor focused on metabolic health and prevention strategies.",
        "image_url": "/avatars/doctor-marcus.svg",
    },
    {
        "name": "Dr. Priya Nair",
        "specialty": "General Practice",
        "rating": 4.8,
        "review_count": 156,
        "clinic_name": "Harbour Family Practice",
        "location": "Chelsea",
        "consultation_fee_min": 75,
        "consultation_fee_max": 130,
        "next_available_slot": "Tomorrow, 1:30 PM",
        "appointment_types": ["TELEMEDICINE"],
        "languages": ["English", "Hindi"],
        "description": "General practitioner offering routine care and virtual follow-ups for families.",
        "image_url": "/avatars/doctor-sarah.svg",
    },
    {
        "name": "Dr. Sofia Martinez",
        "specialty": "Dermatology",
        "rating": 4.9,
        "review_count": 188,
        "clinic_name": "Lumen Skin Center",
        "location": "Mayfair",
        "consultation_fee_min": 160,
        "consultation_fee_max": 260,
        "next_available_slot": "Saturday, 10:00 AM",
        "appointment_types": ["IN_PERSON", "TELEMEDICINE"],
        "languages": ["English", "Spanish"],
        "description": "Dermatologist with expertise in skin health, acne treatment, and follow-up care.",
        "image_url": "/avatars/doctor-elena.svg",
    },
]

DOCTOR_AVAILABILITY_SEED_DATA = {
    "Dr. Sarah Jenkins": [
        {
            "available_date": date(2026, 6, 9),
            "start_time": "10:30",
            "end_time": "11:00",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 9),
            "start_time": "15:00",
            "end_time": "15:30",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    "Dr. Marcus Chen": [
        {
            "available_date": date(2026, 6, 10),
            "start_time": "09:00",
            "end_time": "09:30",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 10),
            "start_time": "14:00",
            "end_time": "14:30",
            "appointment_type": "IN_PERSON",
        },
    ],
    "Dr. Elena Rodriguez": [
        {
            "available_date": date(2026, 6, 11),
            "start_time": "10:00",
            "end_time": "10:30",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 11),
            "start_time": "16:00",
            "end_time": "16:30",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    "Dr. James Wilson": [
        {
            "available_date": date(2026, 6, 12),
            "start_time": "09:45",
            "end_time": "10:15",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 12),
            "start_time": "15:15",
            "end_time": "15:45",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    "Dr. Aisha Khan": [
        {
            "available_date": date(2026, 6, 13),
            "start_time": "11:15",
            "end_time": "11:45",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 13),
            "start_time": "17:00",
            "end_time": "17:30",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    "Dr. Daniel Park": [
        {
            "available_date": date(2026, 6, 14),
            "start_time": "10:45",
            "end_time": "11:15",
            "appointment_type": "TELEMEDICINE",
        },
        {
            "available_date": date(2026, 6, 14),
            "start_time": "13:30",
            "end_time": "14:00",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    "Dr. Lucy Bennett": [
        {
            "available_date": date(2026, 6, 15),
            "start_time": "08:45",
            "end_time": "09:15",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 15),
            "start_time": "12:45",
            "end_time": "13:15",
            "appointment_type": "IN_PERSON",
        },
    ],
    "Dr. Noah Turner": [
        {
            "available_date": date(2026, 6, 16),
            "start_time": "10:30",
            "end_time": "11:00",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 16),
            "start_time": "15:30",
            "end_time": "16:00",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    "Dr. Priya Nair": [
        {
            "available_date": date(2026, 6, 17),
            "start_time": "13:30",
            "end_time": "14:00",
            "appointment_type": "TELEMEDICINE",
        },
        {
            "available_date": date(2026, 6, 17),
            "start_time": "18:00",
            "end_time": "18:30",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    "Dr. Sofia Martinez": [
        {
            "available_date": date(2026, 6, 18),
            "start_time": "10:00",
            "end_time": "10:30",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 18),
            "start_time": "14:30",
            "end_time": "15:00",
            "appointment_type": "TELEMEDICINE",
        },
    ],
}


def seed_doctors(session: Session) -> None:
    existing_names = {name for (name,) in session.query(Doctor.name).all()}
    created = False

    for doctor_data in DOCTOR_SEED_DATA:
        if doctor_data["name"] in existing_names:
            continue

        session.add(
            Doctor(
                name=doctor_data["name"],
                specialty=doctor_data["specialty"],
                rating=doctor_data["rating"],
                review_count=doctor_data["review_count"],
                clinic_name=doctor_data["clinic_name"],
                location=doctor_data["location"],
                consultation_fee_min=doctor_data["consultation_fee_min"],
                consultation_fee_max=doctor_data["consultation_fee_max"],
                next_available_slot=doctor_data["next_available_slot"],
                appointment_types=Doctor.encode_list(doctor_data["appointment_types"]),
                languages=Doctor.encode_list(doctor_data["languages"]),
                description=doctor_data["description"],
                image_url=doctor_data["image_url"],
                is_active=True,
            )
        )
        created = True

    if created:
        session.commit()


def seed_availability(session: Session) -> None:
    existing_slots = {
        (
            availability.doctor_id,
            availability.available_date,
            availability.start_time,
            availability.appointment_type,
        )
        for availability in session.query(DoctorAvailability).all()
    }
    doctors_by_name = {doctor.name: doctor.id for doctor in session.query(Doctor).all()}
    created = False

    for doctor_name, slots in DOCTOR_AVAILABILITY_SEED_DATA.items():
        doctor_id = doctors_by_name.get(doctor_name)
        if doctor_id is None:
            continue

        for slot_data in slots:
            slot_key = (
                doctor_id,
                slot_data["available_date"],
                slot_data["start_time"],
                slot_data["appointment_type"],
            )
            if slot_key in existing_slots:
                continue

            session.add(
                DoctorAvailability(
                    doctor_id=doctor_id,
                    available_date=slot_data["available_date"],
                    start_time=slot_data["start_time"],
                    end_time=slot_data["end_time"],
                    appointment_type=slot_data["appointment_type"],
                    is_booked=False,
                )
            )
            created = True

    if created:
        session.commit()
