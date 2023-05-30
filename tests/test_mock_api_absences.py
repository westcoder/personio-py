import re
from datetime import date

import pytest
import responses

from personio_py import PersonioError, Absence, Employee
from tests.mock_data import (
    json_dict_absence_alan,
    json_dict_absence_types,
    json_dict_empty_response,
    json_dict_delete_absence,
    json_dict_absence_alan_first,
    json_dict_absence_create_no_halfdays,
    json_dict_get_absence
)
from tests.test_mock_api import mock_personio, compare_labeled_attributes, mock_employees


@responses.activate
def test_get_absence_from_id():
    personio = mock_personio()
    mock_get_absence()
    absence_id_only = Absence(id_=2628890)
    absence = personio.get_absence(absence_id_only)
    assert absence.employee.first_name == 'Alan'
    assert absence.employee.last_name == 'Turing'
    assert absence.id_ == 2628890
    assert absence.start_date == date(2021, 1, 1)
    assert absence.end_date == date(2021, 1, 10)


@responses.activate
def test_get_absence_from_object_without_id():
    personio = mock_personio()
    mock_get_absence()
    mock_single_absences()
    absence_id_only = Absence(id_=2628890)
    absence = personio.get_absence(absence_id_only)
    absence.id_ = None
    personio.get_absence(absence)


@responses.activate
def test_create_absence():
    mock_absence_types()
    mock_create_absence_no_halfdays()
    personio = mock_personio()
    absence_type = personio.get_absence_types()[0]
    employee = Employee(
        first_name="Alan",
        last_name='Turing',
        email='alan.turing@cetitec.com'
    )
    absence = Absence(
        client=personio,
        employee=employee,
        start_date=date(2020, 1, 1),
        end_date=date(2020, 1, 10),
        half_day_start=False,
        half_day_end=False,
        time_off_type=absence_type)
    absence.create()
    assert absence.id_


@responses.activate
def test_delete_absence():
    mock_delete_absence()
    personio = mock_personio()
    result = personio.delete_absence(2116365)
    assert result is True


@responses.activate
def test_delete_absence_no_client():
    personio = mock_personio()
    mock_absences()
    absence = personio.get_absences(2116365)[0]
    absence._client = None
    with pytest.raises(PersonioError):
        absence.delete()


@responses.activate
def test_delete_absence_passed_client():
    personio = mock_personio()
    mock_absences()
    mock_delete_absence()
    absence = personio.get_absences(2116365)[0]
    absence._client = None
    assert absence.delete(client=personio) is True


@responses.activate
def test_delete_absence_no_id():
    personio = mock_personio()
    mock_absences()
    absence = personio.get_absences(2116365)[0]
    absence.id_ = None
    with pytest.raises(ValueError):
        absence.delete()
    with pytest.raises(ValueError):
        personio.delete_absence(absence)


@responses.activate
def test_get_absences():
    # configure personio & get absences for alan
    mock_absences()
    personio = mock_personio()
    absences = personio.get_absences(2116365)
    # validate
    assert len(absences) == 3
    selection = [a for a in absences if "marathon" in a.comment.lower()]
    assert len(selection) == 1
    marathon = selection[0]
    assert marathon.start_date == date(1944, 9, 1)
    assert marathon.half_day_start == 0
    assert marathon.half_day_end == 1
    assert marathon.status == 'approved'
    # validate serialization
    source_dict = json_dict_absence_alan['data'][0]
    target_dict = marathon.to_dict()
    compare_labeled_attributes(source_dict, target_dict)


@responses.activate
def test_get_absences_from_employee_objects():
    # mock endpoints & get absences for all employees
    mock_employees()
    mock_absences()
    personio = mock_personio()
    employees = personio.get_employees()
    assert employees
    absences = personio.get_absences(employees)
    # the response is not important (it does not match the input), but the function should accept
    # a list of Employee objects as parameter and return a result
    assert absences


@responses.activate
def test_get_absence_types():
    mock_absence_types()
    # configure personio & get absences for alan
    personio = mock_personio()
    absence_types = personio.get_absence_types()
    # non-empty contents
    assert len(absence_types) == 3
    for at in absence_types:
        assert at.id_ > 0
        assert isinstance(at.name, str)
    # serialization matches input
    for source_dict, at in zip(json_dict_absence_types['data'], absence_types):
        target_dict = at.to_dict()
        assert source_dict == target_dict


def mock_absence_types():
    # mock the get absence types endpoint
    responses.add(
        responses.GET,
        'https://api.personio.de/v1/company/time-off-types',
        status=200,
        json=json_dict_absence_types,
        adding_headers={'Authorization': 'Bearer foo'})


def mock_absences():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET,
        re.compile('https://api.personio.de/v1/company/time-offs?.*offset=1.*'),
        status=200,
        json=json_dict_absence_alan,
        adding_headers={'Authorization': 'Bearer foo'})


def mock_single_absences():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET,
        re.compile('https://api.personio.de/v1/company/time-offs?.*offset=1.*'),
        status=200,
        json=json_dict_absence_alan_first,
        adding_headers={'Authorization': 'Bearer foo'})


def mock_no_absences():
    # mock the get absences endpoint
    responses.add(
        responses.GET,
        re.compile('https://api.personio.de/v1/company/time-offs?.*offset=1.*'),
        status=200,
        json=json_dict_empty_response,
        adding_headers={'Authorization': 'Bearer bar'})


def mock_delete_absence():
    # mock the delete endpoint
    responses.add(
        responses.DELETE,
        re.compile('https://api.personio.de/v1/company/time-offs/*'),
        status=200,
        json=json_dict_delete_absence,
        adding_headers={'Authorization': 'Bearer bar'})


def mock_create_absence_no_halfdays():
    responses.add(
        responses.POST,
        'https://api.personio.de/v1/company/time-offs',
        status=200,
        json=json_dict_absence_create_no_halfdays,
        adding_headers={'Authorization': 'Bearer bar'})


def mock_get_absence():
    responses.add(
        responses.GET,
        re.compile('https://api.personio.de/v1/company/time-offs/.*'),
        status=200,
        json=json_dict_get_absence,
        adding_headers={'Authorization': 'Bearer bar'})
