#!/usr/bin/env python
#
# Copyright 2016 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Delete all config data for model Cisco-IOS-XR-telemetry-model-driven-cfg.
usage: nc-delete-ncs1002-telemetry-native-all-ydk.py [-h] [-v] \
                                            device1 device2 .. deviceN
positional arguments:
  devices        NETCONF devices (ssh://user:password@host:port)
optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  print debugging messages
"""

from argparse import ArgumentParser
from urlparse import urlparse

from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_telemetry_model_driven_cfg \
    as xr_telemetry_model_driven_cfg
import logging


if __name__ == "__main__":
    """Execute main program."""
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', help='print debugging messages',
                        action='store_true')
    parser.add_argument('devices', nargs='+',
                        help='NETCONF devices (ssh://user:password@host:port)')
    args = parser.parse_args()

    # log debug messages if verbose argument specified
    if args.verbose:
        logger = logging.getLogger('ydk')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(('%(asctime)s - %(name)s - '
                                      '%(levelname)s - %(message)s'))
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # create CRUD service
    crud = CRUDService()
    # create object
    telemetry_model_driven = xr_telemetry_model_driven_cfg.TelemetryModelDriven()  

    arg_list = args.devices
    for i in arg_list:
        device = urlparse(i)
        # create NETCONF provider
        provider = NetconfServiceProvider(address=device.hostname,
                                          port=device.port,
                                          username=device.username,
                                          password=device.password,
                                          protocol=device.scheme)
        # delete configuration on NETCONF device
        crud.delete(provider, telemetry_model_driven)
        provider.close()
    exit()
# End of script
