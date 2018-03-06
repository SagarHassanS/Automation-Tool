# Imports
import os
import shutil
import fileinput
import subprocess
import filecmp
import sys
import re
import subprocess
import subprocess, platform
import time
import tkinter as tk
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import webbrowser
import difflib
import socket
import zipfile
import socket,os
import threading
from zipfile import ZipFile
from difflib import ndiff
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from xml.dom import minidom
from xml.dom.minidom import Node
from tkinter.ttk import Separator, Style

# Global Declaration
szTkExecution=Tk()
szTkExecution.geometry("550x300+60+60")
szTkExecution.title("CFD Automation Tool")
dialog_window = None
szDialogEindowForRunTestcase = None
szTempFolder= ""
iPortNumber=9999
txtPortNumber= ""
szIpAddress= ""
txtEntryCfdExePath= ""
szEnteredTestCaseName= ""
szTargetFolderPath = ""
RootLibraryFolderPath = ""
szCopiedModelFolder= ""
CfdExePath = ""
szBaseLineFolder = ""
szModelFolder = ""
szPythonFilePath= ""
txtEntryRootFolderPath= ""
lstBoxListAllClients= ""
Settingsicon=PhotoImage(file="Settings.png")
# XML elements declaration
ParentNode = ET.Element("ParentNode")
ChildNode = ET.SubElement(ParentNode, "ChildNode")
ResultNode= ET.SubElement(ChildNode, "ResultNode")
# XML for settings
MainMode=ET.Element("Settings")
MainPath=ET.SubElement(MainMode,"Paths")
# Creating the Frame for CFD automation tool application
szMainFrame = Frame()
szMainFrame.grid()

# Class for displaying the Tooltip
class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background='light goldenrod yellow', relief='solid', borderwidth=1,
                       font=("times", "12", "normal"))
        label.pack(ipadx=1)
    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

# Function to select Root folder path
def SelectMainPath():
    global RootLibraryFolderPath
    RootLibraryFolderPath=filedialog.askdirectory(title="Select Root Folder Path")
    if len(RootLibraryFolderPath) == 0:
        RootLibraryFolderPath = os.getcwd()
    txtEntryRootFolderPath.insert(0,RootLibraryFolderPath)
    txtEntryRootFolderPath.config(state=DISABLED)
# Function to select CFD exe path
def SelectCfdExePath():
    global CfdExePath
    CfdExePath=filedialog.askopenfilename(title="SelectCFDSolverPath",filetypes = (("python files","*.exe"),("all files","*.*")))
    if len(CfdExePath)==0:
        messagebox.showerror("Error","You have to select the CFD solver path")
    else:
        txtEntryCfdExePath.insert(0,CfdExePath)
        txtEntryCfdExePath.config(state=DISABLED)
def EnterPortNumber():
    global iPortNumber
    szPortNumber=txtPortNumber.get()
    iPortNumber=int(szPortNumber)
    messagebox.showinfo("Info","Default value '"+iPortNumber+"'is the port number")
def CloseSettingsWindow():
    global RootLibraryFolderPath
    szSelectCurrentDir=os.getcwd()
    ET.SubElement(MainPath, "RootLibraryFolderPath").text = RootLibraryFolderPath
    ET.SubElement(MainPath, "CfdExePath").text =CfdExePath
    tree = ET.ElementTree(MainMode)
    tree.write(szSelectCurrentDir+"\\"+"SettingsConfigure.xml")
    dialog_window.destroy()
        
