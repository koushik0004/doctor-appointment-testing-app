from fastapi import HTTPException, status


def doctor_not_found(doctor_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Doctor {doctor_id} not found",
    )
