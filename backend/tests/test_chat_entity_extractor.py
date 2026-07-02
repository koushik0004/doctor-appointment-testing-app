from datetime import date, timedelta

from app.services.chat_entity_extractor import extract_chat_search_filters


def test_extract_chat_search_filters_for_specialty_gender_and_date():
    filters = extract_chat_search_filters("Need a female cardiologist tomorrow")

    assert filters.specialization == "Cardiology"
    assert filters.gender == "Female"
    assert filters.date == date.today() + timedelta(days=1)
    assert filters.minimum_fee is None
    assert filters.maximum_fee is None


def test_extract_chat_search_filters_for_fee_and_location():
    filters = extract_chat_search_filters("Show doctors under ₹200 near Soho clinic")

    assert filters.specialization is None
    assert filters.maximum_fee == 200
    assert filters.minimum_fee is None
    assert filters.clinic_location == "Soho"


def test_extract_chat_search_filters_for_time_preference():
    filters = extract_chat_search_filters("Need a pediatrician after 5 PM")

    assert filters.specialization == "Pediatrics"
    assert filters.time_preference == "After 5:00 PM"


def test_extract_chat_search_filters_does_not_infer_gender_from_payment_methods():
    filters = extract_chat_search_filters("What payment methods are accepted?")

    assert filters.gender is None