# Creating Settings dialog dialog
def CreateSettingsdialog():
    global dialog_window
    global txtPortNumber
    global CfdExePath
    global txtEntryRootFolderPath
    global txtEntryCfdExePath
    dialog_window = Toplevel()
    dialog_window.geometry("330x180+300+200")
    dialog_window.grab_set()
    dialog_window.title("Settings")
    # Label to display Select path
    lblSelectMainStoragePath=Label(dialog_window,text="Select a path for Storage:")
    lblSelectMainStoragePath.grid(row=0,column=0,sticky=W)
    # Button to browse Root folder path
    btnBrowseMainPath = Button(dialog_window, text='Browse...', bg="Light Blue",command=SelectMainPath,width=7, height=1)
    btnBrowseMainPath.grid(row=1,column=1,padx=10)
    # Text entry to display selected root folder path
    txtEntryRootFolderPath = Entry(dialog_window,width=40,bg="azure")
    txtEntryRootFolderPath.grid(row=1,column=0,sticky=W,padx=5,ipady=4)
    # Tooltip for root folder text entry
    txtEntryRootFolderPathTooltip=CreateToolTip(txtEntryRootFolderPath,"Select the folder to create and \nstore all your testcases")
    # Label to display Select CFD exe
    lblSelectCfdExePath=Label(dialog_window,text="Select a path for CFD.exe(Mandatory):")
    lblSelectCfdExePath.grid(row=2,column=0,sticky=W)
    # Button to browse CFD exe path
    btnBrowseCfdExePath = Button(dialog_window, text='Browse...',bg="Light Blue",command=SelectCfdExePath,width=7, height=1)
    btnBrowseCfdExePath.grid(row=3,column=1,padx=10)
    # Text entry to display selected CFD exe path
    txtEntryCfdExePath = Entry(dialog_window,width=40,bg="azure")
    txtEntryCfdExePath.grid(row=3,column=0,sticky=W,padx=5,ipady=4)
    # Tooltip for CFD solver text entry
    txtEntryCfdExePathTooltip=CreateToolTip(txtEntryCfdExePath,"Select the path of CFD solver( .exe )")
    # Label for port number
    lblSelectPortNumber=Label(dialog_window,text="Port number:")
    lblSelectPortNumber.grid(row=4,column=0,sticky=W)
    # Text entry take port number
    txtPortNumber = Entry(dialog_window,width=40,bg="azure")
    txtPortNumber.grid(row=5,column=0,sticky=W,padx=5,ipady=4)
    # Tooltip for port number text entry
    txtPortNumberTooltip=CreateToolTip(txtPortNumber,"Enter the port number on which\nclient is running (default = '9999')")
    # Button to Select the port number
    btnPortNumber = Button(dialog_window, text='Click',bg="Light Blue",command=EnterPortNumber,width=7, height=1)
    btnPortNumber.grid(row=5,column=1,padx=10)
    # Button ok
    btnOk = Button(dialog_window, text='Ok',bg="Light Blue",width=7, height=1,command=CloseSettingsWindow)
    btnOk.grid(row=6,column=0,pady=5)
    
    dialog_window.lift()
# Lifting Settings dialog window
def ShowSettingsdialog():
    if dialog_window is None:
        CreateSettingsdialog()
        return
    try:
        dialog_window.lift()
    except TclError:
        CreateSettingsdialog()

