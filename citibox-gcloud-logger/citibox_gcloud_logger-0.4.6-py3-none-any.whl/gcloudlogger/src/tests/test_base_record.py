import unittest

from citibox.gcloudlogger.src.base_record import BaseRecord, Body, Response, ResponseHeaders, RequestHeaders, Request,\
    Params


class TestBody(unittest.TestCase):
    def test_init(self):
        body = Body(**{'attr_1': 'a1', 'attr_2': 'a2'}).to_dict()

        self.assertIn('attr_1', body)
        self.assertEqual(body['attr_1'], 'a1')
        self.assertIn('attr_2', body)
        self.assertEqual(body['attr_2'], 'a2')

    def test_empty_body(self):
        body = Body().to_dict()

        self.assertEqual(body, {})


class TestRequestHeaders(unittest.TestCase):
    def test_init(self):
        request_headers = RequestHeaders(
            **{'attr_1': 'a1', 'attr_2': 'a2'}
        ).to_dict()

        self.assertIn('attr_1', request_headers)
        self.assertEqual(request_headers['attr_1'], 'a1')
        self.assertIn('attr_2', request_headers)
        self.assertEqual(request_headers['attr_2'], 'a2')


class TestResponseHeaders(unittest.TestCase):
    def test_init(self):
        response_headers = ResponseHeaders(**{'attr_1': 'a1', 'attr_2': 'a2'}).to_dict()

        self.assertIn('attr_1', response_headers)
        self.assertEqual(response_headers['attr_1'], 'a1')
        self.assertIn('attr_2', response_headers)
        self.assertEqual(response_headers['attr_2'], 'a2')

    def test_empty_body(self):
        response_headers = ResponseHeaders().to_dict()
        self.assertEqual(response_headers, {})


class TestParams(unittest.TestCase):
    def test_init(self):
        params = Params(**{'attr_1': 'a1', 'attr_2': 'a2'}).to_dict()

        self.assertIn('attr_1', params)
        self.assertEqual(params['attr_1'], 'a1')
        self.assertIn('attr_2', params)
        self.assertEqual(params['attr_2'], 'a2')

    def test_empty_body(self):
        params = Params().to_dict()
        self.assertEqual(params, {})


class TestRequest(unittest.TestCase):
    def test_init(self):
        request = Request(
            headers=RequestHeaders(
                **{'attr1': 'a1'}
            ),
            params=Params(
                **{'attr2': 'a2'}
            ),
            body=Body(
                **{'attr2': 'a2'}
            )
        ).to_dict()

        self.assertIn('headers', request)
        self.assertIn('params', request)
        self.assertIn('body', request)

    def test_init_ok_when_no_body(self):
        request = Request(
            headers=RequestHeaders(
                **{'attr1': 'a1'}
            ),
            params=Params(
                **{'attr2': 'a2'}
            ),
        ).to_dict()

        self.assertIn('body', request)
        self.assertIsNone(request['body'])

    def test_error_raised_when_no_params_or_none_params(self):
        with self.assertRaises(TypeError):
           Request(
                headers=RequestHeaders(
                    **{'attr1': 'a1'}
                ),
                body=Body(
                    **{'attr2': 'a2'}
                )
            ).to_dict()

        with self.assertRaises(AssertionError):
           Request(
               headers=RequestHeaders(
                   **{'attr1': 'a1'}
               ),
               params=None,
               body=Body(
                   **{'attr2': 'a2'}
               )
            ).to_dict()

    def test_error_raised_when_no_headers_or_none_headers(self):
        with self.assertRaises(TypeError):
            Request(
                params=Params(
                    **{'attr2': 'a2'}
                ),
                body=Body(
                    **{'attr2': 'a2'}
                )
            ).to_dict()

        with self.assertRaises(AssertionError):
            Request(
                headers=None,
                params=Params(
                    **{'attr2': 'a2'}
                ),
                body=Body(
                    **{'attr2': 'a2'}
                )
            ).to_dict()


