import pytest
from unittest import mock
from it_automation.reports import generate_report

@mock.patch("it_automation.reports.getSampleStyleSheet")
@mock.patch("it_automation.reports.Paragraph")
@mock.patch("it_automation.reports.Spacer")
@mock.patch("it_automation.reports.SimpleDocTemplate")
def test_generate_report(mock_simpleDocTemplate,
                         mock_spacer,
                         mock_paragraph,
                         mock_getSampleStyleSheet,
                         ):
    mock_getSampleStyleSheet.return_value = mock.MagicMock(name="mock_style")
    mock_simpleDocTemplate.return_value = mock.Mock(
        name="mock_doc",
        **{"build.return_value": "test mock doc return value"}
    )
    mock_paragraph.return_value = "test paragraph return value"
    mock_spacer.return_value = "test spacer return value"

    report_path = "mock report path"
    title = "mock title"
    paragraph = "fake paragraph"
    generate_report(report_path, title, paragraph)

    mock_paragraph_call_list = [
        mock.call(title, mock_getSampleStyleSheet()['h1']),
        mock.call(paragraph, mock_getSampleStyleSheet()['BodyText'])
    ]
    mock_paragraph.assert_has_calls(calls=mock_paragraph_call_list)

    mock_spacer.assert_called()
    mock_getSampleStyleSheet.assert_called()
    mock_simpleDocTemplate.return_value.build.assert_called()

    build_called_with = [
        'test paragraph return value',
        "test spacer return value",
        "test paragraph return value"
    ]
    mock_simpleDocTemplate.return_value.build.assert_called_with(
        build_called_with)
