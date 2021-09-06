import os.path
import pytest
from unittest import mock
from it_automation.supplier_image_upload import post_images

@pytest.mark.parametrize(
    "_input, expected",
    [(201, "Success"), (400, "POST error status=400")]
)
@mock.patch("it_automation.run.requests.post")
def test_post_images(mock_requests_post, _input, expected):
    mock_requests_post.return_value = mock.Mock(**{"status_code": _input})

    test_url = 'test_url'
    test_image_directory = os.path.expanduser('~') + '/Documents' \
                                                '/google_class' \
                                                '/project_8' \
                                                '/tests' \
                                                '/images'
    if _input != 201:
        with pytest.raises(Exception, match=expected):
            post_images(test_url, test_image_directory)
    else:
        post_images(test_url, test_image_directory)
    mock_requests_post.assert_called()