class TestResponse(unittest.TestCase):
    def test_init(self):
        body = Body(
                **{'attr1': 'a1'}
        )

        response_headers = ResponseHeaders(
                **{'attr2': 'a2'}
            )

        response = Response(
            status_code='http_200_ok',
            body=body,
            headers=response_headers
        )

        response_dict = response.to_dict()

        self.assertEqual(response.status_code, 'http_200_ok')
        self.assertEqual(response.body, body)

        self.assertIn('status_code', response_dict)
        self.assertEqual(response_dict['status_code'], 'http_200_ok')
        self.assertIn('body', response_dict)
        self.assertEqual(response_dict['body'], body.to_dict())
        self.assertIn('headers', response_dict)
        self.assertEqual(response_dict['headers'], response_headers.to_dict())

    def test_error_raised_with_no_status_code_or_none_status_code(self):
        with self.assertRaises(TypeError):
            Response(
                body=Body(
                    **{'attr1': 'a1'}
                ),
                headers=ResponseHeaders(
                    **{'attr2': 'a2'}
                )
            )

        with self.assertRaises(AssertionError):
            Response(
                status_code=None,
                body=Body(
                    **{'attr1': 'a1'}
                ),
                headers=ResponseHeaders(
                    **{'attr2': 'a2'}
                )
            )


class TestBaseRecord(unittest.TestCase):
    def test_init(self):

        base_record, request, response = self._create_base_record()

        base_record_dict = base_record.to_dict()

        self.assertEqual(base_record.message, 'POST 200 OK path')

        self.assertIn('url_fingerprint', base_record_dict)
        self.assertEqual(base_record_dict['url_fingerprint'], 'url_fingerprint')
        self.assertIn('duration', base_record_dict)
        self.assertEqual(base_record_dict['duration'], 'duration')
        self.assertIn('method', base_record_dict)
        self.assertEqual(base_record_dict['method'], 'POST')
        self.assertIn('path', base_record_dict)
        self.assertEqual(base_record_dict['path'], 'path')
        self.assertIn('host', base_record_dict)
        self.assertEqual(base_record_dict['host'], 'host')
        self.assertIn('request', base_record_dict)
        self.assertEqual(base_record_dict['request'], request.to_dict())
        self.assertIn('response', base_record_dict)
        self.assertEqual(base_record_dict['response'], response.to_dict())
        self.assertIn('br_attr1', base_record_dict)
        self.assertEqual(base_record_dict['br_attr1'], 'br_a1')

    def test_error_raised_when_none_params(self):
        with self.assertRaises(AssertionError):
            self._create_base_record(response_none=True)

        with self.assertRaises(AssertionError):
            self._create_base_record(request_none=True)

        with self.assertRaises(AssertionError):
            self._create_base_record(url_fingerprint_none=True)

        with self.assertRaises(AssertionError):
            self._create_base_record(duration_none=True)

        with self.assertRaises(AssertionError):
            self._create_base_record(path_none=True)

        with self.assertRaises(AssertionError):
            self._create_base_record(method_none=True)

        with self.assertRaises(AssertionError):
            self._create_base_record(host_none=True)

    def _create_base_record(
        self,
        request_none=False,
        response_none=False,
        url_fingerprint_none=False,
        duration_none=False,
        path_none=False,
        method_none=False,
        host_none=False
    ):

        request = Request(
            headers=RequestHeaders(
                **{'attr1': 'a1'}
            ),
            params=Params(
                **{'attr2': 'a2'}
            )
        ) if not request_none else None

        response = Response(
            status_code='200 OK',
            body=Body(
                **{'attr1': 'a1'}
            ),
            headers=ResponseHeaders(
                **{'attr2': 'a2'}
            )
        ) if not response_none else None

        base_record = BaseRecord(
            url_fingerprint='url_fingerprint' if not url_fingerprint_none else None,
            duration='duration' if not duration_none else None,
            method='POST' if not method_none else None,
            path='path' if not path_none else None,
            host='host' if not host_none else None,
            request=request,
            response=response,
            **{'br_attr1': 'br_a1'}
        )

        return base_record, request, response
