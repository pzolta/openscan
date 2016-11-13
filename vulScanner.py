# -*- coding: latin-1 -*-
import openVAS
import subprocess
import time

class vulScanner(object):
    """A serulekenyseg vizsgalatot osszefogo modul"""
    openVASServices = ["openvasmd", "openvassd"]

    def __init__(self, exceptionList = None, targetList = None):
        self.exceptionList = exceptionList
        self.targetList = targetList
        self.vas = openVAS.openVAS()
        return

    msg1 = "OpenVAS inditasa:\t[openvas]\nKilepes:\t\t\t[exit]"

    def startScanners(self):
        self.vas.startOpenvasServices()
        return

    def stopScannerTasks(self):
        for service in self.openVASServices:
            if self.isRunning(service):
                self.vas.stopAnyOpenvasTask()
                break
        return

    def killAllScanners(self):
        #ide erkezhet a kesobbiekben mas szkenner modul is
        for service in self.openVASServices:
            if self.isRunning(service):
                self.vas.stopAnyOpenvasTask()
                self.vas.stopOpenvasServices()
                break
        return

    #forras: http://serverfault.com/questions/319684/what-s-s1-t-r-mean-in-ps-ax-ps-list
    processStateCodes = "D    Uninterruptible sleep (usually IO)\n" \
                        "R    Running or runnable (on run queue)\n" \
                        "S    Interruptible sleep (waiting for an event to complete)\n" \
                        "T    Stopped, either by a job control signal or because it is being traced.\n" \
                        "W    paging (not valid since the 2.6.xx kernel)\n" \
                        "X    dead (should never be seen)\n" \
                        "Z    Defunct ('zombie') process, terminated but not reaped by its parent.\n\n" \
                        "<    high-priority (not nice to other users)\n" \
                        "N    low-priority (nice to other users)\n" \
                        "L    has pages locked into memory (for real-time and custom IO)\n" \
                        "s    is a session leader\n" \
                        "l    is multi-threaded (using CLONE_THREAD, like NPTL pthreads do)\n" \
                        "+    is in the foreground process group\n"

    folyamatAllapotKod = "D    Varakozo allapot (altalaban I/O)\n" \
                        "R    Futo, vagy futtathato (varakozo sorban)\n" \
                        "S    Megszakithato alvas\n" \
                        "T    Megallithato, utemezo jel altal vagy debug uzemmoddal\n" \
                        "W    Lapozott\n" \
                        "X    Nem valaszol\n" \
                        "Z    Zombi folyamat\n\n" \
                        "<    magas prioritasu\n" \
                        "N    alacsony prioritasu\n" \
                        "L    gyorsitotarazott a memoriaban\n" \
                        "s    munkamenet-vezer\n" \
                        "l    tobbszalasitott\n" \
                        "+    aktiv folyamatok csoportjaba tartozo\n"

    def isRunning(self, serviceName=None, verbose=False):
        """Input: a lekerdezendo szolgaltatas neve"""
        if  (serviceName == None):
            print("Nem adtal meg szolgaltatas nevet!")
            return
        else:
            # inString = "ps aux | grep " + serviceName
            inString = "ps cax | grep " + serviceName
            output = subprocess.getoutput(inString)
            if output.__contains__(serviceName):
                if verbose:
                    print(self.folyamatAllapotKod)
                    print(output)
                return True
        return False

    def vulscannerController(self):
        """Ezen keresztul lehet a vulScanner modult iranyitani"""
        #ide majd johet egy valasztas, hogyha tobb scannert is beepitek
        prefixString = "<vulScanner> "
        end = False
        while (end == False):
            print("\n" + prefixString + "\n" + self.msg1)
            command = input(prefixString + "Parancs:")
            command = command.upper()
            if (command == "EXIT"):
                end = True
            elif (command.startswith("OPENVAS")):
                self.vas.openvasController()
            else:
                print("<vulScanner>: Nem adtal meg ervenyes parancsot")
                #time.sleep(1)
        return

    selectedOpenVASTaskID = None
    def selectSingleOpenVASTask(self):
        """1: feladat inditasa, 2: feladat megallitasa (itt csak azt lehessen, amit mar elinditottunk"""
        prefixString = "<vulScanner/selectSingleOpenVASTask> "
        if self.selectedOpenVASTaskID is None:
            #self.selectedOpenVASTaskID = self.vas.manageTasks(operateRemotely=True)
            result = self.vas.manageTasks(operateRemotely=True)
            if result == False:
                return result
            else:
                self.selectedOpenVASTaskID = result
        else:
            print(prefixString + "Mar letezik kivalasztott feladat!\nID:" + str(self.selectedOpenVASTaskID))
            cmd = input("[1]\tFeladat megtartasa\n[2]\tTorles es uj letrehozasa")
            if cmd == '2':
                self.selectedOpenVASTaskID = self.vas.manageTasks(operateRemotely=True)
            else:
                print("Torles elvetve.")
        return

    reportIdOfSelectedTask = None
    def startSingleOpenVASTask(self):
        prefixString = "<vulScanner/startSingleOpenVASTask> "
        if self.selectedOpenVASTaskID is None:
            print(prefixString+"Meg nem valasztott ki feladatot!")
            self.selectedOpenVASTaskID = self.vas.manageTasks(operateRemotely=True)
        else:
            result = self.vas.fireSingleTaskStart(self.selectedOpenVASTaskID, safeStart=True)
            #itt megnezni, sikeres-e az inditas
            if result == False:
                print("\n" + prefixString + "A feladat inditasa sikertelen!")
                return False
            else:
                print("\n" + prefixString + "A feladat inditasa sikeres!")
                self.reportIdOfSelectedTask = result
                return True
            #ha nem, vissza false, feladat torlese
        return

    def selectedOpenVASTaskFinished(self):
        if self.selectedOpenVASTaskID is None:
            print("Meg nem kerult OpenVAS task utemezesre!")
            return None
        elif self.reportIdOfSelectedTask is None:
            #print("A feladat meg nem kerult elinditasra.")
            return None
        else:
            result = self.vas.isTaskFinished(self.selectedOpenVASTaskID, self.reportIdOfSelectedTask)
        return result