def OnClickCreateNewTestCaseWindow():
    global dialog_window
    global szEnteredTestCaseName
    global RootLibraryFolderPath
    dialog_window = Toplevel()
    dialog_window.geometry("518x250+250+160")
    dialog_window.grab_set()
    dialog_window.title("New Testcase")
    # Label frame for all the buttons and entries
    lblfCreateNewTestcase = LabelFrame(dialog_window,font=('arial',10))
    lblfCreateNewTestcase.grid(pady=5,ipady=10)
    # Label for the name
    lblEnterTestcaseName = Label(lblfCreateNewTestcase, font=('arial',10),text="Name :")
    lblEnterTestcaseName.grid(row=0,column=0,pady=5,sticky=W)
    # Text entry for printing the name of the test case
    txtEntryEnterTestcase = Entry(lblfCreateNewTestcase,width=50,bg="azure")
    txtEntryEnterTestcase.grid(row=0,column=1,pady=5,ipady=3)
    # Tooltip for Testcasename text entry
    txtEntryEnterTestcaseTooltip=CreateToolTip(txtEntryEnterTestcase,"Enter any name of your choice\n( Eg: Testcase1 )")
    # Label for the moedl filder
    lblModelFolder = Label(lblfCreateNewTestcase, font=('arial',10),text="Model folder :")
    lblModelFolder.grid(row=1,column=0,pady=2,sticky=W)
    # Text entry for priniting the name of the Model folder
    txtEntryBrowseModelFolder = Entry(lblfCreateNewTestcase,width=50,bg="azure")
    txtEntryBrowseModelFolder.grid(row=1,column=1,pady=2,padx=20,ipady=3)

    # Function On clck creat new testcase
    def OnClickCreateNewTestCase():
        global szModelFolder
        global szBaseLineFolder
        global szCopiedModelFolder
        global szTargetFolderPath
        if len(CfdExePath)==0:
            messagebox.showerror("Error","You have to select the CFD solver path")
            return
        szStatusbar['text']="Enter a testcase name of your choice"
        # Text box input 
        szEnteredTestCaseName=txtEntryEnterTestcase.get()
	# Checking if the text box is empty
        if len(szEnteredTestCaseName) == 0:
            # Displaying the error message
            messagebox.showerror("Error","Please enter a valid testcase name")
            return
        if os.path.isdir(os.path.join(RootLibraryFolderPath,szEnteredTestCaseName)):
            messagebox.showerror("Error", "Testcase alredy exists")
        else:
	    # Printing which testcase name user has entered 
            szStatusbar['text']="Testcase Name :"+" "+szEnteredTestCaseName
            txtEntryEnterTestcase.config(state=DISABLED)
            szStatusbar['text']="Select a Model Folder"
	    # UI dialog for selecting the folder 
            szModelFolder = filedialog.askdirectory(title="Select Model Folder")
	    # Checking if the selection is done 
            if len(szModelFolder) == 0:
		# Displaying the error message
                messagebox.showerror("Error","Please select a valid folder, Selection process terninated")
                return
            if szModelFolder == RootLibraryFolderPath:
                messagebox.showerror("Error","Model folder and Rootpath should not be same\nSelect different location")
            else:
                txtEntryBrowseModelFolder.insert(0,szModelFolder)
                txtEntryBrowseModelFolder.config(state=DISABLED)
		# Obtaining the path of the user selected folder
                szTargetFolderPath = os.path.join(RootLibraryFolderPath,szEnteredTestCaseName)           

                if not os.path.exists(szTargetFolderPath):
                    os.makedirs(szTargetFolderPath)
		    # Copping the user selected folder to model folder location
                    szCopiedModelFolder = os.path.join(szTargetFolderPath, os.path.basename(szModelFolder))  
                    shutil.copytree(szModelFolder, szCopiedModelFolder)
                    szBaseLineFolder = os.path.join(szTargetFolderPath,"BaseLineFiles")                 
                    os.makedirs(szBaseLineFolder)
                    btnBrowseModelFolder.config(state=DISABLED)
                    
    # Button to browse the model folder
    btnBrowseModelFolder=Button(lblfCreateNewTestcase,text="Browse...",
                                bg="Light Blue",command=OnClickCreateNewTestCase,width=7)
    btnBrowseModelFolder.grid(row=1,column=2,pady=2,padx=10)
    # Tool tip for Model Folder Browse button
    szBrowseModelFolderTooltip = CreateToolTip(btnBrowseModelFolder, "Select the model folder which \ncontains the python scipt to run on CFD")
    # Label for the Python script
    lblPythonScript = Label(lblfCreateNewTestcase, font=('arial',10),text="Python script :")
    lblPythonScript.grid(row=2,column=0,pady=2,sticky=W)
    # Text entry for printing the name of the Python script
    txtEntryPythonScript = Entry(lblfCreateNewTestcase,width=50,bg="azure")
    txtEntryPythonScript.grid(row=2,column=1,pady=2,padx=20,ipady=3)
    # Nested Function on click select select python file
    def OnClickSelectPythonFile():
        global szPythonFilePath
        global szTempFolder
        if len(szModelFolder)== 0:
               szStatusbar['text']="Select Model folder in order to browse the python file"
               return 

        szStatusbar['text']="Select Python Script"
        
        szPythonFilePath = filedialog.askopenfilename(initialdir=szModelFolder,title="Select Python File",
                                                      filetypes = (("python files","*.py"),("all files","*.*"))) 
	# Checking if the selection is done 
        if len(szPythonFilePath) == 0:
            messagebox.showerror("Error","Please select a valid python file, Selection process terninated")
        else:
            txtEntryPythonScript.insert(0,szPythonFilePath)
            txtEntryPythonScript.config(state=DISABLED)
            szTempFolder=os.path.join(szTargetFolderPath,"Temp")
            os.makedirs(szTempFolder)
            szFilesInsideBaseline=os.listdir(szCopiedModelFolder)
            for i in szFilesInsideBaseline:
                szFilesInsideBaselinePath=os.path.join(szCopiedModelFolder,i)
                shutil.copy2(szFilesInsideBaselinePath,szTempFolder)
            szSelectedPythonFileBasename=os.path.basename(szPythonFilePath)
            szPythonFileForCFD=os.path.join(szTempFolder,szSelectedPythonFileBasename)
            szStatusbar['text']="Click yes to execute python file,CFD will run in background  "
            szMsgBoxYesNo=messagebox.askyesno("Message", "Do you want to run the current \nPython script on CFD ?")
            if szMsgBoxYesNo == True:
                subprocess.call([CfdExePath,'-script',szPythonFileForCFD])
                szStatusbar['text']="CFD Finished execution"
                return
            szStatusbar['text']="Select the Files to copy into the baseline"
            btnBrowsePythonScript.config(state=DISABLED)
            return
    # Button to browse the Python script
    btnBrowsePythonScript=Button(lblfCreateNewTestcase,text="Browse...",
                                bg="Light Blue",command=OnClickSelectPythonFile,width=7, height=1)
    btnBrowsePythonScript.grid(row=2,column=2,pady=2,padx=10,)
    # Tool tip for python script Browse button
    btnBrowsePythonScriptTooltip = CreateToolTip(btnBrowsePythonScript, "Select the python script to\nrun on CFD solver")
    # Label for the Baseline files
    lblBaselineFiles = Label(lblfCreateNewTestcase, font=('arial',10),text="Baseline files :")
    lblBaselineFiles.grid(row=4,column=0,sticky=W)
    # Lis box to show all the files 
    lstBoxListAllBaseLineFiles = Listbox(lblfCreateNewTestcase,selectmode=EXTENDED,width=50,height=6,bg="azure")
    lstBoxListAllBaseLineFiles.grid(row=3,column=1,rowspan=3)
    def OnClickAddBaselineFilesList():
        if len(szModelFolder) == 0:
            szStatusbar['text']="Please create testcase,select modelfolder for Adding the baseline files"
            return
        if len(szPythonFilePath)== 0:
            szStatusbar['text']="Please create testcase,python file for Adding the baseline files"
            return
        szSelectedUserFilesForBaseline=filedialog.askopenfilename(initialdir=szTempFolder,title="Select Files for Baseline",multiple=1)
        for i in szSelectedUserFilesForBaseline:
            lstBoxListAllBaseLineFiles.insert(END, i)
            
    # Button to Add theBaseline files
    btnBrowseBaselineFiles=Button(lblfCreateNewTestcase,text="Add",bg="Light Blue",width=7, height=1,command=OnClickAddBaselineFilesList)
    btnBrowseBaselineFiles.grid(row=3,column=2)
    # Tooltip for add baseline files button
    btnBrowseBaselineFilesTooltip=CreateToolTip(btnBrowseBaselineFiles,"Select the files to be added\ninto baseline for comparision")
    #button to delete the baseline files
    def OnClickDeleteBaselineFileList():
        if len(lstBoxListAllBaseLineFiles.get(0,END)) == 0:
            szStatusbar['text']="Listbox is empty, Cannot remove an entry"
        else:
            selection =lstBoxListAllBaseLineFiles.curselection()
            lstBoxListAllBaseLineFiles.delete(selection)
        
    btnBrowseDeleteFiles=Button(lblfCreateNewTestcase,text="Delete",bg="Light Blue",width=7, height=1,command=OnClickDeleteBaselineFileList)
    btnBrowseDeleteFiles.grid(row=4,column=2)
    # Tooltip for delete baseline files button
    btnBrowseDeleteFilesTooltip=CreateToolTip(btnBrowseDeleteFiles,"Select the files in the listbox to be\nremoed from the baseline and click\non Delete button")
    # Button to Copy the files into baseline files
    def OnClickCopyTheFilesTOBaseline():
        if len(lstBoxListAllBaseLineFiles.get(0,END)) == 0:
            szStatusbar['text']="Listbox is empty, Add Files to Copy to Baseline"
        else:
            szGetAllListItems=lstBoxListAllBaseLineFiles.get(0,END)
            for i in range(0,len(szGetAllListItems)):
                shutil.copy2(os.path.join(szCopiedModelFolder,os.path.basename(szGetAllListItems[i])),szBaseLineFolder)
                szStatusbar['text']="The selected files have been copied into the baseline"
                
            ET.SubElement(ChildNode, "ModelFolder").text = szCopiedModelFolder
            ET.SubElement(ChildNode, "PythonFilePath").text =szPythonFilePath
            for i in range(0,len(szGetAllListItems)):
                szStrConvertions=str(i)
                ET.SubElement(ResultNode, "UserSelectedResult-"+szStrConvertions).text=szGetAllListItems[i]
            tree = ET.ElementTree(ParentNode)
            tree.write(szTargetFolderPath+"\\"+"allpaths.xml")
            messagebox.showinfo("Success", "Testcase has been created ")
            shutil.rmtree(szTempFolder, ignore_errors=False, onerror=None)
            dialog_window.destroy()
    btnAllDone=Button(lblfCreateNewTestcase,text="Ok",bg="Light Blue",width=7, height=1,command=OnClickCopyTheFilesTOBaseline)
    btnAllDone.grid(row=5,column=2)

    # Label for the Status bar
    szStatusbar= Label(dialog_window,text=" ",anchor=W)
    szStatusbar.grid(sticky=W+E+N+S)
    szStatusbar['text']="Enter a testcase name of your choice"
    
    dialog_window.lift()
    
