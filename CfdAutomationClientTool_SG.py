# Imports
import os
import shutil
import fileinput
import subprocess
import filecmp
import sys
import re
import subprocess
import time
import tkinter as tk
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import webbrowser
import difflib
import glob
from difflib import ndiff
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from xml.dom import minidom
from zipfile import ZipFile
from xml.dom.minidom import Node
import socket
import zipfile

# Global Declaration
RootLibraryFolderPath=""
CfdExePath = ""
HOST = ""
PORT = 9999
dialog_window = None
# XML for settings
MainMode=ET.Element("Settings")
MainPath=ET.SubElement(MainMode,"Paths")

#socket opening
szSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
szSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

szSocket.bind((HOST, PORT))
szSocket.settimeout(None)
szSocket.listen(5)



#main frame
szTkExecution=Tk()
szTkExecution.geometry("550x170+300+200")
szTkExecution.title("CFD Automation Tool")
szMainFrame = Frame()
szMainFrame.grid()
# Function to select CFD exe path


# Function to select Root folder path
def SelectMainPath():
    global RootLibraryFolderPath
    RootLibraryFolderPath=filedialog.askdirectory()
    if len(RootLibraryFolderPath) == 0:
        RootLibraryFolderPath = os.getcwd()
        return
    txtEntryRootFolderPath.insert(0,RootLibraryFolderPath)
    txtEntryRootFolderPath.config(state=DISABLED)

def SelectCfdExePath():
    global CfdExePath
    CfdExePath=filedialog.askopenfilename(title="SelectCFDSolverPath",filetypes = (("python files","*.exe"),("all files","*.*")))
    if len(CfdExePath)==0:
        messagebox.showerror("Error","You have to select the CFD solver path")
    else:
        txtEntryCfdExePath.insert(0,CfdExePath)
        txtEntryCfdExePath.config(state=DISABLED)
def EnterPortNumber():
    global szPortNumber
    szPortNumber=txtPortNumber.get()
    if len(szPortNumber)==0:
        szPortNumber=9999
        messagebox.showinfo("Info","Default value '9999' is the port number")
        return
    else:
        szPortNumber=szPortNumber
def CloseSettingsWindow():
    global RootLibraryFolderPath
    szSelectCurrentDir=os.getcwd()
    ET.SubElement(MainPath, "RootLibraryFolderPath").text = RootLibraryFolderPath
    ET.SubElement(MainPath, "CfdExePath").text =CfdExePath
    tree = ET.ElementTree(MainMode)
    tree.write(szSelectCurrentDir+"\\"+"SettingsClientConfigure.xml")
    dialog_window.destroy()

def CreateSettingsdialog():
    global dialog_window
    global CfdExePath
    global txtEntryRootFolderPath
    global txtEntryCfdExePath
    dialog_window = Toplevel()
    dialog_window.geometry("330x180+400+300")
    dialog_window.grab_set()
    dialog_window.title("Settings")
    # Label to display Select path folder
    lblSelectMainStoragePath = Label(dialog_window, text="Select a path for Storage:")
    lblSelectMainStoragePath.grid(row=0, column=0, sticky=W)
    # Button to browse Root folder path
    btnBrowseMainPath = Button(dialog_window, text='Browse...', bg="Light Blue", command=SelectMainPath, width=7,
                               height=1)
    btnBrowseMainPath.grid(row=1, column=1, padx=10)
    # Text entry to display selected root folder path
    txtEntryRootFolderPath = Entry(dialog_window,width=40, bg="azure")
    txtEntryRootFolderPath.grid(row=1, column=0, sticky=W, padx=5, ipady=4)
    # Label to display Select CFD exe
    # Label to display Select path
    lblSelectCfdExePath = Label(dialog_window, text="Select a path for CFD.exe:")
    lblSelectCfdExePath.grid(row=2, column=0, sticky=W)
    # Button to browse CFD exe path
    btnBrowseCfdExePath = Button(dialog_window, text='Browse...', bg="Light Blue", command=SelectCfdExePath, width=7,height=1)
    btnBrowseCfdExePath.grid(row=3, column=1, padx=10)
    # Text entry to display selected CFD exe path
    txtEntryCfdExePath = Entry(dialog_window,width=40, bg="azure")
    txtEntryCfdExePath.grid(row=3, column=0, sticky=W, padx=5, ipady=4)
    # Label for port number
    lblSelectPortNumber=Label(dialog_window,text="Port number:")
    lblSelectPortNumber.grid(row=4,column=0,sticky=W)
    # Text entry take port number
    txtPortNumber = Entry(dialog_window,width=40,bg="azure")
    txtPortNumber.grid(row=5,column=0,sticky=W,padx=5,ipady=4)
    # Button to Select the port number
    btnPortNumber = Button(dialog_window, text='Click',bg="Light Blue",command=EnterPortNumber,width=7, height=1)
    btnPortNumber.grid(row=5,column=1,padx=10)
    # Button ok
    btnOk = Button(dialog_window, text='Ok', bg="Light Blue", width=7, height=1, command=CloseSettingsWindow)
    btnOk.grid(row=6, column=0, pady=5)



    dialog_window.lift()
#function for setting dialog
def ShowSettingsdialog():
    if dialog_window is None:
        CreateSettingsdialog()
        return
    try:
        dialog_window.lift()
    except TclError:
        CreateSettingsdialog()

def GetAllPath(directory):
    file_paths=[]
    for root,directories,files in os.walk(directory):
        for filename in files:
            filepath=os.path.join(root,filename)
            file_paths.append(filepath)
    return file_paths
