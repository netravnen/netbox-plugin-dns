from importlib.metadata import version

from django.test import SimpleTestCase
from django.urls import reverse

from netbox_dns import __version__, config
from utilities.testing.api import APITestCase


class NetBoxDNSVersionTestCase(SimpleTestCase):
    def test_version(self):
        self.assertTrue(__version__)
        self.assertEqual(__version__, version("netbox-plugin-dns"))
        self.assertEqual(config.version, __version__)


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("plugins-api:netbox_dns-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)

        self.assertEqual(response.status_code, 200)