def ShowCreateNewTestCasedialog():
    global RootLibraryFolderPath
    if len(RootLibraryFolderPath) == 0:
        RootLibraryFolderPath = os.getcwd()
        return
    if dialog_window is None:
        OnClickCreateNewTestCaseWindow()
        return
    try:
        dialog_window.lift()
    except TclError:
        if len(RootLibraryFolderPath) == 0:
            RootLibraryFolderPath = os.getcwd()
            return
        OnClickCreateNewTestCaseWindow()
    

lblAppname = Label(szMainFrame,font=('arial',30, 'bold'),text="CFD AUTOMATION TOOL",fg="Steel Blue")
lblAppname.grid(row=0,column=0)

btnSettings = Button(szMainFrame,bg="Light Blue",command=ShowSettingsdialog,height=20,width=20)
Settingsicon = Settingsicon.subsample(6)
btnSettings.config(image=Settingsicon)
btnSettings.grid(row=0,column=1,padx=20)

btnCreateNewTestCase = Button(szMainFrame, text='Create new test case', bg="Light Blue",width=30, height=5,command=ShowCreateNewTestCasedialog)
btnCreateNewTestCase.grid(row=1,column=0,pady=10)
def EnterClientIp():
    global szIpAddress
    szEnterClientIpWindow=Toplevel()
    szEnterClientIpWindow.geometry("170x70+400+400")
    szEnterClientIpWindow.grab_set()
    szEnterClientIpWindow.title("Enter IP Of Client")
    txtEnteyClientName=Entry(szEnterClientIpWindow)
    txtEnteyClientName.grid(row=0,padx=10,pady=10,ipadx=10)
    def SelectIP():
        global szIpAddress
        szIpAddress=txtEnteyClientName.get()
        szPingStr = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
        szPingClient = "ping " + " " + szPingStr + " " + szIpAddress
        szPingReturnVal = False if  platform.system().lower()=="windows" else True
        szPingRes=subprocess.call(szPingClient, shell=szPingReturnVal) == 0
        if szPingRes == True:
            lstBoxListAllClients.insert(END,szIpAddress)
        else:
            messagebox.showerror("Error","Requested Client is inactive")
        szEnterClientIpWindow.destroy()
    btnAddClintName=Button(szEnterClientIpWindow, text='Ok', bg="Light Blue",width=7, height=1,command=SelectIP)
    btnAddClintName.grid(row=1)
