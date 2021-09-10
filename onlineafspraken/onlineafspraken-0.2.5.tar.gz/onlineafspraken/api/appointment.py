from onlineafspraken.api.client import OnlineAfsprakenAPI, client
from onlineafspraken.schema.appointment import (
    CancelAppointmentResponse,
    ConfirmAppointmentResponse,
    GetAppointmentsResponse,
    GetAppointmentResponse,
    SetAppointmentResponse,
    SetAppointmentSchema,
    AppointmentSchema,
)


def cancel_appointment(
    appointment_id, mode=None, remarks=None, confirmation=None, dry_run=None
) -> CancelAppointmentResponse:

    resp = client.get(
        "cancelAppointment",
        Id=appointment_id,
        Mode=mode,
        Remarks=remarks,
        Confirmation=confirmation,
        DryRun=dry_run,
    )

    return CancelAppointmentResponse.parse_obj(resp)


def confirm_appointment(
    appointment_id, confirmation_code
) -> ConfirmAppointmentResponse:

    resp = client.get(
        "confirmAppointment", Id=appointment_id, ConfirmationCode=confirmation_code
    )

    return ConfirmAppointmentResponse.parse_obj(resp)


def get_appointments(
    agenda_id,
    start_date,
    end_date,
    customer_id=None,
    appointment_type_id=None,
    resource_id=None,
    include_cancelled=None,
    limit=None,
    offset=None,
) -> GetAppointmentsResponse:

    resp = client.get(
        "getAppointments",
        AgendaId=agenda_id,
        StartDate=start_date,
        EndDate=end_date,
        CustomerId=customer_id,
        AppointmentTypeId=appointment_type_id,
        ResourceId=resource_id,
        IncludeCancelled=include_cancelled,
        Limit=limit,
        Offset=offset,
    )

    return GetAppointmentsResponse.parse_obj(resp)


def get_appointment(appointment_id) -> AppointmentSchema:

    resp = client.get("getAppointment", Id=appointment_id)

    return GetAppointmentResponse.parse_obj(resp).appointment


def remove_appointment(appointment_id) -> None:

    response = client.get("removeAppointment", Id=appointment_id)

    return response


def set_appointment(
    agenda_id,
    start_time,
    date,
    customer_id,
    appointment_type_id,
    end_time=None,
    appointment_id=None,
    name=None,
    description=None,
    booking_mode=None,
    **custom_fields
) -> SetAppointmentSchema:

    resp = client.get(
        "setAppointment",
        Id=appointment_id,
        AgendaId=agenda_id,
        StartTime=start_time,
        Date=date,
        CustomerId=customer_id,
        AppointmentTypeId=appointment_type_id,
        EndTime=end_time,
        Name=name,
        Description=description,
        BookingMode=booking_mode,
        **custom_fields,
    )

    response = SetAppointmentResponse.parse_obj(resp)

    return response.objects["Appointment"]
