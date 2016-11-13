# -*- coding: latin-1 -*-
import nmap
import subprocess

class webDiscover(object):
    """A serulekenyseg vizsgalatot osszefogo modul"""
    def __init__(self, exceptionList = None, targetList = None):
        self.nmap = nmap.nmap()
        return

    msg1 = "Nmap inditasa:\t[nmap]\nKilepes:\t\t[exit]"
    scannerServiceNames = ["nmap"]

    def startFinders(self, scanners=None):
        # meg nincs ra szukseg, mert az nmap nem igenyel kulonosebb inditasi folyamatot
        return
    def stopFinders(self, scanners=None):
        # egyelore nincs ra szukseg, mert az nmap nem igenyel kulonosebb leallitasi procedurat
        return

    def stopScannerTasks(self):
        for service in self.scannerServiceNames:
            if self.isRunning(service):
                self.killProcess(service)
                break
        return

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
        if (serviceName == None):
            print("Nem adtal meg szolgaltatas nevet!")
            return
        else:
            inString = "ps cax | grep " + serviceName
            output = subprocess.getoutput(inString)
            if output.__contains__(serviceName):
                if verbose:
                    print(self.folyamatAllapotKod)
                    print(output)
                return True
        return False

    def webDiscoverController(self):
        """Ezen keresztul lehet a webDiscover modult iranyitani"""
        #ide majd johet egy valasztas, hogyha tobb findert is beepitek
        prefixString="<webDiscover> "
        end = False
        while (end == False):
            print("\n"+ prefixString +"\n" + self.msg1)
            command = input(prefixString + "Parancs:")
            command = command.upper()
            if (command == "EXIT"):
                end = True
            elif (command.startswith("NMAP")):
                self.nmap.nmapController()
            else:
                print("<webDiscover>: Nem adtal meg ervenyes parancsot")
                #time.sleep(1)
        return

    def killProcess(self, processName):
        prefixString = "<webDiscover> "
        output = subprocess.getoutput("killall " + processName)
        print(prefixString + output)
        return

    commandToSchedule = None
    fileNamePrefixForSchedule = None
    msg2 = "[1]\t\tAllomas felderites\n[2]\t\tKapuletapogatas\n[exit]\tKilepes"
    def selectSingleNMAPTask(self):
        prefixString = "<webDiscover/selectSingleNMAPProject> "
        end = False
        while (end == False):
            print(prefixString + "\n" + self.msg2)
            command = input(prefixString + "Parancs:")
            command = command.upper()
            if (command == "EXIT"):
                end = True
            elif (command == "1"):
                result = self.nmap.discoverHosts(operateRemotely=True)
                #end = result ezt még ki kell tesztelni
                end = result
            elif (command == "2"):
                result = self.nmap.portScan(operateRemotely=True)
                end = result
            else:
                print(prefixString + "Nem adtal meg ervenyes parancsot")

        if result:
            self.commandToSchedule = self.nmap.commandToSchedule
            self.fileNamePrefixForSchedule = self.nmap.fileNamePrefixForSchedule
            return True
        else:
            return False
        return

    selectedNMAPTaskFinished = None
    def startSingleNMAPTask(self):
        if (self.commandToSchedule is None) or (self.fileNamePrefixForSchedule is None):
            print("Nem kerult feladat kivalasztasra!")
            return False
        else:
            self.selectedNMAPTaskFinished = False
            self.nmap.passCommandToNMAP(self.commandToSchedule, self.fileNamePrefixForSchedule)
            self.selectedNMAPTaskFinished = True
            return True
        return