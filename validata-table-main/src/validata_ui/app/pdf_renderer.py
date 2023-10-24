"""PDF report rendering utilities."""
import json
import logging
import subprocess
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import requests

log = logging.getLogger(__name__)


class PDFRenderer(ABC):
    """Abstract PDF renderer."""

    @abstractmethod
    def render(self, url: str) -> bytes:
        """Render a PDF document content from given URL."""
        pass

    @staticmethod
    def create_renderer_from_config(config):
        """PDF renderer instance factory."""
        if config.BROWSERLESS_API_URL and config.BROWSERLESS_API_TOKEN:
            log.info("Creating Browserless.io PDF renderer")
            return BrowserlessPDFRenderer(
                config.BROWSERLESS_API_URL, config.BROWSERLESS_API_TOKEN
            )

        # fallback
        log.info("Creating Chromium headless PDF renderer")
        return ChromiumHeadlessPDFRenderer()


class BrowserlessPDFRenderer(PDFRenderer):
    """Browserless IO implementation."""

    def __init__(self, api_url: str, api_token: str):
        """Create browserless.io implementation."""
        log.info("BrowserlessPDFRenderer: creating instance with api_url = %r", api_url)
        self.api_url = api_url
        self.api_token = api_token

    def render(self, url: str) -> bytes:
        """Call browserless.io service to generate PDF."""
        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
        }
        params = {"token": self.api_token}
        data = {
            "url": url,
            "options": {
                "displayHeaderFooter": True,
                "printBackground": False,
                "format": "A4",
            },
            "gotoOptions": {
                "waitUntil": "networkidle0",
            },
        }
        log.info(
            "BrowserlessPDFRenderer.render: about to send a POST request to "
            "browserless with data = %r and headers = %r",
            json.dumps(data),
            json.dumps(headers),
        )

        # Request server
        r = requests.post(
            self.api_url, headers=headers, params=params, data=json.dumps(data)
        )
        r.raise_for_status()
        log.info(
            "BrowserlessPDFRenderer.render: received response, content size = %d",
            len(r.content),
        )
        return r.content


class ChromiumHeadlessPDFRenderer(PDFRenderer):
    """Chromium implementation."""

    def render(self, url: str) -> bytes:
        """Render PDF document using Chromium headless."""
        # Create temp file to save validation report
        # This temp file will be automatically deleted on context exit
        with tempfile.NamedTemporaryFile(
            prefix="validata_{}_report_".format(datetime.now().timestamp()),
            suffix=".pdf",
        ) as tmpfile:
            tmp_pdf_report = Path(tmpfile.name)

            # Use chromium headless to generate PDF from validation report page
            cmd = [
                "chromium",
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                f"--print-to-pdf={tmp_pdf_report}",
                url,
            ]

            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            if result.returncode != 0:
                output = result.stdout.decode("utf-8")
                log.error("Command %r returned an error: %r", cmd, output)
                raise ValueError("Erreur lors de la génération du rapport PDF")

            return tmp_pdf_report.read_bytes()
