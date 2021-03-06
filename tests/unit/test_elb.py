# This file is part of Certifier.
# Copyright 2015, Behance Ops.

"""Tests for the the EC2 service class"""

import os
import sys
import time
import ConfigParser
from tests.unit import CertifierTestCase
import sure
import mock
from mock import patch
from mock import Mock
from nose.plugins.attrib import attr

import boto.ec2.elb as elb


from moto import mock_elb

from certifier.elb import *
from certifier.certificate import get_expiry

class ElbTestCase(CertifierTestCase):

    creds = {
        'aws_access_key_id': '',
        'aws_secret_access_key': ''
    }

    def setUp(self):
        super(ElbTestCase, self).setUp()

    @attr(elb=True)
    @mock_elb
    def test_get_empty_elbs(self):

        elbs = get_elbs(self.creds)
        elbs.should.be.empty

        elbs = get_elbs(self.creds, region='us-west-2')
        elbs.should.be.empty

    @attr(elb=True)
    @mock_elb
    def test_get_elbs(self):

        for x in range(0,50):
            self.create_elb()

        elbs = get_elbs(self.creds)
        len(elbs).should.equal(50)

    @attr(elb=True)
    @mock_elb
    @patch('certifier.elb.get_expiry')
    def test_certify_elbs(self, mock_get_expiry):

        mock_get_expiry.return_value = '2018-01-29 23:59:59'

        self.create_elb()
        self.create_elb(scheme='internal')
        self.create_elb(scheme='poopy-scheme', include_https=False)

        certify_elbs(self.creds)

    def create_elb(self, scheme='internet-facing', include_https=True):

        name = self.random_name()

        conn = elb.connect_to_region('us-east-1')

        zones = ['us-east-1a', 'us-east-1b']
        ports = [(80, 80, 'http')]
        if include_https:
            ports.append((443, 80, 'https', 'arn:aws:iam::1234567890123:server-certificate/my.nifty.cert.net'))

        lb = conn.create_load_balancer(name, zones, ports, scheme=scheme)

