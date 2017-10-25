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
Create configuration for Telemetry gRPC Dial-out mode using
Cisco-IOS-XR-telemetry-model-driven-cfg model.
usage: nc-create-ncs1002-telemetry-native-grpc-out-ydk.py [-h] [-v] \
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
from ydk.types import Empty
import logging

## inventory (chassis SN)
PATH1 = ('Cisco-IOS-XR-plat-chas-invmgr-oper:'
         'platform-inventory/racks/rack/'
         'attributes/basic-info')

## system alarms-active
PATH10 = ('Cisco-IOS-XR-alarmgr-server-oper:alarms/'
         'brief/brief-card/brief-locations/brief-location/active')

## inventory (pluggables SN/FW)
PATH2 = ('Cisco-IOS-XR-plat-chas-invmgr-oper:'
         'platform-inventory/racks/rack/slots/'
         'slot/cards/card/port-slots/port-slot/'
         'portses/ports/hw-components/'
         'hw-component/attributes/basic-info')

## system memory summary
PATH11 = ('Cisco-IOS-XR-nto-misc-oper:memory-summary/nodes/node'
          '/summary')

## CPU utilization detail
PATH12 = ('Cisco-IOS-XR-wdsysmon-fd-oper:'
          'system-monitoring/cpu-utilization')

## controllers coherentDSP X/X/X/X pm current 30-sec fec
PATH20 = ('Cisco-IOS-XR-pmengine-oper:performance-management/'
         'otu/otu-ports/otu-port/otu-current/otu-second30'
         '/otu-second30fecs/otu-second30fec')

## controllers coherentDSP X/X/X/X pm current 30-sec otn
PATH21 = ('Cisco-IOS-XR-pmengine-oper:performance-management/'
         'otu/otu-ports/otu-port/otu-current/otu-second30'
         '/otu-second30otns/otu-second30otn')

## controllers hundredGigECtrlr X/X/X/X pm current 30-sec ether
PATH22 = ('Cisco-IOS-XR-pmengine-oper:performance-management/'
         'ethernet/ethernet-ports/ethernet-port/ethernet-current/'
         'ethernet-second30/second30-ethers/second30-ether')

## controllers optics X/X/X/X pm current 30-sec optics
PATH23 = ('Cisco-IOS-XR-pmengine-oper:performance-management/'
         'optics/optics-ports/optics-port/optics-current/'
         'optics-second30/optics-second30-optics'
         '/optics-second30-optic')

## show controllers optics * summary
PATH24 = ('Cisco-IOS-XR-controller-optics-oper'
         '-sub1:optics-oper/optics-ports/'
         'optics-port/optics-info')

PATH_LONG = [PATH1, PATH2]
PATH_MED = [PATH10, PATH11, PATH12]
PATH_SHORT = [PATH20, PATH21, PATH22, PATH23, PATH24]

SGROUP1_ID, SGROUP2_ID, SGROUP3_ID = 'SGROUP1', 'SGROUP2', 'SGROUP3'
SGROUP1_INT, SGROUP2_INT, SGROUP3_INT = 1800000, 20000, 10000
SUBS1_ID, SUBS2_ID, SUBS3_ID = "Sub1", "Sub2", "Sub3"
DGROUP_ID = 'DGROUP1'
SERVER_1 = '10.30.110.38'
S1_PORT = 57500
SERVER_2 = '1.1.1.1'  # use None if there is no second server
S2_PORT = 57500

