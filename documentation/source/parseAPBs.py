#
# Copyright 2020 United States Government
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

import os
import sys
from xml.dom import minidom
from xml.parsers.expat import ExpatError

class apb(object):
    def __init__(self):
        self.name = 'none'
        self.desc = ''
        self.uuid = ''
        self.apbfile = ''
        self.inpType = ''
        self.outType = ''
        self.ordered = ''
        self.asps_data = { "data":[]}
        self.meas_spec = { "data":[]}
        self.env_var = { "data":[]}
        self.selinux_type = ''
        self.user = ''

def printHeader( ):
    "This Function Prints SPHINX Header to Standard Output"
    print ('=====================================')
    print ('Attestation Protocol Blocks (APBs)')
    print ('=====================================\n')
    print ('APBs are responsible for understanding the requirements of' + 
            ' a particular attestation scenario as defined by the Measurement' + 
            ' Specification, selecting an appropriate sequence of ASPs to' + 
            ' execute to satisfy the scenario, and collecting the results' + 
            ' generated by individual ASPs into a cohesive whole that' + 
            ' is consumable by the remote party.\n')

#    print ('.. figure:: images/attester-appraiser.pdf');
#    print ('.. figure:: images/attesterselectionprocess.jpg');
#    print ('   :align:  center\n');
#    print ('   Attester Appraisar Image');
#    print('\n');
    return

def printAPBInfo(apb):
    "Print XML Info"
    print ('.. _' + apb.uuid + ':\n\n' + apb.name)
    print ('--------------------------------------\n')
    print('| Filename: ' +  apb.apbfile)
    print('| UUID: ' +  apb.uuid)
#    print('| Input Type: ' + apb.inpType)
#    print('| Output Type: ' + apb.outType)
    print('| Description: \n| \t' + apb.desc)
    
    if (len(apb.asps_data["data"]) > 0):
        print('| ASPs: (Ordered = ' + apb.ordered + ')')
        for values in iter(apb.asps_data.values()):
            for value in values:
                print("|\t:ref:`" + value["name"] + " <" + value["uuid"] + ">`")
    
    if (len(apb.meas_spec["data"]) > 0):
        print('| Measurement Specifications:')
        for values in iter(apb.meas_spec.values()):
            for value in values:
                print("|\t:ref:`" + value["name"] + " <" + value["uuid"] + ">`")
    
    if (len(apb.env_var["data"]) > 0):
        print('| Environment Variables (Default Value)')    
        for values in iter(apb.env_var.values()):
            for value in values:
                print("|\t" + value["name"] + " (" + value["val"] + ")")

    print("| Security: ")
    print('| \tType: ' + apb.selinux_type)
    print('| \tUser: ' + apb.user)

    print('')
    return

def parseAPBXml( string ):
    "Parse ASP XML"
    doc = parseXml(string);
    if (doc is not None):
        parsedapb = parseAPBFields(doc)
        return parsedapb

    return None

def parseXml( path ): 
    "minidom xml parsing"

    try: 
        doc = minidom.parse(path)
        return doc
    except IOError as e:
        print("I/O error ({0}): {1}".format(e.errno, e.strerror))
        return None
    except ExpatError as expatError:
        print("Minidom Parse Error: " + str(expatError) + " when parsing " + path)        
        return None
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return None

def parseAPBFields(doc):
    "Parse APB Fields from minidom object"
    try: 
        parsedapb = apb()
        field = doc.getElementsByTagName("name")[0]
        parsedapb.name = field.firstChild.data
    except:
        print ("Could Not Parse APB Name (Unexpected Error: " + sys.exc_info()[0] + ")")
        return None

    try:
        field = doc.getElementsByTagName("uuid")[0]
        parsedapb.uuid = field.firstChild.data
        field = doc.getElementsByTagName("input_type")[0]
        parsedapb.inpType = field.firstChild.data
        field = doc.getElementsByTagName("output_type")[0]
        parsedapb.outType = field.firstChild.data
        field = doc.getElementsByTagName("desc")[0]
        parsedapb.desc = field.firstChild.data
        field = doc.getElementsByTagName("file")[0]
        parsedapb.apbfile = field.firstChild.data
        asps = doc.getElementsByTagName("asps")
        for asp in asps:
            if asp.hasAttribute("ordered"):
                parsedapb.ordered = asp.getAttribute("ordered")

        asps = doc.getElementsByTagName("asp")
        for asp in asps:
            entry = {}
            entry["name"] = asp.firstChild.data
            entry["uuid"] = asp.getAttribute("uuid")
            parsedapb.asps_data["data"].append(entry)

        meas = doc.getElementsByTagName("measurement_specification")
        for spec in meas:
            entry = {}
            entry["name"] = spec.firstChild.data
            entry["uuid"] = spec.getAttribute("uuid")
            parsedapb.meas_spec["data"].append(entry)

        envs = doc.getElementsByTagName("environment_variable")
        for env in envs:
            entry = {}
            entry["name"] = env.getAttribute("name")
            entry["val"]  = env.getAttribute("val")
            parsedapb.env_var["data"].append(entry)

        securitys = doc.getElementsByTagName("security_context")
        for security in securitys:
            selinux = security.getElementsByTagName("selinux")
            if (selinux.length > 0):
                selinux = security.getElementsByTagName("selinux")[0]
                field = selinux.getElementsByTagName("type")[0]
                parsedapb.selinux_type = field.firstChild.data
            user = security.getElementsByTagName("user")
            if (user.length > 0):
                field = security.getElementsByTagName("user")[0]
                parsedapb.user = field.firstChild.data

    except:
        print("Parsing APB: " + parsedapb.name)
        print("Unexpected Error: ", sys.exc_info()[0])
        return None
 
    return parsedapb

# Print SPHYNX Header
printHeader()

# Variables
APBsLocation = sys.argv[1]
Apbs = []

# Parse and Organize ASPs
for root, directories, files in os.walk(APBsLocation):
    for filename in sorted(files):
        if filename.endswith(".xml"):
            parsedapb = parseAPBXml(APBsLocation + filename);
            if parsedapb is not None: 
                Apbs.append(parsedapb)
    break; # only top folder, break before recursively checking test folders

# Print APBs
for apb_object in Apbs:
    printAPBInfo(apb_object)
