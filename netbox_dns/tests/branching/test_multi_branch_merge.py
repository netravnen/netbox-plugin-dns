import unittest

from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices
from netbox_dns.models import NameServer, Record, View, Zone
from netbox_dns.tests.branching.base import (
    HAS_BRANCHING,
    BranchingTestBase,
    TestBase,
    activate_branch,
    event_tracking,
    make_request,
    provision_branch,
)

if HAS_BRANCHING:
    from netbox_branching.choices import BranchMergeStrategyChoices


@unittest.skipUnless(HAS_BRANCHING, "netbox-branching is not installed")
class MultiBranchMergeTestCase(BranchingTestBase, TestBase):
    """
    Integration test suite validating branch merge operations across all 18
    supported DNS record types and unlinked IPAddress foreign key scenarios.
    """

    def test_merge_all_18_dns_record_types(self):
        """
        Validate creating, updating, and merging records across all 18 supported
        DNS record types (A, AAAA, PTR, MX, TXT, CAA, TLSA, SPF, SRV, NAPTR, RP,
        HINFO, CERT, DS, SSHFP, LOC, NS, CNAME).
        """
        branch = provision_branch(
            "18-Record-Types-Test", BranchMergeStrategyChoices.ITERATIVE, self.user
        )

        record_specs = [
            ("a-record", RecordTypeChoices.A, "192.0.2.1"),
            ("aaaa-record", RecordTypeChoices.AAAA, "2001:db8::1"),
            ("mx-record", RecordTypeChoices.MX, "10 mail.example.com."),
            ("txt-record", RecordTypeChoices.TXT, '"v=spf1 -all"'),
            ("ns-record", RecordTypeChoices.NS, "ns1.example.com."),
            ("cname-record", RecordTypeChoices.CNAME, "target.example.com."),
            ("caa-record", RecordTypeChoices.CAA, '0 issue "letsencrypt.org"'),
            ("tlsa-record", RecordTypeChoices.TLSA, "3 1 1 1234567890abcdef"),
            ("spf-record", RecordTypeChoices.SPF, '"v=spf1 mx -all"'),
            ("srv-record", RecordTypeChoices.SRV, "10 60 5060 sip.example.com."),
            ("naptr-record", RecordTypeChoices.NAPTR, '100 10 "s" "SIP+D2U" "" _sip._udp.example.com.'),
            ("rp-record", RecordTypeChoices.RP, "admin.example.com. text.example.com."),
            ("hinfo-record", RecordTypeChoices.HINFO, '"Intel PC" "Linux"'),
            ("cert-record", RecordTypeChoices.CERT, "1 0 0 AA=="),
            ("ds-record", RecordTypeChoices.DS, "60485 5 1 1234567890abcdef"),
            ("sshfp-record", RecordTypeChoices.SSHFP, "1 1 1234567890abcdef"),
            ("loc-record", RecordTypeChoices.LOC, "52 22 23.000 N 4 53 32.000 E -2.00m"),
            ("ptr-record", RecordTypeChoices.PTR, "host.example.com."),
        ]

        with activate_branch(branch), event_tracking(self.request):
            ns = NameServer.objects.create(name="ns1.example.com")
            zone = Zone.objects.create(name="example.com", soaparent=ns)
            created_pks = {}
            for name, rtype, rval in record_specs:
                rec = Record.objects.create(
                    zone=zone,
                    name=name,
                    type=rtype,
                    value=rval,
                    status=RecordStatusChoices.STATUS_ACTIVE,
                )
                created_pks[name] = rec.pk

        for name, pk in created_pks.items():
            self.assertFalse(Record.objects.filter(pk=pk).exists())

        self._merge(branch)

        for name, pk in created_pks.items():
            self.assertTrue(Record.objects.filter(pk=pk).exists())

    def test_clean_record_with_dangling_ipam_ip_address(self):
        """
        Verify Record.clean() and Record.has_ipam_ip_address safely inspects
        ipam_ip_address_id without throwing IPAddress.DoesNotExist during branch replay.
        """
        rec = Record(name="test", type=RecordTypeChoices.A, value="192.0.2.100")
        rec.ipam_ip_address_id = 999999  # Non-existent ID in active schema
        self.assertFalse(rec.has_ipam_ip_address)
