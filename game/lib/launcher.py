# Filename: launcher.py
# Created by:  blach (09Nov14)
# Edited by:  blach (12Apr15) - Improved the way files are validated
# Edited by:  blach (14Jul15) - Improved the gui
# Edited by:  blach (06Nov15) - Improved security and using SSL

import sys
import os
import ctypes
import subprocess
import hashlib
from uuid import getnode as getMacAddress

from panda3d.core import *
loadPrcFileData('startup', 'window-type none')
loadPrcFileData('startup', 'default-directnotify-level info')
from direct.showbase.ShowBase import ShowBase
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.distributed.PyDatagram import PyDatagram
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task import Task

from Tkinter import *
from PIL import Image, ImageTk
import ttk
import tkMessageBox
base = ShowBase()
base.startTk()

CLIENT_MD5 = 0
SERVER_MD5 = 1
ACC_VALIDATE = 10
ACC_INVALID = 11
ACC_VALID = 12
ACC_CREATE = 13
ACC_CREATED = 14
ACC_EXISTS = 15
DL_TIME_REPORT = 16
LAUNCHER_VERSION = 17
LAUNCHER_GOOD = 18
LAUNCHER_BAD = 19
FETCH_DL_LIST = 20
DL_LIST = 21
REQUEST_BASE_LINK = 101
BASE_LINK = 102
SERVER_MSG = 103

baseLink = ""
files2Download = []

