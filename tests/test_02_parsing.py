# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016, OVH SAS
#
# This file is part of Cerberus-core.
#
# Cerberus-core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
    Unit test for email parser
"""

import os

from tests import GlobalTestCase
from worker.parsing import parser

SAMPLES_DIRECTORY = 'tests/samples'


class TestParser(GlobalTestCase):
    """
        Unit tests for parser
    """
    def setUp(self):

        super(TestParser, self).setUp()
        self.email_parser = parser.EmailParser()
        self.samples = {}

        for root, dirs, files in os.walk(SAMPLES_DIRECTORY):
            for name in files:
                filename = root + '/' + name
                f = open(filename, 'r')
                self.samples[name] = f

    def tearDown(self):
        for k, v in self.samples.iteritems():
            v.close()

    def test_get_headers_sample1(self):

        sample = self.samples['sample1']
        headers = self.email_parser.get_headers(sample.read())
        self.assertIn('Date', headers)
        self.assertIn('From', headers)
        self.assertIn('Subject', headers)

    def test_get_sender_sample1(self):

        sample = self.samples['sample1']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        self.assertEqual('simon.vasseur@ovh.net', sender)

    def test_get_recipients_sample1(self):

        sample = self.samples['sample1']
        headers = self.email_parser.get_headers(sample.read())
        recipients = parser.get_recipients_from_headers(headers)
        self.assertIn('abuse@ovh.net', recipients)
        self.assertNotIn('simon.vasseur@ovh.net', recipients)

    def test_get_subject_sample1(self):

        sample = self.samples['sample1']
        headers = self.email_parser.get_headers(sample.read())
        subject = parser.get_subject_from_headers(headers)
        self.assertEqual('Encoding test', subject)

    def test_get_date_sample1(self):

        sample = self.samples['sample1']
        headers = self.email_parser.get_headers(sample.read())
        date = parser.get_date_from_headers(headers)
        self.assertEqual(1430342845, int(date))

    def test_get_template_sample1(self):

        sample = self.samples['sample1']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        template = self.email_parser.get_template(sender)
        self.assertEqual(None, template)

    def test_get_parsed_email_sample1(self):

        sample = self.samples['sample1']
        content = sample.read()
        parsed_email = self.email_parser.parse(content)

        self.assertEqual('Other', parsed_email.category)
        self.assertEqual(False, parsed_email.ack)
        self.assertEqual(True, parsed_email.trusted)
        self.assertIn(u'é"', parsed_email.body)
        self.assertEqual([], parsed_email.attachments)
        self.assertEqual(None, parsed_email.ips)
        self.assertEqual(None, parsed_email.urls)
        self.assertEqual(None, parsed_email.fqdn)

    def test_get_headers_sample2(self):

        sample = self.samples['sample2']
        headers = self.email_parser.get_headers(sample.read())
        self.assertIn('Date', headers)
        self.assertIn('From', headers)
        self.assertIn('Subject', headers)

    def test_get_sender_sample2(self):

        sample = self.samples['sample2']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        self.assertEqual('6301094139@reports.spamcop.net', sender)

    def test_get_recipients_sample2(self):

        sample = self.samples['sample2']
        headers = self.email_parser.get_headers(sample.read())
        recipients = parser.get_recipients_from_headers(headers)
        self.assertIn('abuse@ovh.net', recipients)
        self.assertNotIn('6301094139@reports.spamcop.net', recipients)

    def test_get_subject_sample2(self):

        sample = self.samples['sample2']
        headers = self.email_parser.get_headers(sample.read())
        subject = parser.get_subject_from_headers(headers)
        self.assertIn('[SpamCop (213.251.151.160) id:6301094139]{SPAM 07.7} =?UTF-8?Q?Impor', subject)

    def test_get_date_sample2(self):

        sample = self.samples['sample2']
        headers = self.email_parser.get_headers(sample.read())
        date = parser.get_date_from_headers(headers)
        self.assertEqual(1430342845, int(date))

    def test_get_parsed_email_sample2(self):

        sample = self.samples['sample2']
        content = sample.read()
        parsed_email = self.email_parser.parse(content)

        self.assertEqual('Spam', parsed_email.category)
        self.assertEqual(False, parsed_email.ack)
        self.assertEqual(False, parsed_email.trusted)
        self.assertEqual([], parsed_email.attachments)
        self.assertEqual(1, len(parsed_email.ips))
        self.assertIn('213.251.151.160', parsed_email.ips)
        self.assertEqual(None, parsed_email.urls)
        self.assertEqual(None, parsed_email.fqdn)

    def test_get_headers_sample3(self):

        sample = self.samples['sample3']
        headers = self.email_parser.get_headers(sample.read())
        self.assertIn('Date', headers)
        self.assertIn('From', headers)
        self.assertIn('Subject', headers)

    def test_get_sender_sample3(self):

        sample = self.samples['sample3']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        self.assertEqual('newsletter@ipm.dhnet.be', sender)

    def test_get_recipients_sample3(self):

        sample = self.samples['sample3']
        headers = self.email_parser.get_headers(sample.read())
        recipients = parser.get_recipients_from_headers(headers)
        self.assertIn('abuse@ovh.net', recipients)

    def test_get_date_sample3(self):

        sample = self.samples['sample3']
        headers = self.email_parser.get_headers(sample.read())
        date = parser.get_date_from_headers(headers)
        self.assertEqual(1430342845, int(date))

    def test_get_template_sample3(self):

        sample = self.samples['sample3']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        template = self.email_parser.get_template(sender)
        self.assertEqual(None, template)

    def test_get_parsed_email_sample3(self):

        sample = self.samples['sample3']
        content = sample.read()
        parsed_email = self.email_parser.parse(content)

        self.assertEqual('Copyright', parsed_email.category)
        self.assertEqual(False, parsed_email.ack)
        self.assertEqual([], parsed_email.attachments)
        self.assertEqual(None, parsed_email.ips)
        self.assertIn('http://re.ldh.be/image/1e/55755fc935709a87ac80251e.jpg', parsed_email.urls)
        self.assertEqual(None, parsed_email.fqdn)
        self.assertTrue(parsed_email.trusted)

    def test_get_headers_sample4(self):

        sample = self.samples['sample4']
        headers = self.email_parser.get_headers(sample.read())
        self.assertIn('Date', headers)
        self.assertIn('From', headers)
        self.assertIn('Subject', headers)

    def test_get_sender_sample4(self):

        sample = self.samples['sample4']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        self.assertEqual('cpro@cpro.pt', sender)

    def test_get_recipients_sample4(self):

        sample = self.samples['sample4']
        headers = self.email_parser.get_headers(sample.read())
        recipients = parser.get_recipients_from_headers(headers)
        self.assertIn('abuse@ovh.net', recipients)
        self.assertIn('cpro@cpro.pt', recipients)

    def test_get_date_sample4(self):

        sample = self.samples['sample4']
        headers = self.email_parser.get_headers(sample.read())
        date = parser.get_date_from_headers(headers)
        self.assertEqual(1433343560, int(date))

    def test_get_template_sample4(self):

        sample = self.samples['sample4']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        template = self.email_parser.get_template(sender)
        self.assertEqual(None, template)

    def test_get_parsed_email_sample4(self):

        sample = self.samples['sample4']
        content = sample.read()
        parsed_email = self.email_parser.parse(content)

        self.assertEqual('Copyright', parsed_email.category)
        self.assertEqual(False, parsed_email.ack)
        self.assertNotIn(u'é"', parsed_email.body)
        self.assertEqual(2, len(parsed_email.attachments))
        self.assertIn('data', parsed_email.attachments[0])
        self.assertEqual(None, parsed_email.ips)
        self.assertIn('http://schemas.microsoft.com/office/2004/12/omml', parsed_email.urls)
        self.assertEqual(3, len(parsed_email.urls))
        self.assertEqual(None, parsed_email.fqdn)

    def test_get_headers_sample5(self):

        sample = self.samples['sample5']
        headers = self.email_parser.get_headers(sample.read())
        self.assertIn('Date', headers)
        self.assertIn('From', headers)
        self.assertIn('Subject', headers)

    def test_get_sender_sample5(self):

        sample = self.samples['sample5']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        self.assertEqual('antipiracy-node320@degban.com', sender)

    def test_get_recipients_sample5(self):

        sample = self.samples['sample5']
        headers = self.email_parser.get_headers(sample.read())
        recipients = parser.get_recipients_from_headers(headers)
        self.assertIn('abuse@ovh.net', recipients)
        self.assertIn('dmca@brazzers.com', recipients)

    def test_get_date_sample5(self):

        sample = self.samples['sample5']
        headers = self.email_parser.get_headers(sample.read())
        date = parser.get_date_from_headers(headers)
        self.assertEqual(1433756506, int(date))

    def test_get_template_sample5(self):

        sample = self.samples['sample5']
        headers = self.email_parser.get_headers(sample.read())
        sender = parser.get_sender_from_headers(headers)
        template = self.email_parser.get_template(sender)
        self.assertTrue(1, len(template))

    def test_get_parsed_email_sample5(self):

        sample = self.samples['sample5']
        content = sample.read()
        parsed_email = self.email_parser.parse(content)

        self.assertEqual('Copyright', parsed_email.category)
        self.assertEqual(False, parsed_email.ack)
        self.assertEqual(0, len(parsed_email.attachments))
        self.assertEqual(None, parsed_email.ips)
        self.assertIn('http://www.example.com/share/file/AAAAAAAAAAAAAAAAAAAAAAAAAA/', parsed_email.urls)
        self.assertEqual(2, len(parsed_email.urls))
        self.assertEqual(None, parsed_email.fqdn)

    def test_get_template(self):

        sample = self.samples['sample8']
        content = sample.read()
        parsed_email = self.email_parser.parse(content)

        template = self.email_parser.get_template(parsed_email.provider)
        self.assertEqual(r'(?:Problem\s*:\s*)(.*)', template['category']['pattern'])
