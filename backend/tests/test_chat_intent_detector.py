from datetime import date, timedelta

from app.schemas.chat import ChatIntent
from app.services.chat_intent_detector import detect_chat_intent


def test_detect_chat_intent_for_specialization_query():
    match = detect_chat_intent("Show cardiologists")

    assert match.intent == ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION
    assert match.specialty == "Cardiology"
    assert match.target_date is None


def test_detect_chat_intent_for_availability_query():
    match = detect_chat_intent("Who is available tomorrow?")

    assert match.intent == ChatIntent.SHOW_AVAILABLE_DOCTORS
    assert match.specialty is None
    assert match.target_date == date.today() + timedelta(days=1)


def test_detect_chat_intent_for_doctor_details_query():
    match = detect_chat_intent("What is Dr. Sarah Jenkins fee?")

    assert match.intent == ChatIntent.SHOW_DOCTOR_DETAILS
    assert match.specialty is None
    assert match.target_date is None


def test_detect_chat_intent_for_appointment_help_query():
    match = detect_chat_intent("How do I book an appointment?")

    assert match.intent == ChatIntent.APPOINTMENT_HELP


def test_detect_chat_intent_for_unknown_query():
    match = detect_chat_intent("Need some help")

    assert match.intent == ChatIntent.UNKNOWN
    assert match.specialty is None
    assert match.target_date is None
