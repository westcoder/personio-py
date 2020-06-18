from datetime import datetime, timezone

from personio_py import Absence

absence_dict = {
    'id': 42100,
    'status': 'approved',
    'comment': 'Christmas <3',
    'start_date': '1835-12-24T00:00:00+00:00',
    'end_date': '1835-12-31T00:00:00+00:00',
    'days_count': 5,
    'half_day_start': 0,
    'half_day_end': 0,
    'time_off_type': {'type': 'TimeOffType', 'attributes': {'id': 1, 'name': 'vacation'}},
    'employee': {
        'type': 'Employee',
        'attributes': {
            'id': {'label': 'ID', 'value': 42},
            'first_name': {'label': 'First name', 'value': 'Ada'},
            'last_name': {'label': 'Last name', 'value': 'Lovelace'},
            'email': {'label': 'Email', 'value': 'ada@example.org'}
        }
    },
    'created_by': 'Ada Lovelace',
    'certificate': {'status': 'not-required'},
    'created_at': '1835-12-01T13:15:00+00:00'
}


def test_parse_absence():
    absence = Absence.from_dict(absence_dict)
    assert absence
    assert absence.comment == 'Christmas <3'
    assert absence.created_by == 'Ada Lovelace'
    assert absence.start_date == datetime(1835, 12, 24, tzinfo=timezone.utc)
    assert absence.certificate.status == 'not-required'
    assert absence.time_off_type.name == 'vacation'
    assert absence.employee.id_ == 42


def test_serialize_absence():
    absence = Absence.from_dict(absence_dict)
    d = absence.to_dict()
    assert d == absence_dict