def ShowEnerClientdialog():
    if dialog_window is None:
        EnterClientIp()
        return
    try:
        dialog_window.lift()
    except TclError:
        EnterClientIp()
# Function to create run testcase
def CreateRunTestWindow():
    global szDialogEindowForRunTestcase
    global lstBoxListAllClients
    szDialogEindowForRunTestcase = Toplevel()
    szDialogEindowForRunTestcase.geometry("405x366+250+160")
    szDialogEindowForRunTestcase.grab_set()
    szDialogEindowForRunTestcase.title("Run Testcase")
    # Label frame for Run testcase
    lblfRunTestcase = LabelFrame(szDialogEindowForRunTestcase,font=('arial',10))
    lblfRunTestcase.grid(ipady=5,pady=5,padx=2,ipadx=40)
    # Label test case name
    lblAppname = Label(lblfRunTestcase,text="Test Cases :")
    lblAppname.grid(row=0,column=0,sticky=W,padx=5)
    # Tooltip for label testcase name
    lblAppnameTooltip=CreateToolTip(lblAppname,"You can select any\nnumber of testcases to run")
    # Label test status
    lblStatus = Label(lblfRunTestcase,text="Status :")
    lblStatus.grid(row=0,column=1,sticky=W)
    # Tooltip for label client list
    lblStatusTooltip=CreateToolTip(lblStatus,"Future use")
    # List box to display all the testcases
    lstBoxListAllTestCases = Listbox(lblfRunTestcase,selectmode='multiple',width=30,height=6,bg="azure",exportselection=0)
    lstBoxListAllTestCases.grid(row=1,column=0,padx=5,ipady=40,sticky=W)
    szAllDirectories=os.listdir(RootLibraryFolderPath)
    for i in szAllDirectories:
            lstBoxListAllTestCases.insert(END, i)

    def OnSelectRunTestCase():
        global iPortNumber
        global szIpAddress
        szBrowserNewTab = 2
        szListBoxSelectedValue=lstBoxListAllTestCases.curselection()
        szListBoxSelectedClient=lstBoxListAllClients.curselection()
        if len(szListBoxSelectedValue)==0:
            messagebox.showerror("Error","Please select a testcase")
            return
        if len(szListBoxSelectedClient)== 0:
            messagebox.showerror("Error","Select Client machine to run on,\nYou can even select LocalRun")
            return
        #szStatusbarRunTestcase['text']="You have selected LocalRun CDF will run in the background"
        szLocalClientSelected=lstBoxListAllClients.get(szListBoxSelectedClient)
        if szLocalClientSelected == "LocalRun":
            for j in szListBoxSelectedValue:
                szSelectedFolderName=os.path.join(RootLibraryFolderPath, lstBoxListAllTestCases.get(j))
                szEmptyFolder=os.listdir(szSelectedFolderName)
                if len(szEmptyFolder) == 0:
                    szStatusbarRunTestcase['text']="Selected testcase folder is empty please select a valid folder"
                else:
                    szTestCaseInput = szSelectedFolderName

        
                    szReadXml=minidom.parse(szTestCaseInput+"\\"+"allpaths.xml")
                    szListForHoldingResultFiles=[]
                    szXmlModelFolder=szReadXml.getElementsByTagName('ModelFolder')
                    szXmlPythonFile=szReadXml.getElementsByTagName('PythonFilePath')
                    szModelFolder=(szXmlModelFolder[0].firstChild.data)
                    szPythonFile=(szXmlPythonFile[0].childNodes[0].data)
        
                    subprocess.call([CfdExePath,'-script',szPythonFile])

                    # Selecting the baseline files
                    szBaseLineFolderName="BaseLineFiles"
                    szBaselineFolderLocation=os.path.join(szTestCaseInput,szBaseLineFolderName)
                    # Variable to select the Date and time
                    szDateAndTime=time.strftime("%d%m%Y-%H%M%S")
                    # Creating a new directory base on the date and time
            
                    szCoppyBeforeRun = os.path.join(szTestCaseInput,"Run_"+szDateAndTime)
                    os.makedirs(szCoppyBeforeRun)
            
                    szLocalFolder=os.path.join(szCoppyBeforeRun,"LocalRun")
                    os.makedirs(szLocalFolder)
            
                    # Loop to select the Result file from the xml
                    for elem in szReadXml.getElementsByTagName('ResultNode'):
                        for x in elem.childNodes:
                            if x.nodeType == Node.ELEMENT_NODE:
                                szListForHoldingResultFiles.append(x.childNodes[0].data)
                    # Loop to select the Basename of the files from xml and copying it to the dedicated run folder 
                    for i in range(0,len(szListForHoldingResultFiles)):
                        szResulfFileBasename=os.path.basename(szListForHoldingResultFiles[i])
                        szAllResultFileModelFolderPath=os.path.join(szModelFolder,szResulfFileBasename)
                        shutil.copy2(szAllResultFileModelFolderPath,szLocalFolder)
                
                    szCommonFilesInLocalRun=filecmp.dircmp(szBaselineFolderLocation,szLocalFolder)
                    for j in szCommonFilesInLocalRun.common_files:
                        szCommonFilesInBaselineForRun=os.path.join(szBaselineFolderLocation, j)
                        szCommonFilesInCoppyBeforeRun=os.path.join(szLocalFolder, j)
                        context  = True
                        context_number = 0
                        szFirstFileOpenToreadFronRun=open(szCommonFilesInBaselineForRun,"r")
                        szSecondFileOpenToreadFronRun=open(szCommonFilesInCoppyBeforeRun,"r")
                        szDifferenceInRun=difflib.HtmlDiff().make_file(
                            szFirstFileOpenToreadFronRun.readlines(),szSecondFileOpenToreadFronRun.readlines(),
                            szCommonFilesInBaselineForRun,szCommonFilesInCoppyBeforeRun, context, context_number)
                        szLocalOutputResult=open(os.path.join(szLocalFolder, "report.html"), "a")
                        szLocalOutputResult.write(szDifferenceInRun)
                        szLocalOutputResult.close()
                        urlLocalRun=os.path.join(szLocalFolder, "report.html")
                    webbrowser.open(urlLocalRun,new=szBrowserNewTab)
            szDialogEindowForRunTestcase.destroy()
        else:
            def GetAllFilePath(directory):
                file_paths = []
                # crawling through directory and subdirectories
                for root, directories, files in os.walk(directory):
                    for filename in files:
                        # join the two strings in order to form the full filepath.
                        filepath = os.path.join(root, filename)
                        file_paths.append(filepath)

                # returning all file paths
                return file_paths
            def ThreadStart(szIpAddress,szSelectedClientTestCasePath,szSelectedClientTestCase):
                # Creating a socket
                szSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                szSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                szSocket.settimeout(None)
                # Socket connecting
                szSocket.connect((szIpAddress,iPortNumber))
                #szStatusbarRunTestcase['text']="Connected with the client"
                # Selecting the directory name
                szSocket.send(szSelectedClientTestCase.encode('utf8'))
                
                # Sending the path and calling the function to get all the paths
                szZipFilePath=GetAllFilePath(szSelectedClientTestCasePath)

                with ZipFile('CfdAutomationTool.zip', 'w') as zip:
                    for file in szZipFilePath:
                        zip.write(file,file.replace(szSelectedClientTestCasePath, ""))
                #sending zip file
                szZipedFileSending='CfdAutomationTool.zip'
                with open(szZipedFileSending, "rb") as f:
                    szZipedData=f.read()
                    szSocket.sendall(szZipedData)
                szSocket.shutdown(socket.SHUT_WR)
                # Reciving zip file
                szRecivingZipContent = open("szRecivedResultZip.zip", "wb")
                while True:
                    szRecivedContent=szSocket.recv(4096)
                    if not szRecivedContent:
                        break
                    szRecivingZipContent.write(szRecivedContent)
                szRecivingZipContent.close()
                # Variable to select the Date and time
                szDateAndTime=time.strftime("%d%m%Y-%H%M%S")
                szCoppyBeforeRun = os.path.join(szSelectedFolderName,"Run_"+szDateAndTime)
                os.makedirs(szCoppyBeforeRun)
                szClientFolder=os.path.join(szCoppyBeforeRun,"Client."+szIpAddress)
                os.makedirs(szClientFolder)
                # Unziping the Recived content
                szExtractingFiles=zipfile.ZipFile("szRecivedResultZip.zip")
                szExtractingFiles.extractall(szClientFolder)
                # Selecting the baseline files
                szBaseLineFolderName="BaseLineFiles"
                szBaselineFolderLocation=os.path.join(szSelectedFolderName,szBaseLineFolderName)
                szCommonFilesInLocalRun=filecmp.dircmp(szBaselineFolderLocation,szClientFolder)
                for j in szCommonFilesInLocalRun.common_files:
                    szCommonFilesInBaselineForRun=os.path.join(szBaselineFolderLocation, j)
                    szCommonFilesInCoppyBeforeRun=os.path.join(szClientFolder, j)
                    context  = True
                    context_number = 0
                    szFirstFileOpenToreadFronRun=open(szCommonFilesInBaselineForRun,"r")
                    szSecondFileOpenToreadFronRun=open(szCommonFilesInCoppyBeforeRun,"r")
                    szDifferenceInRun=difflib.HtmlDiff().make_file(
                        szFirstFileOpenToreadFronRun.readlines(),szSecondFileOpenToreadFronRun.readlines(),
                        szCommonFilesInBaselineForRun,szCommonFilesInCoppyBeforeRun, context, context_number)
                    szLocalOutputResult=open(os.path.join(szClientFolder, "report.html"), "a")
                    szLocalOutputResult.write(szDifferenceInRun)
                    szLocalOutputResult.close()
                    urlClientRun=os.path.join(szClientFolder, "report.html")
                webbrowser.open(urlClientRun,new=szBrowserNewTab)
                szSocket.close()
                
            for i in szListBoxSelectedClient:
                szIpAddress=lstBoxListAllClients.get(i)
                for j in szListBoxSelectedValue:
                    szSelectedClientTestCase=lstBoxListAllTestCases.get(j)
                    szSelectedFolderName=os.path.join(RootLibraryFolderPath, szSelectedClientTestCase)
                    szEmptyFolder=os.listdir(szSelectedFolderName)
                    if len(szEmptyFolder) == 0:
                        szStatusbarRunTestcase['text']="Selected testcase folder is empty please select a valid folder"
                    else:
                        szSelectedClientTestCasePath = szSelectedFolderName
                        szNewThread=threading.Thread(target=ThreadStart,args=(szIpAddress,szSelectedClientTestCasePath,szSelectedClientTestCase))
                        szNewThread.start()
                        szNewThread.join()
            szDialogEindowForRunTestcase.destroy()
    # List box to display Status
    lstBoxListAllStatus = Listbox(lblfRunTestcase,selectmode=EXTENDED,width=20,height=6,bg="azure",exportselection=0)
    lstBoxListAllStatus.config(state=DISABLED)
    lstBoxListAllStatus.grid(row=1,column=1,ipady=40)
    # Label for Client list
    lblClientList = Label(lblfRunTestcase,text="Client List :")
    lblClientList.grid(row=2,column=0,sticky=W,padx=5)
    # Tooltip for label client list
    lblClientListTooltip=CreateToolTip(lblClientList,"You can either select 'LocalRun'\nor any number of client IP-Address")
    # List box to display the client list
    lstBoxListAllClients = Listbox(lblfRunTestcase,selectmode='multiple',exportselection=0,width=30,height=6,bg="azure")
    lstBoxListAllClients.grid(row=3,column=0,padx=5,sticky=W,rowspan=2)
    # Fixed list box value for Local machine 
    lstBoxListAllClients.insert(0,"LocalRun")
    # Button to add client
    btnAddClient = Button(lblfRunTestcase, text='AddClient', bg="Light Blue",width=7, height=1,command=ShowEnerClientdialog)
    btnAddClient.grid(row=3,column=1)
    # Tooltip for add client button
    btnAddClientTooltip=CreateToolTip(btnAddClient,"Enter the IP-Address\nof the client machine")
    # Button to run the Testcase
    btnRun = Button(lblfRunTestcase, text='Run', bg="Light Blue",width=7, height=1,command=OnSelectRunTestCase)
    btnRun.grid(row=4,column=1)
    # Status bar
    szStatusbarRunTestcase= Label(szDialogEindowForRunTestcase,text="Status Bar",anchor=W)
    szStatusbarRunTestcase.grid(sticky=N+S+W+E)
    szStatusbarRunTestcase['text']="Select the Testcase of your choice from the list and also select the Client"
    
def ShowRunTestCasedialog():
    global RootLibraryFolderPath
    if len(RootLibraryFolderPath) == 0:
        RootLibraryFolderPath = os.getcwd()
        return
    if dialog_window is None:
        CreateRunTestWindow()
        return
    try:
        dialog_window.lift()
    except TclError:
        if len(RootLibraryFolderPath) == 0:
            RootLibraryFolderPath = os.getcwd()
            return
        CreateRunTestWindow()
btnCompareResults = Button(szMainFrame, text="Run Testcase", bg="Light Blue",width=30, height=5,command=ShowRunTestCasedialog)
btnCompareResults.grid(row=2,column=0,pady=10) 

szSelectCurrentDir=os.getcwd()
szConfigureXmlLocation=os.path.join(szSelectCurrentDir,"SettingsConfigure.xml")
szCheckExist=os.path.exists(szConfigureXmlLocation)
if szCheckExist == True:
    szReadXml=minidom.parse(szSelectCurrentDir+"\\"+"SettingsConfigure.xml")
    
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