def config_telemetry_model_driven(telemetry_model_driven):

    """
    Add config data to telemetry_model_driven object.
    The goal is to configure Destinaton Group == Destination Collector
    Sensor group is the place for sensor paths, where you define metrics
    to push from NCS1002
    Subscription is the place where you connect paths with destinatons
    and define how often stream information from the defined paths
    """
    
    ## destination group for the servers, put your details here
    for i in [[S1_PORT, SERVER_1],
          [S2_PORT, SERVER_2]]:
        
        if i[1] is not None:
            destination_group = telemetry_model_driven.destination_groups.\
                                DestinationGroup()
            ## the name of this destination group
            destination_group.destination_id = DGROUP_ID
            ipv4_destination = destination_group.ipv4_destinations.\
                               Ipv4Destination()
            ## address and port of the server configuration
            ipv4_destination.destination_port = i[0]
            ipv4_destination.ipv4_address = i[1]
            ipv4_destination.encoding = xr_telemetry_model_driven_cfg.\
                                        EncodeTypeEnum.self_describing_gpb
            protocol = ipv4_destination.Protocol()
            ## define the transport protocol
            protocol.protocol = xr_telemetry_model_driven_cfg.ProtoTypeEnum.grpc
            protocol.no_tls = 1
            ipv4_destination.protocol = protocol
            destination_group.ipv4_destinations.ipv4_destination.\
                                                append(ipv4_destination)
            telemetry_model_driven.destination_groups.\
                                   destination_group.append(destination_group)
        else:
            pass
    
    ## sgroup1/2/3 configuration for 30-min/20sec/10sec
    ## interval paths [you can use your timers]
    for i in [[SGROUP1_ID, PATH_LONG],
          [SGROUP2_ID, PATH_MED],
          [SGROUP3_ID, PATH_SHORT]]:
        
        sensor_group = telemetry_model_driven.sensor_groups.SensorGroup()
        sensor_group.sensor_group_identifier = i[0]
        sensor_group.enable = Empty()        
        for PATH in i[1]:
            sensor_path = sensor_group.sensor_paths.SensorPath()
            sensor_path.telemetry_sensor_path = PATH
            sensor_group.sensor_paths.sensor_path.append(sensor_path)   
        ## all paths above are added into sensor groups:
        telemetry_model_driven.sensor_groups.sensor_group.append(sensor_group)

    ## subscription configuration
    for i in [[SUBS1_ID, SGROUP1_ID, SGROUP1_INT],
              [SUBS2_ID, SGROUP2_ID, SGROUP2_INT],
              [SUBS3_ID, SGROUP3_ID, SGROUP3_INT]]: 
        ## subscription configuration
        subscription = telemetry_model_driven.subscriptions.Subscription()
        ## name of the subscription group
        subscription.subscription_identifier = i[0]
        sensor_profile = subscription.sensor_profiles.SensorProfile()
        ## attach the sensor-group
        sensor_profile.sensorgroupid = i[1]
        ## define the interval
        sensor_profile.sample_interval = i[2]
        subscription.sensor_profiles.sensor_profile.append(sensor_profile) 
        sensor_profile = subscription.sensor_profiles.SensorProfile()
        ## define destination group to be used
        destination_profile = subscription.destination_profiles.DestinationProfile()
        destination_profile.destination_id = DGROUP_ID
        destination_profile.enable = Empty()
        subscription.destination_profiles.destination_profile.append(destination_profile) 
        telemetry_model_driven.subscriptions.subscription.append(subscription)
        

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
    # add object configuration
    config_telemetry_model_driven(telemetry_model_driven) 

    arg_list = args.devices
    for i in arg_list:
        device = urlparse(i)
        # create NETCONF provider
        provider = NetconfServiceProvider(address=device.hostname,
                                           port=device.port,
                                           username=device.username,
                                           password=device.password,
                                           protocol=device.scheme)
        # create configuration on NETCONF device
        crud.create(provider, telemetry_model_driven)
        provider.close()

    exit()
    
# End of script

#### sh run for the model ####

##telemetry model-driven
## destination-group DGROUP1
##  address-family ipv4 1.1.1.1 port 57500
##   encoding self-describing-gpb
##   protocol grpc no-tls
##  !
##  address-family ipv4 10.30.110.38 port 57500
##   encoding self-describing-gpb
##   protocol grpc no-tls
##  !
## !
## sensor-group SGROUP1
##  sensor-path Cisco-IOS-XR-plat-chas-invmgr-oper:platform-inventory/racks/rack/attributes/basic-info
## !
## sensor-group SGROUP2
##  sensor-path Cisco-IOS-XR-wdsysmon-fd-oper:system-monitoring/cpu-utilization
##  sensor-path Cisco-IOS-XR-nto-misc-oper:memory-summary/nodes/node/summary
##  sensor-path Cisco-IOS-XR-alarmgr-server-oper:alarms/brief/brief-card/brief-locations/brief-location/active
## !
## sensor-group SGROUP3
##  sensor-path Cisco-IOS-XR-controller-optics-oper-sub1:optics-oper/optics-ports/optics-port/optics-info
##  sensor-path Cisco-IOS-XR-pmengine-oper:performance-management/otu/otu-ports/otu-port/otu-current/otu-second30/otu-second30fecs/otu-second30fec
##  sensor-path Cisco-IOS-XR-pmengine-oper:performance-management/otu/otu-ports/otu-port/otu-current/otu-second30/otu-second30otns/otu-second30otn
##  sensor-path Cisco-IOS-XR-pmengine-oper:performance-management/ethernet/ethernet-ports/ethernet-port/ethernet-current/ethernet-second30/second30-ethers/second30-ether
##  sensor-path Cisco-IOS-XR-pmengine-oper:performance-management/optics/optics-ports/optics-port/optics-current/optics-second30/optics-second30-optics/optics-second30-optic
## !
## subscription Sub1
##  sensor-group-id SGROUP1 sample-interval 1800000
##  destination-id DGROUP1
## !
## subscription Sub2
##  sensor-group-id SGROUP2 sample-interval 20000
##  destination-id DGROUP1
## !
## subscription Sub3
##  sensor-group-id SGROUP3 sample-interval 10000
##  destination-id DGROUP1
## !
##!

