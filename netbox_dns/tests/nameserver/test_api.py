from netbox_dns.models import NameServer
from netbox_dns.tests.custom import (
    APITestCase,
    CustomFieldTargetAPIMixin,
    NetBoxDNSGraphQLMixin,
)
from utilities.testing import APIViewTestCases


class NameServerAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    CustomFieldTargetAPIMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = NameServer

    brief_fields = ["description", "display", "id", "name", "url"]

    create_data = [
        {"name": "ns1.example.com"},
        {"name": "ns2.example.com"},
        {"name": "ns3.example.com"},
    ]

    bulk_update_data = {
        "description": "Test Name Server",
    }
    bulk_update_invalid_data = {
        "name": "aa,bb",
    }

    @classmethod
    def setUpTestData(cls):
        nameservers = (
            NameServer(name="ns4.example.com"),
            NameServer(name="ns5.example.com"),
            NameServer(name="ns6.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)
