# -*- coding: utf-8 -*-
import re
import os
import lxml.etree as ET
# Global Variables
CurrentDir = os.getcwd()

def ReadHeaders():
    VersionNumber =""
    with open(CurrentDir + r'\Build_Increment.h','r') as varReadFileObj:
        for line in varReadFileObj:
            authorise = bool('#define BUILD' in line)
            if authorise is True:
                varVersion=line.split(" ")[-1].rstrip()
                VersionNumber += "."+varVersion
        ReadWriteXml(VersionNumber)

def ReadWriteXml(VersionNumber):
    xmlReader = ET.parse(CurrentDir + r'\ThirdParties_Neutron.xml')
    myroot = xmlReader.getroot()
    for rootElement in myroot.findall('ThirdParty'):
        if(rootElement.get('Id')=="NASTRANSolver"):
            for innerElement in rootElement.iter('Platform'):
                innerElement.set('Version',VersionNumber.lstrip('.'))
    xmlReader = ET.tostring(xmlReader,encoding="unicode", method="html")# Undo the unicode done by Parser
    with open (CurrentDir + r'\ThirdParties_Neutron.xml','w') as filewrite:
        filewrite.write(xmlReader)

def main():
    ReadHeaders()

if __name__ == "__main__":
    main()  