class Launcher:
    notify = directNotify.newCategory("Launcher")
    appTitle = "Cog Invasion Launcher"
    loginServer_port = 7033
    Server_host = "gameserver-dev.coginvasion.com"
    timeout = 2000
    version = 1.4
    helpVideoLink = "http://download.coginvasion.com/videos/ci_launcher_crash_help.mp4"
    hashFileLink = "http://download.coginvasion.com/file_info.txt"
    contactLink = "http://coginvasion.com/contact-us.html"

    def __init__(self):
        self.tk = base.tkRoot
        self.tk.geometry("581x436")
        self.tk.title(self.appTitle)
        self.tk.resizable(0, 0)
        self.tk.iconbitmap('icon.ico')
        self.launcherFSM = ClassicFSM('launcher', [State('menu', self.enterMenu, self.exitMenu, ['login', 'updateFiles', 'accCreate']),
            State('fetch', self.enterFetch, self.exitFetch, ['menu']),
            State('validate', self.enterValidate, self.exitValidate, ['fetch']),
            State('connect', self.enterConnect, self.exitConnect, ['validate']),
            State('accCreate', self.enterAccCreate, self.exitAccCreate, ['submitAcc', 'menu']),
            State('submitAcc', self.enterSubmitAcc, self.exitSubmitAcc, ['menu', 'accCreate']),
            State('login', self.enterLogin, self.exitLogin, ['play', 'menu']),
            State('play', self.enterPlay, self.exitPlay, ['connect']),
            State('updateFiles', self.enterUpdateFiles, self.exitUpdateFiles, ['login']),
            State('off', self.enterOff, self.exitOff)], 'off', 'off')
        self.launcherFSM.enterInitialState()
        self.loginUserName = StringVar()
        self.loginPassword = StringVar()
        self.downloadTime = {}

        # This var is in case the user sent incorrect account info
        # so they don't have to update all their files again.
        self.alreadyUpdated = False

        self.__initConnectionManagers()
        self.checkHasFolder("logs")
        self.checkHasFolder("screenshots")
        self.checkHasFolder("config")
        self.launcherFSM.request('connect')

    def __initConnectionManagers(self):
        self.cMgr = QueuedConnectionManager()
        self.cReader = QueuedConnectionReader(self.cMgr, 0)
        self.cWriter = ConnectionWriter(self.cMgr, 0)
        self.http = HTTPClient()
        self.rf = Ramfile()
        self.channel = self.http.makeChannel(True)

    def checkHasFolder(self, folderName):
        if not os.path.isdir(folderName):
            os.mkdir(folderName)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterValidate(self):
        self.infoLbl = canvas.create_text(287, 210, text = "Validating...", fill = "white")
        self.tk.update()
        self.badLauncherMsg = None
        dg = PyDatagram()
        dg.addUint16(LAUNCHER_VERSION)
        dg.addFloat64(self.version)
        self.cWriter.send(dg, self.Connection)

    def __handleBadLauncher(self):
        self.badLauncherMsg = tkMessageBox.showwarning(parent = self.tk, title = "Error", message = "This launcher is out of date. Please go to coginvasion.com and download the latest launcher.")
        sys.exit()

    def exitValidate(self):
        canvas.delete(self.infoLbl)
        del self.infoLbl
        if self.badLauncherMsg:
            self.badLauncherMsg.destroy()
            del self.badLauncherMsg

    def enterFetch(self):
        self.infoLbl = canvas.create_text(287, 210, text = "Fetching download list...", fill = "white")
        self.tk.update()
        self.sendBaseLinkRequest()
        self.downloadHashFile()

    def sendBaseLinkRequest(self):
        dg = PyDatagram()
        dg.addUint16(REQUEST_BASE_LINK)
        self.cWriter.send(dg, self.Connection)

    def __handleBaseLink(self, dgi):
        global baseLink
        baseLink = dgi.getString()
        print "base link is: " + baseLink

    def exitFetch(self):
        canvas.delete(self.infoLbl)
        del self.infoLbl

    def enterUpdateFiles(self):
        self.currentFile = -1
        self.filesDownloaded = 0
        self.currentMD5 = ""
        self.title = canvas.create_text(287, 167, text = "Updating files...", fill = "white")
        self.infoLbl = canvas.create_text(287, 215, fill = "white")
        self.progBar = ttk.Progressbar(orient = "horizontal", length = 100, mode = "determinate")
        self.progBar.place(x = 237, y = 230)
        self.nextFile()

    def nextFile(self):
        self.currentFile += 1
        if self.currentFile > len(files2Download) - 1:
            if self.filesDownloaded > 0:
                self.reportDownloadTimes()
            self.alreadyUpdated = True
            self.launcherFSM.request('login')
            return
        fileName = files2Download[self.currentFile]
        canvas.itemconfigure(self.infoLbl, text = "File {0} of {1}... ({2})".format(self.currentFile + 1, len(files2Download), fileName))
        self.downloadFile()

    def reportDownloadTimes(self):
        print "----------DOWNLOAD TIMES----------"
        totalTime = 0
        for k, v in self.downloadTime.iteritems():
            print files2Download[k] + ": " + str(self.downloadTime[k]) + " seconds."
            totalTime += self.downloadTime[k]
        print "Total time: " + str(totalTime) + " seconds."
        dg = PyDatagram()
        dg.addUint16(DL_TIME_REPORT)
        dg.addFloat64(totalTime)
        self.cWriter.send(dg, self.Connection)

    def startTrackingDownloadTime(self):
        self.downloadTime[self.currentFile] = 0.0
        self.currentDownloadStartTime = globalClock.getFrameTime()

    def stopTrackingDownloadTime(self):
        self.downloadTime[self.currentFile] = globalClock.getFrameTime() - self.currentDownloadStartTime
        del self.currentDownloadStartTime

    def downloadFile(self):
        name = files2Download[self.currentFile]
        fullLink = baseLink + name
        self.channel.beginGetDocument(DocumentSpec(fullLink))
        self.channel.downloadToFile(name)
        taskMgr.add(self.__downloadTask, "downloadTask")
        self.startTrackingDownloadTime()

    def __downloadTask(self, task):
        if self.channel.run():
            try:
                self.progBar['value'] = 100.*self.channel.getBytesDownloaded()/self.channel.getFileSize()
            except:
                pass
            return task.cont
        self.filesDownloaded += 1
        self.stopTrackingDownloadTime()
        self.progBar['value'] = 0
        self.nextFile()
        return task.done

    def downloadHashFile(self):
        self.notify.info("Downloading hash file...")
        self.channel.beginGetDocument(DocumentSpec(self.hashFileLink))
        self.channel.downloadToRam(self.rf)
        taskMgr.add(self.__downloadHashFileTask,"dlHashFileTask")

    def __downloadHashFileTask(self, task):
        if self.channel.run():
            return task.cont
        data = self.rf.getData()
        self.__finishedDownloadingHashFile(data)
        return task.done

    def __finishedDownloadingHashFile(self, data):
        self.notify.info("Reading hash file...")
        for line in data.splitlines():
            if len(line) <= 0 or line[:2] == "//":
                continue
            fileName, md5 = line.split(' ')
            if not self.isSameMD5(fileName, md5):# or not self.isSameFileSize(fileName, size):
                self.notify.info("{0} is out of date or missing! Adding to download list.".format(fileName))
                files2Download.append(fileName)
            else:
                self.notify.info("{0} is up to date!".format(fileName))
        if len(files2Download) > 0:
            self.notify.info("Will download files: " + str(files2Download))
        else:
            self.notify.info("All files are up to date!")
        self.launcherFSM.request('menu')

    def isSameMD5(self, filename, md5):
        return os.path.isfile(filename) and hashlib.sha1(open(filename, 'rb').read()).hexdigest() == md5

    def isSameFileSize(self, filename, size):
        return os.path.isfile(filename) and os.path.getsize(filename) == size

    def sendMD5(self, fileName):
        dg = PyDatagram()
        dg.addUint16(CLIENT_MD5)
        dg.addString(fileName)
        dg.addString(self.currentMD5)
        self.cWriter.send(dg, self.Connection)

    def __handleServerMD5(self, dgi):
        servermd5 = dgi.getString()
        if servermd5 == self.currentMD5:
            self.nextFile()
        else:
            self.downloadFile()

    def exitUpdateFiles(self):
        canvas.delete(self.title)
        del self.title
        self.progBar.place_forget()
        del self.progBar
        canvas.delete(self.infoLbl)
        del self.infoLbl

    def enterMenu(self):
        try:
            admin = os.getuid() == 0
        except:
            admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not admin:
            self.adminLbl = canvas.create_text(287, 220, text = "You must run the Cog Invasion Launcher\nwith administrator rights for correct operation.", fill = "red")
            self.notify.warning("Launcher is not running in administrator mode!")
            return
        self.title = canvas.create_text(287, 167, text = "Log-In", fill = "white")
        self.userNameEntryLbl = canvas.create_text(195, 198, text = "Username:", fill = "white", font = ("Arial", 12))
        self.passwordEntryLbl = canvas.create_text(196, 228, text = "Password:", fill = "white", font = ("Arial", 12))
        self.userNameEntry = Entry(self.tk, textvariable = self.loginUserName)
        self.passwordEntry = Entry(self.tk, textvariable = self.loginPassword, show = "*")
        self.userNameEntry.place(x = 242, y = 190)
        self.passwordEntry.place(x = 242, y = 220)
        self.loginBtn = Button(self.tk, text = "  Play  ", command = self.__handleLoginButton)
        self.loginBtn.place(x=375, y=203)
        #self.crashBtn = Button(self.tk, text = "Game Crashes When It Opens", command = self.sendToHelpVideo)
        #self.crashBtn.pack(side=BOTTOM)
        self.accBtn = Button(self.tk, text = "Create Account", command = self.__handleAccCreateButton)
        self.accBtn.place(x = 242, y = 265)
        self.contactBtn = Button(self.tk, text = "Contact Us/Report A Bug", command = self.__handleContactButton)
        self.contactBtn.place(x = 220, y = 405)

    def __handleContactButton(self):
        os.startfile(self.contactLink)

    def sendToHelpVideo(self):
        os.startfile(self.helpVideoLink)

    def __handleAccCreateButton(self):
        self.launcherFSM.request('accCreate')

    def exitMenu(self):
        if hasattr(self, 'adminLbl'):
            canvas.delete(self.adminLbl)
            del self.adminLbl
        canvas.delete(self.title)
        del self.title
        canvas.delete(self.userNameEntryLbl)
        canvas.delete(self.passwordEntryLbl)
        self.userNameEntry.place_forget()
        self.passwordEntry.place_forget()
        self.loginBtn.place_forget()
        self.accBtn.place_forget()
        self.contactBtn.place_forget()
        del self.contactBtn
        del self.userNameEntryLbl
        del self.passwordEntryLbl
        del self.userNameEntry
        del self.passwordEntry
        del self.loginBtn
        del self.accBtn

    def enterConnect(self):
        self.connectingLbl = canvas.create_text(287, 210, text = "Connecting...", fill = "white")
        self.tk.update()
        self.Connection = self.cMgr.openTCPClientConnection(self.Server_host, self.loginServer_port, self.timeout)
        self.noConnectionDialog = None
        if self.Connection:
            self.cReader.addConnection(self.Connection)
        if self.Connection:
            taskMgr.add(self.datagramPoll, "datagramPoll", -40)
            self.launcherFSM.request('validate')
        else:
            self.__handleNoConnection()

    def __handleNoConnection(self):
        self.noConnectionDialog = tkMessageBox.showwarning(parent = self.tk, title = "Error", message = "Could not connect to the servers.")
        sys.exit()

    def exitConnect(self):
        canvas.delete(self.connectingLbl)
        del self.connectingLbl
        if self.noConnectionDialog:
            self.noConnectionDialog.destroy()
            del self.noConnectionDialog

    def __handleLoginButton(self):
        if not self.alreadyUpdated:
            self.launcherFSM.request('updateFiles')
        else:
            self.launcherFSM.request('login')

    def enterLogin(self):
        self.loggingInLbl = canvas.create_text(287, 210, text = "Logging in...", fill = "white")
        self._sendLoginCredidentials()

    def _sendLoginCredidentials(self):
        dg = PyDatagram()
        dg.addUint16(ACC_VALIDATE)
        dg.addString(self.loginUserName.get())
        dg.addString(self.loginPassword.get())
        # Send this to the account server which is self.Connection
        self.cWriter.send(dg, self.Connection)

    def __handleCredidentialResp(self, resp, dgi):
        if resp == ACC_VALID:
            self.__handleValidCredidentials(dgi)
        else:
            self.__handleInvalidCredidentials()

    def __handleValidCredidentials(self, dgi):
        self.gameServer = dgi.getString()
        self.gameVersion = dgi.getString()
        self.loginToken = dgi.getString()
        self.launcherFSM.request('play')

    def __handleInvalidCredidentials(self):
        self.invalidDialog = tkMessageBox.showwarning(parent = self.tk, message = "Username and/or password is incorrect.", title = "Error")
        del self.invalidDialog
        self.launcherFSM.request('menu')

    def exitLogin(self):
        canvas.delete(self.loggingInLbl)
        del self.loggingInLbl

    def enterAccCreate(self):
        self.title = canvas.create_text(287, 167, text = "Create An Account", fill = "white")
        #self.title.pack()
        self.userNameEntryLbl = canvas.create_text(195, 198, text = "Username:", fill = "white", font = ("Arial", 12))
        self.passwordEntryLbl = canvas.create_text(196, 228, text = "Password:", fill = "white", font = ("Arial", 12))
        self.userNameEntry = Entry(self.tk, textvariable = self.loginUserName)
        self.passwordEntry = Entry(self.tk, textvariable = self.loginPassword, show = "*")
        self.userNameEntry.place(x = 242, y = 190)
        self.passwordEntry.place(x = 242, y = 220)
        self.doneBtn = Button(self.tk, text = "Done", command = self.__handleAccCreateDone)
        self.doneBtn.place(x=378, y=203)
        self.backBtn = Button(self.tk, text = "<<", command = self.__handleGoBackButton)
        self.backBtn.place(x=157, y=260)
        self.doneBtn.config(state=NORMAL)
        self.userNameEntry.config(state=NORMAL)
        self.passwordEntry.config(state=NORMAL)
        self.backBtn.config(state=NORMAL)

    def __handleGoBackButton(self):
        self.launcherFSM.request('menu')

    def __handleAccCreateDone(self):
        self.launcherFSM.request('submitAcc')

    def __handleInvalidEntries(self, state):
        self.invalidMsg = tkMessageBox.showwarning(
            parent = self.tk,
            message = "Your account name and password must be at least 5 characters long. " + \
                "You cannot have whitespace or blank entries. Your account name and password cannot be identical.",
            title = "Bad Entries"
        )
        self.launcherFSM.request(state)

    def enterSubmitAcc(self):
        self.infoLbl = canvas.create_text(287, 210, text = "Submitting...", fill = "white")
        if not self.validateEntries():
            self.__handleInvalidEntries('accCreate')
            return
        dg = PyDatagram()
        dg.addUint16(ACC_CREATE)
        dg.addString(self.loginUserName.get())
        dg.addString(self.loginPassword.get())
        dg.addString(str(getMacAddress()))
        self.cWriter.send(dg, self.Connection)

    def exitSubmitAcc(self):
        canvas.delete(self.infoLbl)
        del self.infoLbl

    def validateEntries(self):
        if (
            self.loginUserName.get().isspace() or len(self.loginUserName.get()) < 5 or
            self.loginUserName.get().lower() == self.loginPassword.get().lower() or
            self.loginPassword.get().isspace() or len(self.loginPassword.get()) < 5
        ):
            return False
        return True

    def __handleAccCreateResp(self, msg):
        if msg == ACC_CREATED:
            self.launcherFSM.request('menu')
        if msg == ACC_EXISTS:
            self.__handleAccExists()

    def __handleAccExists(self):
        self.accExisitsDialog = tkMessageBox.showwarning(parent = self.tk, message = "That account name already exists.", title = "Account Exists")
        del self.accExisitsDialog
        self.launcherFSM.request('accCreate')

    def exitAccCreate(self):
        canvas.delete(self.title)
        self.userNameEntry.place_forget()
        self.passwordEntry.place_forget()
        canvas.delete(self.userNameEntryLbl)
        canvas.delete(self.passwordEntryLbl)
        self.doneBtn.place_forget()
        self.backBtn.place_forget()
        del self.backBtn
        del self.title
        del self.userNameEntry
        del self.passwordEntry
        del self.userNameEntryLbl
        del self.passwordEntryLbl
        del self.doneBtn

    def enterPlay(self):
        global files2Download
        global baseLink

        # Close connection to the login server.
        self.cMgr.closeConnection(self.Connection)

        # Reset our variables for when the launcher opens back up.
        self.alreadyUpdated = False
        baseLink = ""
        files2Download = []
        self.downloadTime = {}

        # Hide the launcher gui window.
        self.tk.withdraw()

        # Set the environment variables.
        os.environ['ACCOUNT_NAME'] = self.loginUserName.get()
        os.environ['GAME_SERVER'] = self.gameServer
        os.environ['GAME_VERSION'] = self.gameVersion
        os.environ['LOGIN_TOKEN'] = self.loginToken

        # Open the game.
        subprocess.call('coginvasion.exe')

        # This stuff happens after the game closes:

        # Make sure we have the right folders present.
        self.checkHasFolder("logs")
        self.checkHasFolder("screenshots")
        self.checkHasFolder("config")

        # Show the launcher window again.
        self.tk.deiconify()

        # Re-connect to the login server.
        self.launcherFSM.request('connect')

    def exitPlay(self):
        pass

    def handleDatagram(self, datagram):
        dgi = DatagramIterator(datagram)
        msgType = dgi.getUint16()
        if msgType == ACC_VALID or msgType == ACC_INVALID:
            self.__handleCredidentialResp(msgType, dgi)
        elif msgType == ACC_CREATED or msgType == ACC_EXISTS:
            self.__handleAccCreateResp(msgType)
        elif msgType == SERVER_MD5:
            self.__handleServerMD5(dgi)
        elif msgType in [LAUNCHER_GOOD, LAUNCHER_BAD]:
            self.__handleLauncherStatus(msgType)
        elif msgType == DL_LIST:
            self.__handleDLList(dgi)
        elif msgType == BASE_LINK:
            self.__handleBaseLink(dgi)
        elif msgType == SERVER_MSG:
            self.__handleServerMsg(dgi)

    def __handleServerMsg(self, dgi):
        msg = dgi.getString()
        dialog = tkMessageBox.showwarning(parent = self.tk, message = msg, title = "Message from Server")
        self.launcherFSM.request('menu')

    def __handleDLList(self, dgi):
        global baseLink
        global fileNames
        baseLink += dgi.getString()
        numFiles = dgi.getUint8()
        for i in range(numFiles):
            files2Download.append(dgi.getString())
        self.launcherFSM.request('menu')
        print fileNames

    def __handleLauncherStatus(self, msgType):
        if msgType == LAUNCHER_GOOD:
            self.launcherFSM.request('fetch')
        else:
            self.__handleBadLauncher()

    def datagramPoll(self, task):
        if self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                self.handleDatagram(datagram)
        return Task.cont

canvas = Canvas(base.tkRoot, width = 581, height = 436)
canvas.pack()
im = Image.open('bg.png')
tkimage = ImageTk.PhotoImage(im)
canvas.create_image(290, 216.5, image = tkimage)
Launcher()
run()
