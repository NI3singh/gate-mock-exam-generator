"""Tests for transient-failure retry/backoff in the LaTeX compile step."""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx

from app.services import pdf_service


class FakeResponse:
    def __init__(self, status_code, *, body=b"", text=None,
                 content_type="text/plain", json_data=None):
        self.status_code = status_code
        self.content = body
        self._text = text if text is not None else body.decode(errors="replace")
        self.headers = {"content-type": content_type}
        self._json = json_data

    @property
    def text(self):
        return self._text

    def json(self):
        if self._json is None:
            raise ValueError("no json body")
        return self._json


class FakeClient:
    """Returns scripted responses (or raises scripted exceptions) per .post()."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json=None):
        item = self.script[self.calls]
        self.calls += 1
        if isinstance(item, Exception):
            raise item
        return item


PDF_OK = b"%PDF-1.7 fake"


class LatexCompileRetryTests(unittest.TestCase):
    def setUp(self):
        self._orig = pdf_service.settings.LATEX_MAX_RETRIES
        pdf_service.settings.LATEX_MAX_RETRIES = 2  # -> 3 attempts total

    def tearDown(self):
        pdf_service.settings.LATEX_MAX_RETRIES = self._orig

    def _run(self, script):
        client = FakeClient(script)
        with patch.object(pdf_service.httpx, "AsyncClient", lambda *a, **k: client), \
                patch.object(pdf_service.asyncio, "sleep", new=AsyncMock()):
            try:
                result = asyncio.run(pdf_service._compile_latex_to_pdf("x"))
                return result, client, None
            except Exception as exc:  # noqa: BLE001
                return None, client, exc

    def test_success_first_try(self):
        result, client, err = self._run([FakeResponse(201, body=PDF_OK)])
        self.assertIsNone(err)
        self.assertTrue(result.startswith(b"%PDF"))
        self.assertEqual(client.calls, 1)

    def test_retries_on_5xx_then_succeeds(self):
        result, client, err = self._run([
            FakeResponse(503, body=b"busy"),
            FakeResponse(201, body=PDF_OK),
        ])
        self.assertIsNone(err)
        self.assertTrue(result.startswith(b"%PDF"))
        self.assertEqual(client.calls, 2)

    def test_retries_on_network_error_then_succeeds(self):
        result, client, err = self._run([
            httpx.ConnectError("connection refused"),
            FakeResponse(201, body=PDF_OK),
        ])
        self.assertIsNone(err)
        self.assertTrue(result.startswith(b"%PDF"))
        self.assertEqual(client.calls, 2)

    def test_no_retry_on_4xx_compilation_error(self):
        _, client, err = self._run([
            FakeResponse(
                400,
                body=b'{"detail":"COMPILATION_ERROR","logs":"! Undefined control sequence"}',
                content_type="application/json",
                json_data={"detail": "COMPILATION_ERROR",
                           "logs": "! Undefined control sequence"},
            ),
            FakeResponse(201, body=PDF_OK),  # would succeed if (wrongly) retried
        ])
        self.assertIsInstance(err, RuntimeError)
        self.assertEqual(client.calls, 1)  # must NOT retry a deterministic 4xx

    def test_raises_after_exhausting_retries(self):
        _, client, err = self._run([FakeResponse(503, body=b"busy")] * 5)
        self.assertIsInstance(err, RuntimeError)
        self.assertEqual(client.calls, 3)  # retries(2) + 1
        self.assertIn("3 attempt", str(err))

    def test_2xx_without_pdf_is_not_retried(self):
        _, client, err = self._run([
            FakeResponse(200, body=b"not a pdf"),
            FakeResponse(201, body=PDF_OK),
        ])
        self.assertIsInstance(err, RuntimeError)
        self.assertEqual(client.calls, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