#unZipping files
def unzipp():
    global CfdExePath
    szStatusbarRunTestcase['text']="Client Listening ..."
    while True:
        conn, addr = szSocket.accept()
        str1 = conn.recv(2048)
        szFinalMsg=str1.decode('utf8')
        if szFinalMsg == "disconnect":
            conn.close()
            szSocket.close()
            sys.exit(0)
        else:
            szStatusbarRunTestcase['text']="Client connected: "
            szReceivedTestCaseName=str1.decode('utf8')
            # Creating a directory testcase
            szReceivedTestCaseNamePath=os.path.join(RootLibraryFolderPath,szReceivedTestCaseName)
            if os.path.exists(szReceivedTestCaseNamePath):
                shutil.rmtree(szReceivedTestCaseNamePath)
            os.makedirs(szReceivedTestCaseNamePath)
            szTempResultFolder=os.path.join(szReceivedTestCaseNamePath,"TempResult")
            os.makedirs(szTempResultFolder)

            # Creating a zip to recive the content
            szReceivedZipFile = open(szReceivedTestCaseNamePath+"Temp.zip", "wb")
            while True:
                # get file bytes
                szReceivingServerdata = conn.recv(4096)
                if not szReceivingServerdata:
                    break
                # write bytes on file
                szReceivedZipFile.write(szReceivingServerdata)
            szReceivedZipFile.close()
            # Extracting the recived zipfile
            szExctractingZipFiles = zipfile.ZipFile(szReceivedTestCaseNamePath+"Temp.zip")
            szExctractingZipFiles.extractall(szReceivedTestCaseNamePath)
            szStatusbarRunTestcase['text']="Download complete! and unzip is done"
            #Reading from xml
            szReadXml = minidom.parse(szReceivedTestCaseNamePath + "\\" + "allpaths.xml")
            szListForHoldingResultFiles = []
            # Getting the element of the XML tree
            szXmlModelFolder = szReadXml.getElementsByTagName('ModelFolder')
            szXmlPythonFile = szReadXml.getElementsByTagName('PythonFilePath')
            # Getting the content of the XML tree
            szModelFolder = (szXmlModelFolder[0].firstChild.data)
            szPythonFile = (szXmlPythonFile[0].childNodes[0].data)
            # Taking the nae of the Model folder and python script
            szModelFolderBaseName=os.path.basename(szModelFolder)
            szPythonScriptBaseName=os.path.basename(szPythonFile)
            #Path of the python script
            szSelectingModelFolderPath=os.path.join(szReceivedTestCaseNamePath,szModelFolderBaseName)
            szSelectingPythonFilePath=os.path.join(szSelectingModelFolderPath,szPythonScriptBaseName)

            szStatusbarRunTestcase['text']="CFD Running In the background"
            #subprocess.call([CfdExePath, '-script', szSelectingPythonFilePath])
            szStatusbarRunTestcase['text']="CFD Finished execution"
    

            for elem in szReadXml.getElementsByTagName('ResultNode'):
                for x in elem.childNodes:
                    if x.nodeType == Node.ELEMENT_NODE:
                        szListForHoldingResultFiles.append(x.childNodes[0].data)

            for i in range(0,len(szListForHoldingResultFiles)):
                szResultFileBasename=os.path.basename(szListForHoldingResultFiles[i])
                szAllResultFilePath=os.path.join(szSelectingModelFolderPath,szResultFileBasename)
                szChekingExistence=os.path.exists(szAllResultFilePath)
                if szChekingExistence == True:
                    shutil.copy2(szAllResultFilePath,szTempResultFolder)
                else:
                    print("not exist")
                    
            szZipFilePath=GetAllPath(szTempResultFolder)
            with ZipFile('SendingZipFileBackToServer.zip','w') as zip:
                for file in szZipFilePath:
                    zip.write(file,file.replace(szTempResultFolder,""))
        
            szSendingBackToServer='SendingZipFileBackToServer.zip'
            with open(szSendingBackToServer,'rb') as f:
                szZipdata=f.read()
                conn.sendall(szZipdata)
            
        conn.close()


#label frames
lblAppname = Label(szMainFrame,font=('arial',30, 'bold'),text="CFD AUTOMATION TOOL",fg="Steel Blue")
lblAppname.grid(row=0,column=0)
# Setting button creation
btnSettings = Button(szMainFrame,bg="Light Blue",height=1,width=5,text="setting",command=ShowSettingsdialog)
btnSettings.grid(row=0,column=1)
# Run Client Button
btnSettings = Button(szMainFrame,bg="Light Blue",height=1,width=9,text="Run Client",command=unzipp)
btnSettings.grid(row=1,column=0,columnspan=3)
# Status bar
szStatusbarRunTestcase= Label(szMainFrame,bd=1,text="Status Bar",anchor=W)
szStatusbarRunTestcase.grid(sticky=W+S+E+N,pady=70)
szSelectCurrentDir=os.getcwd()
szConfigureXmlLocation=os.path.join(szSelectCurrentDir,"SettingsClientConfigure.xml")
szCheckExist=os.path.exists(szConfigureXmlLocation)
if szCheckExist == True:
    szReadXml=minidom.parse(szSelectCurrentDir+"\\"+"SettingsClientConfigure.xml")
    szXmlRootLibraryFolderPath=szReadXml.getElementsByTagName('RootLibraryFolderPath')
    szXmlCfdExePath=szReadXml.getElementsByTagName('CfdExePath')
    
    szReadXmlRootLibraryFolderPath=(szXmlRootLibraryFolderPath[0].firstChild.data)
    szReadXmlszXmlCfdExePath=(szXmlCfdExePath[0].childNodes[0].data)
    RootLibraryFolderPath=szReadXmlRootLibraryFolderPath
    CfdExePath=szReadXmlszXmlCfdExePath
else:
    messagebox.showerror("Error","Please select the CFD solver path and\nRoot Directory path")
    ShowSettingsdialog()

szTkExecution.mainloop()



