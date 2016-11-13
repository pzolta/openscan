# -*- coding: latin-1 -*-
import time
from datetime import datetime
import subprocess
import vulScanner
import webDiscover
from apscheduler.schedulers.background import BackgroundScheduler


class logic(object):
    """A GUI-t, network discovert es serulekenyseg viszgalatot, valamint az adatokat kezelo osztaly.
    Mas neven: kozponti logika."""

    #SZUKSEG VAN A DATEUTIL TELEPITESERE IS: PIP INSTALL PYTHON-DATEUTIL

    scannersAcitve = False
    # TODO: rendszergazdai jogok tesztelese
    msg1 = "Kerem vegye biztosra, hogy on rendszergazdai (root) fiokkal hasznalja az eszkozt. Ha on nem redszergazda, lepjen ki a programbol es inditsa azt a megfelelo jogokkal ujra."
    nmapScheduler = BackgroundScheduler()
    openVASScheduler = BackgroundScheduler()

    def __init__(self):
        print("\n" + self.msg1)
        self.scanner = vulScanner.vulScanner()
        self.webdiscover = webDiscover.webDiscover()
        self.startVulScannerModule()
        self.controlLogic()
        return

    def controlLogic(self):
        helpString = "Kilepes\t[exit]\nSzolgaltatas vizsgalata\t[check]\nBelepes a vulScan modulba\t[scan]\nBelepes a webDiscover modulba\t[discover]\nFeladat idozitese\t[schedule]\nVeszleallas\t[CTRL-C]"
        prefixString = "<logic> "

        try:
            end = False
            while (end == False):
                print("\n" + helpString + "\n")
                str1 = input(prefixString + "Parancs: ")
                str1 = str1.upper()
                if (str1 == "EXIT"):
                    end = True
                elif (str1.startswith("CHECK") == True):
                    #incmd = str1[6:]
                    #incmd = incmd.lower()
                    #self.isServiceRunning(incmd)
                    self.areServicesRunning()
                elif (str1.startswith("SCAN") == True):
                    self.passControlToVulScan()
                elif (str1.startswith("DISCOVER") == True):
                    self.passControlToWebDiscover()
                elif (str1.startswith("SCHED") == True):
                    self.scheduleController()
                else:
                    print("Nem adott meg ervenyes parancsot.")
            return
        except (KeyboardInterrupt, SystemExit):
            print(prefixString + "Veszleallast kezdemenyezett. Minden komponens, idozito es folyamat megszakitasara keszul. Folytatja?")
            confirm = input("[1]\tIgen\n[2]\tMegsem\nParancs:")
            if str(confirm) == "1":
                self.killAllScheduling(self.nmapScheduler)
                self.killAllScheduling(self.openVASScheduler)
                self.stopVulScannerModule()
                #TODO: nmap megallitasa!
            else:
                self.controlLogic()
            pass
        return

    msg2 = "[1]\t\tOpenVAS feladat utemezese\n[2]\t\tNmap feladat utemezese\n[exit]\tKilepes"
    def scheduleController(self):
        """Utemez egy OpenVAS vagy NMAP feladatot. Minden feladattipusbol kizarolag egyet futtathatunk egyszerre."""
        #scheduler = self.mainscheduler
        ovJobID = "OpenVAS"
        nmJobID = "Nmap"
        prefixString = "<logic/scheduleController> "
        try:
            end = False
            while (end == False):
                print("\n" + prefixString + "\n" + self.msg2)
                command = input(prefixString + "Parancs:")
                command = command.upper()
                scheduler = None
                if (command == "EXIT"):
                    cnt = input(prefixString + "A kilepessel torlodnek az utemezesek. Folytatja?\n[1]\tKielepes\n[2]\tMegsem")
                    if cnt == "1":
                        end = True
                        self.killAllScheduling(self.nmapScheduler)
                        self.killAllScheduling(self.openVASScheduler)
                elif (command == "1"):
                    jobID = ovJobID
                    scheduler = self.openVASScheduler
                    if(self.isTaskInProgress(scheduler, jobID)):
                        print("\n" + prefixString + "Mar hozzaadott egy feladatot!")
                        self.printJobInfo(scheduler, jobID)
                    else:
                        self.OpenVASTasker(scheduler, jobID)
                        #print(prefixString + "Feladat hozzaadva.")

                elif (command == "2"):
                    jobID = nmJobID
                    scheduler = self.nmapScheduler
                    if (self.isTaskInProgress(scheduler, jobID)):
                        print("\n" + prefixString + "Mar hozzaadott egy feladatot!")
                        self.printJobInfo(scheduler, jobID)
                    else:
                        self.NMAPTasker(scheduler, jobID)
                else:
                    print(prefixString + "Nem adott meg ervenyes parancsot")
        except (KeyboardInterrupt, SystemExit):
            #csak akkor kezeljuk le a kilepest, ha tenyleg van futo, leallitando feladat
            if (self.isTaskInProgress(scheduler, ovJobID) or self.isTaskInProgress(scheduler, nmJobID)):
                self.interruptHandler(scheduler)
            else:
                print()
        return

    def printJobInfo(self, scheduler, jobID):
        jobID = str(jobID)
        job = scheduler.get_job(jobID)
        nextRunTime = str(job.next_run_time)
        schedulerType = type(job.trigger).__name__

        if(job.pending):
            isPending = "Igen"
        else:
            isPending = "False"

        if(job._scheduler.running):
            isRunning = "Igen"
        else:
            isRunning = "False"

        timeZone = str(job._scheduler.timezone)

        print("Feladat azonositoja: " + jobID)
        print("Kovetkezo futas ideje: " + nextRunTime)
        print("Utemezo tipusa: " + schedulerType)
        print("A feladat fuggoben van: " + isPending)
        print("A feladat fut: " + isRunning)
        print("Idozona tipusa: " + timeZone)

        return

    cronCollection = [["month", '*'], ["day", '*'], ["week", '*'], ["day_of_week", '*'], ["hour", '*'], ["minute", '*']]
    cronHelperString = ["honap", "nap", "het", "het napja", "ora", "perc"]

    helper = "* 		any 	Fire on every value\n" \
           "*/a 	any 	Fire every a values, starting from the minimum\n" \
           "a-b 	any 	Fire on any value within the a-b range (a must be smaller than b)\n" \
           "a-b/c 	any 	Fire every c values within the a-b range\n" \
           "xth y 	day 	Fire on the x -th occurrence of weekday y within the month\n" \
           "last x 	day 	Fire on the last occurrence of weekday x within the month\n" \
           "last 	day 	Fire on the last day within the month\n" \
           "x,y,z 	any 	Fire on any matching expression; can combine any number of any of the above expressions"

    def setCronCollectionToDefault(self):
        self.cronCollection = [["month", '*'], ["day", '*'], ["week", '*'], ["day_of_week", '*'], ["hour", '*'], ["minute", '*']]
        return

    def setCronTime(self, prefixString = ""):
        end = False
        while (end == False):
            print("\n" + prefixString + "\n" + "Adja meg az idozitesi beallitasokat (ENTER az alapertelmezetthez):")
            print(self.helper)

            counter = 0
            for c in self.cronCollection:
                print(self.assembleCronString(counter))
                command = input(self.cronHelperString[counter] + ": ")
                if command.upper() == "EXIT":
                    end = True
                    self.setCronCollectionToDefault()
                    return False
                else:
                    if command == '*' or command == '':
                        c[1] = '*'
                    else:
                        c[1] = command
                    counter += 1
            end = True
        return True

    def assembleCronString(self, highlight=None):
        s = ""
        counter = 0
        for c in self.cronCollection:
            if (highlight and (counter == highlight)):
                s += "[" + c[0] + "=" + c[1] + "] "
            else:
                s += c[0] + "=" + c[1] + " "
        return s

    def isTaskInProgress(self, scheduler, jobID):
        taskList = scheduler.get_jobs()
        for t in taskList:
            #if str(t).__contains__(jobID):
            #    return True
            if t.id == jobID:
                return True
        return False

    intervalCollection = [["weeks", 0], ["days", 0], ["hours", 0], ["minutes", 0]]
    intervalHelperString = ["hetek", "napok", "orak", "percek", "ora", "masodpercek"]

    def setIntervalCollectionToDefault(self):
        self.intervalCollection = [["weeks", 0], ["days", 0], ["hours", 0], ["minutes", 0]]
        return

    def setIntervalTime(self, prefixString=""):
        end = False
        while (end == False):
            print("\n" + prefixString + "\n" + "Adja meg az idozitesi beallitasokat (ENTER az alapertelmezetthez):")
            print(self.helper)

            try:
                counter = 0
                for c in self.intervalCollection:
                    print(self.assembleIntervalString(counter))
                    command = input(self.intervalHelperString[counter] + ": ")
                    if command.upper() == "EXIT":
                        end = True
                        self.setIntervalCollectionToDefault()
                        return False
                    else:
                        if command == '':
                            c[1] = 0
                        else:
                            c[1] = int(command)
                        counter += 1
            except ValueError as v:
                print(v)
                print("Csak szamot adhat meg! Probalja ujra.")
                #"reset"
                counter = 0
                self.setIntervalCollectionToDefault()

            end = True
        return True

    def assembleIntervalString(self, highlight=None):
        s = ""
        counter = 0
        for c in self.intervalCollection:
            if (highlight and (counter == highlight)):
                s += "[" + str(c[0]) + "=" + str(c[1]) + "] "
            else:
                s += str(c[0]) + "=" + str(c[1]) + " "
        return s

    openVASTaskInProgress = False
    def OpenVASTasker(self, scheduler, jobID):
        argDict = {}

        end = False
        while (end == False):
            print("\n" + "Milyen idozitest szeretne hasznalni?\n[1]\tIdoponthoz kotott\n[2]\tIntervallumhoz kotott")
            command = input("Parancs:")
            command = command.upper()
            if (command == "1"):

                #CRON-szignaturas idopont eloallitasa
                self.setCronTime()

                #CRON-os feladat utemezese
                foundValidItem = False
                for c in self.cronCollection:
                    # az argumentumokhoz dictionary-t kell kesziteni a listabol
                    argDict[c[0]] = c[1]
                    if c[1] != '*':
                        foundValidItem = True

                if (foundValidItem == False):
                    print("Nincs ervenyes CRON idopont megadva!")
                    return

                result = self.selectVulscanTask()
                if result == False:
                    print("Folyamat megszakitva.")
                    return False

                schedResult = scheduler.add_job(lambda: self.startVulscanTask(), 'cron', id=jobID, **argDict)
                if schedResult.pending:
                    print("Sikeres hozzaadas, feladat allapota: fuggoben")
                end = True

            elif (command == "2"):
                #interval idopont beallitasa
                self.setIntervalTime()
                foundValidItem = False
                for i in self.intervalCollection:
                    # az argumentumokhoz dictionary-t kell kesziteni a listabol
                    argDict[i[0]] = i[1]
                    if i[1] != 0:
                        foundValidItem = True

                if (foundValidItem == False):
                    print("Nincs ervenyes intervallum megadva!")
                    return

                # feladat kivalasztasa
                result = self.selectVulscanTask()
                if result == False:
                    print("Folyamat megszakitva.")
                    return False

                #result = self.startVulscanTask()
                #if result == False:
                #    print("Folyamat megszakitva.")
                #    return False

                # feladat hozzaadasa
                schedResult = scheduler.add_job(lambda: self.startVulscanTask(), 'interval', id=jobID, **argDict)
                if schedResult.pending:
                    print("Sikeres hozzaadas, feladat allapota: fuggoben")
                #if result == False:
                #    self.removeJobById(jobID)
                #    print("Folyamat megszakitva.")
                #else:
                #    print("Utemezes sikeres!")
                end = True

            else:
                print("Nem adott meg ervenyes parancsot")

        try:
            print("CTRL+C a megszakitashoz")
            scheduler.start()
            #sikeres volt a feladat inditas, mindenre "reset"
            self.setCronCollectionToDefault()
            self.setIntervalCollectionToDefault()
            return
        except (KeyboardInterrupt, SystemExit):
            self.interruptHandler(scheduler)
            pass
        return

    def selectVulscanTask(self):
        # bovites eseten differencialni kell
        result = self.scanner.selectSingleOpenVASTask()
        return result

    def selectNMAPTask(self):
        result = self.webdiscover.selectSingleNMAPTask()
        return result

    lastVulscanTaskState = None
    def startVulscanTask(self):
        # bovites eseten differencialni kell
        if self.scanner.selectedOpenVASTaskFinished() != False:
            result = self.scanner.startSingleOpenVASTask()
            self.lastVulscanTaskState = result
            return result
        else:
            print("Az elozo feladat meg fut, ezert ujabb feladat nem indithato.")
        return

    msg3 = "[1]\tUtemezo leallitasa\n[2]\tUtemezo hatterben futtatasa"
    def interruptHandler(self, scheduler, forceStop = False):
        #ha a forceStop == True, akkor kerdes nelkul mindent megszakit es leallit
        if forceStop:
            print("Osszes folyamat megallitasa")
            self.killAllScheduling(scheduler)
            # TODO: teljes openvas + NMAP garantalt megallitasa
            self.stopVulScannerModule()
            self.stopWebDiscoverModule()
        else:
            scheduler.print_jobs()
            end = False
            while (end == False):
                print("\n" + self.msg3)
                command = input("Parancs:")
                command = command.upper()
                if (command == "1"):
                    self.killAllScheduling(scheduler)
                    #TODO: teljes openvas + NMAP garantalt megallitasa
                    self.stopVulScannerTasks()
                    end = True
                elif (command == "2"):
                    scheduler.resume()
                    end = True
                else:
                    print("Nem adott meg ervenyes parancsot")
        return

    def killAllScheduling(self, scheduler):
        if scheduler.running:
            scheduler.remove_all_jobs()
            self.setCronCollectionToDefault()
            self.setIntervalCollectionToDefault()
            scheduler.shutdown(wait=False)
        return

    def removeJobById(self, scheduler, jobId):
        scheduler.remove_job(jobId)
        return

    def tick(self, user):
        print("{} - Tick! A pontos ido: {}".format(user, str(datetime.now())))
        return


    def startWebDiscoverTask(self):
        # bovites eseten differencialni kell
        if self.webdiscover.selectedNMAPTaskFinished != False: #vagy nincs elkezdve, vagy nem fut
            if self.nmapTaskInProgress:
                print("Mar utemezett egy NMAP feladatot!")
            else:
                self.nmapTaskInProgress = True
                result = self.webdiscover.startSingleNMAPTask()
                self.nmapTaskInProgress = False
            return result
        else:
            print("Az elozo feladat meg fut, ezert ujabb feladat nem indithato.")
        return

    nmapTaskInProgress = False
    def NMAPTasker(self, scheduler, jobID):
        argDict = {}

        end = False
        while (end == False):
            print("\n" + "Milyen idozitest szeretne hasznalni?\n[1]\tIdoponthoz kotott\n[2]\tIntervallumhoz kotott")
            command = input("Parancs:")
            command = command.upper()
            if (command == "1"):

                # CRON-szignaturas idopont eloallitasa
                self.setCronTime()

                # CRON-os feladat utemezese
                foundValidItem = False
                for c in self.cronCollection:
                    # az argumentumokhoz dictionary-t kell kesziteni a listabol
                    argDict[c[0]] = c[1]
                    if c[1] != '*':
                        foundValidItem = True

                if (foundValidItem == False):
                    print("Nincs ervenyes CRON idopont megadva!")
                    return

                result = self.selectNMAPTask()
                if result == False:
                    print("Folyamat megszakitva.")
                    return False

                schedResult = scheduler.add_job(lambda: self.startWebDiscoverTask(), 'cron', id=jobID, **argDict)
                if schedResult.pending:
                    print("Sikeres hozzaadas, feladat allapota: fuggoben")
                end = True

            elif (command == "2"):
                # interval idopont beallitasa
                self.setIntervalTime()
                foundValidItem = False
                for i in self.intervalCollection:
                    # az argumentumokhoz dictionary-t kell kesziteni a listabol
                    argDict[i[0]] = i[1]
                    if i[1] != 0:
                        foundValidItem = True

                if (foundValidItem == False):
                    print("Nincs ervenyes intervallum megadva!")
                    return

                # feladat kivalasztasa
                result = self.selectNMAPTask()
                if result == False:
                    print("Folyamat megszakitva.")
                    return False

                # feladat hozzaadasa
                schedResult = scheduler.add_job(lambda: self.startWebDiscoverTask(), 'interval', id=jobID, **argDict)
                if schedResult.pending:
                    print("Sikeres hozzaadas, feladat allapota: fuggoben")
                end = True

            else:
                print("Nem adott meg ervenyes parancsot")

        try:
            print("CTRL+C a megszakitashoz")
            scheduler.start()
            # sikeres volt a feladat inditas, mindenre "reset"
            self.setCronCollectionToDefault()
            self.setIntervalCollectionToDefault()
            return
        except (KeyboardInterrupt, SystemExit):
            self.interruptHandler(scheduler)
            pass
        return

    def passControlToVulScan(self):
        """Atadja az iranyitast a Vulscan modulnak"""
        self.scanner.vulscannerController()
        return

    def passControlToWebDiscover(self):
        """Atadja az iranyitast a Vulscan modulnak"""
        self.webdiscover.webDiscoverController()
        return

    def startVulScannerModule(self):
        """Elinditja a VulScanner-ben csatolt serulekenysegvizsgalo modulokat"""
        print("Szolgaltatasok inditasa. Kerem, varjon.")
        self.scanner.startScanners()
        return

    def stopVulScannerModule(self):
        """Leallitja a VulScanner-ben csatolt serulekenysegvizsgalo modulokat"""
        print("VulScanner szolgaltatasok leallitasa. Kerem, varjon.")
        self.scanner.killAllScanners()
        return

    def stopVulScannerTasks(self):
        print("VulScanner futo feladatainak leallitasa. Kerem, varjon.")
        self.scanner.stopScannerTasks()
        return

    def stopWebDiscoverModule(self):
        """Leallitja a WebDiscoverben-ben csatolt modulok szolgaltatasait"""
        print("WebDiscover szolgaltatasok leallitasa. Kerem, varjon.")
        self.webdiscover.stopScannerTasks()
        return
    
    implementedModuleServices = ["nmap", "openvassd", "openvasmd"]
    
    def areServicesRunning(self):
        for service in self.implementedModuleServices:
            state = self.isRunning(service, True)
            if state:
                print(service + ", allapot: AKTIV")
            else:
                print(service + ", allapot: INAKTIV")
        return
    
    def isRunning(self, serviceName=None, verbose=False):
        """Input: a lekerdezendo szolgaltatas neve"""
        if (serviceName == None):
            print("Nem adott meg szolgaltatas nevet!")
            return
        else:
            inString = "ps cax | grep " + serviceName
            output = subprocess.getoutput(inString)
            if output.__contains__(serviceName):
                if verbose:
                    details = subprocess.getoutput("ps aux | grep " + serviceName)
                    info = (details.split('\n')[0].split(serviceName))[1]
                    if info != '':
                        #csak akkor nyomtatunk plusz informaciot, ha az letezik
                        print(serviceName + info)
                return True
        return False

