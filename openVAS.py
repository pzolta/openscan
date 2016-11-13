# -*- coding: latin-1 -*-
import os
import subprocess
import time
from xml.dom import minidom
#from IPy import IP
import IPy #Kulon telepiteni kell az IPy 0.83-at hozza! site: https://pypi.python.org/pypi/IPy/
import glob
import gzip
import shutil
from apscheduler.schedulers.background import BackgroundScheduler

class openVAS(object):
    """OpenVAS-t kezelo osztaly"""

    serviceList = ["openvasmd", "openvassd"]
    taskList = None
    reportFormats = []
    scanConfigList = []
    targetList = []
    openvasPortList = []
    nmapPath = str(os.getcwd()) + "/NmapScans"
    emptyPath = str(os.getcwd()) + "/empty"
    openVASWorkDirPath = ""

    msg1 = "Konfiguraciok listazasa\t[1]\nCelpontok listazasa\t\t[2]\nCelpontok kezelese\t\t[3]\nFeladatok listazasa\t\t[4]\nFeladatok kezelese\t\t[5]\nPortlistak kezelese\t\t[6]\nRiportok lekerese\t\t[7]\nNMAP felhasznalasa\t\t[8]\nOV Scan elemzese\t\t[9]\nKilepes:\t\t\t\t[exit]"
    msg2 = "Celpontok listazasa es kivalasztasa\t[1]\nCelpont letrehozasa\t\t\t\t\t[2]\nCelpont modositasa\t\t\t\t\t[3]\nCelpont torlese\t\t\t\t\t\t[4]\nCelpont reszletei\t\t\t\t\t[5]\nVissza/Megsem\t\t\t\t\t\t[exit]"
    msg3 = "Feladat listazasa es kivalasztasa\t[1]\nFeladat inditasa\t\t\t\t\t[2]\nFeladat megallitasa\t\t\t\t\t[3]\nFeladat letrehozasa\t\t\t\t\t[4]\nFeladat torlese\t\t\t\t\t\t[5]\nFeladat reszletei\t\t\t\t\t[6]\nVissza/Megsem\t\t\t\t\t\t[exit]"
    msg4 = "NMAP scan-ek listazasa \t\t\t[1]\nNMAP scan olvasasa\t\t\t\t[2]\nCelpont es feladat keszitese scan-bol\t\t[3]\nKilepes/megsem\t\t\t\t\t[exit]"

    def __init__(self):
        """Teendok, mielott a scanneles lefutna"""
        self.createOpenVASDir()
        return

    def initInternalLists(self):
        self.getReportFormats()
        self.getScanConfigs()
        self.buildOpenvasTargetList()
        return

    def printSDState(self):
        #NVT cache allapota
        output = (subprocess.getoutput("ps aux | grep openvassd"))
        splittedo = output.rsplit("\n")
        relevant = []
        #dupla inditas eseten a legutobbit mutassa
        for s in splittedo:
            if str(s).__contains__("NVT"):
                relevant.append(s)
        if relevant.__len__() != 0:
            line = str(relevant[(relevant.__len__())-1])
            i = line.index("Reloaded")
            print(line[i:])
        return

    def createOpenVASDir(self, path=os.getcwd()):
        strPath = str(path)
        try:
            if not os.path.exists(strPath + "/OpenVASScans"):
                os.makedirs(strPath + "/OpenVASScans")

            self.openVASWorkDirPath = strPath + "/OpenVASScans/"
        except OSError as e:
            print("Hiba tortent az OpenVAS munkakonyvtar letrehozasa soran: {0}".format(e))
        return

    def startOpenvasServices(self):
        os.system("openvas-start")
        print("Az OpenVAS szolgaltatasok sikeresen elindultak!")
        print("OpenVAS NVT cache frissitese. Kerem, varjon.")

        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: self.printSDState(), 'interval', seconds=5)
        scheduler.start()
        os.system("openvassd -C")
        print("Az OpenVAS sikeresen elindult!")
        scheduler.shutdown(wait=False)
        self.initInternalLists()
        return

    def stopAnyOpenvasTask(self):
        taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())
        for task in taskList:
            if task[1] != "Done" and task[1] != "Stopped":
                print(self.passCommandToOMP(" --xml='<stop_task task_id=\"" + str(task[0]) + "\" />'"))
        return

    def stopOpenvasServices(self):
        os.system("openvas-stop")
        return

    def getReportFormats(self):
        self.reportFormats = (self.splitIntoTwoColumnOutput(self.passCommandToOMP(" --get-report-formats")))

    def getScanConfigs(self):
        self.scanConfigList = (self.splitIntoTwoColumnOutput(self.passCommandToOMP(" --get-configs")))

    # TODO
    def isInitFinished(self):
        """Megnezi, hogy az openvasmd, sd felepult-e. Akkor True, ha az NVT lista is felepult"""
        command = "ps aux | grep "
        print(subprocess.getoutput(command + self.serviceList[0]))
        print(subprocess.getoutput(command + self.serviceList[1]))

    def buildOpenvasTargetList(self):
        """Visszaadja az OpenVAS-ban pillanatnyilag elerheto scan config-okat"""
        command = " -T"
        output = self.passCommandToOMP(command)
        self.targetList = self.splitIntoTwoColumnOutput(output)
        return  # output

    def getOpenvasTasks(self):
        """Visszaadja az OpenVAS-ban talalhato feladatokat"""
        command = " -G"
        output = self.passCommandToOMP(command)
        return output

    def openvasController(self):
        prefixString = "<openVASController> "

        end = False
        while (end == False):
            print("\n" + prefixString + "\n" + self.msg1)
            command = input(prefixString + "Parancs:")
            command = command.upper()
            if (command == "EXIT"):
                end = True
            elif (command == "1"):
                self.getScanConfigs()
                self.printList(self.scanConfigList)
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "2"):
                self.buildOpenvasTargetList()
                self.printList(self.targetList)
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "3"):
                self.manageTargets()
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "4"):
                self.printList(
                self.splitIntoThreeColumnOutput(self.getOpenvasTasks()))
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "5"):
                self.manageTasks()
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "6"):
                self.managePorts()
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "7"):
                self.getReportsOfATask("XML", None)
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "8"):
                self.useNMAPScans()
                input("Nyomjon ENTER-t a folytatashoz.")
            elif (command == "9"):
                self.manageScanResults()
                input("Nyomjon ENTER-t a folytatashoz.")
            else:
                print("<openvasController>: Nem adott meg ervenyes parancsot")
                #time.sleep(1)
        return

    def printList(self, list):
        for i in list:
            print(i)
        return

    def printNumberedList(self, list):
        c = 1
        for i in list:
            print("[" + str(c) + "] " + str(i))
            c+=1
        return

    def splitIntoTwoColumnOutput(self, list):
        twoColumnOutput = []
        # enterek menten vagas
        splittedOutput = list.split("\n")
        num = 0
        for i in splittedOutput:
            firstSpace = i.find(' ')
            begin = i[:firstSpace]
            firstSpace = firstSpace + 2
            end = i[firstSpace:]
            twoColumnOutput.append([])
            twoColumnOutput[num].append(begin)
            twoColumnOutput[num].append(end)
            num += 1
        # for i in self.configList:
        #    print(i)
        # num = None
        return twoColumnOutput

    def splitIntoThreeColumnOutput(self, list):
        threeColumnOutput = []
        splittedOutput = list.split("\n")
        num = 0
        for i in splittedOutput:
            firstSpace = i.find(' ')
            begin = i[:firstSpace]
            firstSpace = firstSpace + 2
            secondSpace = (i[firstSpace:]).find(' ')
            middle = i[firstSpace:(firstSpace + secondSpace)]
            end = i[(firstSpace + secondSpace):]
            threeColumnOutput.append([])
            threeColumnOutput[num].append(begin)
            threeColumnOutput[num].append(middle)
            threeColumnOutput[num].append(end)
            num += 1
        return threeColumnOutput

    def passCommandToOMP(self, command, username="vulscan", password="vulscan", host="127.0.0.1", port="9390"):
        """Atadja az input parancsot az OMP-nek"""
        prefix = "omp -u " + username + " -w " + password + " -h " + host + " -p " + port
        output = subprocess.getoutput(prefix + command)
        return output

    def createNewTask(self, taskConfigNo=None, targetUUID=None, taskName=None, taskComment=None):
        """Uj scan feladat letrehozasa (config, target)"""
        prefixString = "<openvasController/createNewTask> "
        # config kivalasztasa
        self.printNumberedList(self.scanConfigList)
        configCount = len(self.scanConfigList)

        if taskConfigNo is None:
            end = False
            while (end == False):
                selectedConfigIdx = int(
                input(prefixString + "Valassza ki a feladathoz tartozo konfiguraciot: (1-" + str(configCount) + ")"))
                selectedConfigIdx -= 1
                if (0 < selectedConfigIdx < configCount):
                    configUUID = self.scanConfigList[selectedConfigIdx][0]
                    end = True
                else:
                    print(prefixString + "Adjon meg egy ervenyes sorszamot!")
        else:
            selectedConfigIdx = taskConfigNo-1
            if (0<selectedConfigIdx<configCount):
                configUUID = self.scanConfigList[selectedConfigIdx][0]
            else:
                print(prefixString + "Ervenytelen konfiguracio szamot adott meg! Kilepes.")
                return

        # target kivalasztas vagy keszites
        if targetUUID is None:
            targetCount = len(self.targetList)
            print(prefixString + "A rendszerben szereplo celpontok (" + str(targetCount) + " db.) :")
            self.printNumberedList(self.targetList)

            end = False
            while (end == False):
                if targetCount > 0:
                    o = -1
                    while not 0 < o < 3:
                        o = int(input(prefixString + "Letezo celponthoz keszit feladatot [1], vagy ujat szeretne letrehozni [2]?"))
                        if not (0 < o < 3):
                            print(prefixString + "Helytelen input, probalja ujra.")
                        elif o == 1:
                            selectedTargetIdx = int(input(prefixString + "Valassza ki a feladathoz tartozo celpontot: (1-" + str(targetCount) + ")"))
                            end = True
                            selectedTargetIdx -= 1
                            targetUUID = self.targetList[selectedTargetIdx][0]
                        else:
                            """Ujat akart letrehozni"""
                            targetUUID = self.createNewTarget()
                            end = True
                else:
                    """Nincs meg celpont, ezert letre kell hozni ujat"""
                    targetUUID = self.createNewTarget()
                    end = True

        # feladat letrehozasa
        if taskName is None:
            name = input(prefixString + "Adja meg az uj feladat nevet: ")
        else:
            name = str(taskName)

        if taskComment is None:
            comment = input(prefixString + "Megjegyzes a feladathoz: ")
        else:
            comment = str(taskComment)

        rawXmlOutput = self.passCommandToOMP(" --xml='<create_task><name>" + name + "</name><comment>" + comment +
                              "</comment><config id=\"" + configUUID + "\"/><target id=\""
                              + targetUUID + "\"/></create_task>'")
        parsedXmlOutput = minidom.parseString(rawXmlOutput)

        state = int(parsedXmlOutput.firstChild.getAttribute("status"))
        if state != 200 and state != 201:
            print("Hiba tortent. OpenVAS hibauzenet:\n" + str(rawXmlOutput))
        else:
            taskUUID = str(parsedXmlOutput.firstChild.getAttribute("id"))
            print(prefixString + "Feladat sikeresen letrehozva!")

        # itt mindenkepp legyen self.taskList visszairas!
        self.taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())
        return taskUUID

    def createNewTarget(self, nmapTargetList=None, targetName=None, portListID=None, excludedHostList=None):
        """Letrehoz egy uj celpontot. Utana a celpontok listajat frissiteni kell!"""
        UUID = None
        prefixString = "<openvasController/createNewTarget> "

        if targetName is None:
            name = input(prefixString + "Adja meg a celpont nevet: ")
        else:
            name = targetName

        if nmapTargetList is None:
            hosts = self.addHostsToTarget(prefixString)
        else:
            hosts = self.addHostsToTargetFromList(nmapTargetList)

        if portListID is None:
            end = False
            while not end:
                try:
                    cmd = int(input(prefixString + "Hozzaad portlistat?\n[1] Igen\n[2] Nem"))
                    if cmd == 1:

                        endPortListSelection = False
                        while (endPortListSelection == False):
                            selectedPortIdx = -1
                            print(prefixString + "Kerem valassza ki a felhasznalando portlistat")

                            self.getOpenVasPortLists()
                            selectedPortIdx = int(input(prefixString + "Adja meg a portlista sorszamat: "))
                            if not (1 <= selectedPortIdx <= len(self.openvasPortList)):
                                print(prefixString + "Nem adott meg ervenyes sorszamot.")
                            else:
                                portListID = self.openvasPortList[selectedPortIdx - 1][0]
                                endPortListSelection = True

                    if cmd == 2:
                        print(prefixString + "Az alapertelmezett portlista lesz felhasznalva.")
                    end = True
                except:
                    print(prefixString + "Helytelen bevitel. Probalja ujra.")
                    end = False

        if excludedHostList is None:
            end = False
            while not end:
                try:
                    cmd = int(input(prefixString + "Hozzaad kivetelt (exclude)?\n[1] Igen\n[2] Nem"))
                    if cmd == 1:
                        excludedHosts = self.addHostsToTarget(prefixString)
                    if cmd == 2:
                        excludedHosts = ""
                    end = True
                except:
                    print(prefixString + "Helytelen bevitel. Probalja ujra.")
                    end = False
        else:
            excludedHosts = self.addHostsToTargetFromList(nmapTargetList)

        """Parancs osszeallitasa"""
        if portListID:
            cmdText = " --xml=\'<create_target><name>" + name + "</name><hosts>" + hosts + "</hosts><exclude_hosts>\"" + excludedHosts + "\"</exclude_hosts><port_list id=\"" + portListID + "\"/></create_target>\'"
        else:
            cmdText = " --xml=\'<create_target><name>" + name + "</name><hosts>" + hosts + "</hosts><exclude_hosts>\"" + excludedHosts + "\"</exclude_hosts></create_target>\'"

        rawXmlOutput = self.passCommandToOMP(cmdText)
        parsedXmlOutput = minidom.parseString(rawXmlOutput)

        state = int(parsedXmlOutput.firstChild.getAttribute("status"))
        if state != 200 and state != 201:
            print("Hiba tortent. OpenVAS hibauzenet:\n" + str(rawXmlOutput))
            UUID = ""
        else:
            UUID = str(parsedXmlOutput.firstChild.getAttribute("id"))
            print(prefixString + "Celpont sikeresen letrehozva!")
        return UUID

    def addHostsToTarget(self, prefixString=None):
        hosts = ""
        end = False
        while not end:
            correctIP = False
            while not correctIP:
                try:
                    newhost = input(prefixString + "Adja meg az IP cimet: ")
                    correctIP = IPy.IP(newhost)
                    hosts += newhost
                except:
                    print(prefixString + "Nem megfelelo az IP cim formatuma, probalja ujra.")
                    end = False

            try:
                addMore = input(prefixString + "Folytatja a hozzaadaast?\n[1] Igen\n[2] Nem")
                if int(addMore) == 1:
                    end = False
                    hosts += ", "
                elif int(addMore) == 2:
                    end = True
                else:
                    print(prefixString + "Helytelen bevitel. Probalja ujra.")
            except:
                print(prefixString + "Helytelen bevitel. Probalja ujra.")
        return hosts

    def addHostsToTargetFromList(self, hostlist):
        #TODO: state logika ide johet
        stringList = ""
        for h in hostlist:
            stringList += str(h[1]) + ","
        return stringList

    def getReportsOfATask(self, format="XML", task_id=None):
        """Lekeri egy feladathoz tartozo riportot, ha az letezik"""
        prefixString = "<openvasController/getReports> "
        taskList = self.taskList

        if (task_id == None):
            taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())
            self.printList(taskList)
            taskNum = input(prefixString + "Valaszd ki a feladatot: ")

        taskNum = int(taskNum) - 1

        """Riport UUID-k kinyerese a feladat XML-ebol"""
        rawXmlOutput = self.getTaskDetails(taskList[taskNum][0])
        parsedXmlOutput = minidom.parseString(rawXmlOutput)
        reports = parsedXmlOutput.getElementsByTagName("report")

        UUID = []
        print(prefixString + "A feladathoz tartozo riportok azonositoja: ")
        for report in reports:
            rid = report.getAttribute("id")
            if rid not in UUID:
                print(rid)
                UUID.append(rid)

        if len(UUID) == 0:
            return "Nincs riport a feladathoz"
        # erdemes lehet majd osztalyt letrehozni nekik

        formatUUID = None
        """Formatum keresese"""
        for item in self.reportFormats:
            if item[1] == format:
                formatUUID = item[0]

        if formatUUID != None:

            detailedReports = []
            for item in UUID:
                detailedReports.append(self.passCommandToOMP(
                    " -iX '<get_reports report_id=\"" + item + "\" format_id=\"" + formatUUID + "\"/>\'"))

            mode = input(prefixString + "\nKepernyore iras\t[1]\nFajlba mentes\t[2]\nMindketto\t[3]")
            if mode == '1' or mode == '3':
                for item in detailedReports:
                    print(item)

            if mode == '2' or mode == '3':
                for item in detailedReports:
                    print(prefixString + "A fajlba iras elkezdodott. Kerem, varjon.")
                    fullPath = self.saveScanResults(str(item))
                    print(prefixString + "Fajlba iras befejezbe!")

                    print(prefixString + "A fajl tomoritese elkezdodott. Kerem, varjon.")
                    compressSuccess = self.compressWithGZIP(fullPath)
                    if (compressSuccess):
                        print(prefixString + "Tomorites befejezbe!")
                        delete = input(prefixString + "Torli a felesleges, tomoritetlen fajlt?\n[1]\tIgen\n[2]\tNem")
                        if delete == "1":
                            os.remove(fullPath)
                        else:
                            print(prefixString + "Torles mellozve.")

            return detailedReports
        else:
            print(prefixString + " A kivalasztott formatum nem tamogatott, valasszon masikat")
            return

        return

    def getTaskDetails(self, task_id):
        command = " -iX '<get_tasks task_id=\""
        command += task_id + "\" details=\"1\" />'"
        output = str(self.passCommandToOMP(command))
        #self.saveScanResults(output)
        return output

    def manageTasks(self, operateRemotely=False):
        """A feladatok kezelese (start, stop)"""
        #remote - kulso iranyitast tesz lehetove, csak kivalasztas megengedett!
        prefixString = "<openvasController/manageTasks> "

        taskList = self.taskList
        taskNum = None
        end = False
        try:
            if not operateRemotely:
                while (end == False):
                    print("\n" + prefixString + "\n" + self.msg3)
                    command = input(prefixString + "Parancs:")
                    command = command.upper()
                    if (command == "EXIT"):
                        end = True
                    elif command == '1':
                        taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())
                        self.printNumberedList(taskList)
                        taskNum = input(prefixString + "Adja meg a feladat sorszamat: ")
                    elif (1 < int(command) < 4):
                        if taskList is None:
                            taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())

                        if taskNum is None:
                            print(prefixString + "Valasszon ki egy feladatot:")
                            self.printNumberedList(taskList)
                            taskNum = input(prefixString + "A feladat sorszama: ")

                        taskNum = int(taskNum)

                        print(prefixString + "A kivalasztott feladat: " + str(taskList[taskNum - 1][2]))

                        if (command == '2'):
                            print(self.passCommandToOMP(" --xml='<start_task task_id=\"" + str(taskList[taskNum - 1][0]) + "\" />'"))
                        # menet kozben elavult funkcio!
                        #elif (command == '3'):
                        #    print("A felfuggesztes elavult, valasszon masik lehetoseget.")
                        #    print(self.passCommandToOMP(" --xml='<resume_task task_id=\"" + str(taskList[taskNum - 1][0]) + "\" />'"))
                        elif (command == '3'):
                            print(self.passCommandToOMP(" --xml='<stop_task task_id=\"" + str(taskList[taskNum - 1][0]) + "\" />'"))
                        else:
                            print("Ervenytelen parancs")
                    elif (int(command) == 4):
                        self.createNewTask()
                    elif (int(command) == 5):
                        if taskList is None:
                            taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())

                        if taskNum is None:
                            print(prefixString + "Valasszon ki egy feladatot:")
                            self.printNumberedList(taskList)
                            taskNum = input(prefixString + "A feladat sorszama: ")

                        taskNum = int(taskNum)
                        print(prefixString + "A kivalasztott feladat: " + str(taskList[taskNum - 1][2]))
                        print(prefixString + self.deleteTask(str(taskList[taskNum - 1][0])))
                        taskNum = None
                    elif (int(command) == 6):
                        if taskList is None:
                            taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())

                        if taskNum is None:
                            print(prefixString + "Valasszon ki egy feladatot:")
                            self.printNumberedList(taskList)
                            taskNum = input(prefixString + "A feladat sorszama: ")

                        taskNum = int(taskNum)

                        print(prefixString + "A kivalasztott feladat: " + str(taskList[taskNum - 1][0]))
                        print(prefixString + self.getTaskXML(str(taskList[taskNum - 1][0])))
                    else:
                        print("<openvasController>: Nem adott meg ervenyes parancsot")
                        #time.sleep(1)
            else:
                while (end == False):
                    print("\n[EXIT] a megszakitashoz")
                    if taskList is None:
                        ovList = self.getOpenvasTasks()
                        #annak vizsgalata, hogy van-e task a rendszerben
                        if ovList is not None:
                            taskList = self.splitIntoThreeColumnOutput(ovList)
                        else:
                            print("Ures az OpenVAS feladatlista! Elobb letre kell hoznia egyet.")
                            return False

                    #annak vizsgalata, hogy fut-e mar egy task
                    for task in taskList:
                        taskState = task[1]
                        #if (taskState != "New") and (taskState != "Stopped"):
                        if (taskState == "Running") and (taskState != "Requested"):
                            print("Mar van aktiv feladat az OpenVAS-ban! Csak akkor utemezhet ujat, ha nincs meg aktiv feladat a rendszerben.")
                            return False
                        # hack a 'Stop','Requested' output lista miatt
                        if str(taskState + task[2]).__contains__("Requested"):
                            print("Az elozo folyamat meg nem fejezodott be!")
                            return False
                        elif str(taskState).__contains__("Internal"):
                            print("A feladatok kozott szerepel korabban hibara futtott is. Kerem, ezeket ne valassza ki!")

                    if taskNum is None:
                        print(prefixString + "Valasszon ki egy feladatot:")
                        self.printNumberedList(taskList)
                        taskNum = input(prefixString + "A feladat sorszama: ")

                    taskNum = int(taskNum)

                    print(prefixString + "A kivalasztott feladat: " + str(taskList[taskNum - 1][2]))
                    task_id = taskList[taskNum - 1][0]
                    return task_id

        except:
            print(prefixString + "Helyes bevitelt adott meg? Probalja ujra.")
            taskNum = None
            end = False
        return

    def fireSingleTaskStart(self, task_ID = None, safeStart = False):
        if task_ID is not None:

            if safeStart:
                self.taskList = self.splitIntoThreeColumnOutput(self.getOpenvasTasks())
                taskList = self.taskList

                errorFound = False
                taskIDFound = False
                for task in taskList:
                    taskState = task[1]
                    #if (taskState != "New") and (taskState != "Stopped"):
                    if (taskState == "Running") and (taskState != "Requested"):
                        print(
                            "Mar van futo feladat az OpenVAS-ban! Csak akkor utemezhet ujat, ha nincs meg aktiv feladat a rendszerben.")
                        return False
                    #hack a 'Stop','Requested' output lista miatt
                    if str(taskState + task[2]).__contains__("Requested"):
                        print("Az elozo folyamat meg nem fejezodott be!")
                        return False
                    if task[0] == task_ID:
                        taskIDFound = True
                        if str(taskState).__contains__("Internal"):
                            print("Olyan feladatot valasztott, amely korabban hibara futott. Valasszon masikat!")
                            return False

                if taskIDFound and (not errorFound):
                    rawXmlOutput = self.passCommandToOMP(" --xml='<start_task task_id=\"" + str(task_ID) + "\" />'")
                else:
                    print("A kert feladat mar nem letezik!")

            else:
                rawXmlOutput = self.passCommandToOMP(" --xml='<start_task task_id=\"" + str(task_ID) + "\" />'")

            parsedXmlOutput = minidom.parseString(rawXmlOutput)

            state = str(parsedXmlOutput.firstChild.getAttribute("status"))
            if not state.startswith("20"):
                print("Hiba tortent. OpenVAS hibauzenet:\n" + str(rawXmlOutput))
                return False
            else:
                stext = str(parsedXmlOutput.firstChild.getAttribute("status_text"))
                print(stext)
                reportID = str(parsedXmlOutput.firstChild.firstChild.firstChild.nodeValue)
                return reportID
        else:
            print("Nem adott meg ervenyes feladatot!")
            return False
        return False

    def isTaskFinished(self, taskUUID, reportUUID):
        rawXmlOutput = self.getTaskXML(taskUUID)
        parsedXmlOutput = minidom.parseString(rawXmlOutput)

        status = parsedXmlOutput.firstChild.getElementsByTagName("status")[0].firstChild.nodeValue
        if status == "Running":
            return False
        else:
            return True

    def deleteTask(self, taskUUID):

        rawOutput = self.passCommandToOMP(" --xml='<delete_task task_id=\"" + taskUUID + "\"/>'")
        xmlOutput = minidom.parseString(rawOutput)
        statusText = xmlOutput.firstChild.getAttribute("status_text")

        return statusText

    def deleteTarget(self, targetUUID):

        rawOutput = self.passCommandToOMP(" --xml='<delete_target target_id=\"" + targetUUID + "\"/>'")
        xmlOutput = minidom.parseString(rawOutput)
        statusText = xmlOutput.firstChild.getAttribute("status_text")

        return statusText

    def getTargetXML(self, targetUUID):

        rawOutput = self.passCommandToOMP(" -i --xml='<get_targets target_id=\"" + targetUUID + "\" tasks=\"1\" />'")
        #xmlOutput = minidom.parseString(rawOutput)
        #statusText = xmlOutput.firstChild.getAttribute("status_text")
        return rawOutput

    def getTaskXML(self, taskUUID):

        rawOutput = self.passCommandToOMP(" -i --xml='<get_tasks task_id=\"" + taskUUID + "\" details=\"1\" />'")
        return rawOutput

    def manageTargets(self):
        """A celpontok kezelesere szolgalo osztaly"""
        prefixString = "<openvasController/manageTargets> "

        targetNum = None
        target = ""
        end = False
        while not end:
            print("\n" + prefixString + "\n" + self.msg2)
            command = input(prefixString + "Parancs:")
            command = command.upper()


            if target != "":
                print(prefixString + "Kivalasztva: " + target)
            try:
                if command == "EXIT":
                    end = True
                elif command == "1":
                    self.buildOpenvasTargetList()
                    self.printNumberedList(self.targetList)
                    targetNum = (input("\n" + prefixString + "Adja meg a celpont sorszamat: "))
                    target = self.targetList[int(targetNum) - 1][1]
                elif command == "2":
                    self.createNewTarget()
                    self.buildOpenvasTargetList()
                    targetNum = None
                    target = ""
                elif command == "3":
                    if targetNum is None:
                        print(prefixString + "Eloszor valassza ki a celpontot.")
                        self.buildOpenvasTargetList()
                        self.printNumberedList(self.targetList)
                        targetNum = input("\n" + prefixString + "Adja meg a celpont sorszamat: ")
                        print(self.modifyTarget(self.targetList[int(targetNum) - 1][0]))
                        targetNum = None
                    else:
                        print(self.modifyTarget(self.targetList[int(targetNum) - 1][0]))
                        targetNum = None
                    target = ""
                elif command == "4":
                    if targetNum is None:
                        print("\n" + prefixString + "Eloszor valassza ki a celpontot.")
                        self.buildOpenvasTargetList()
                        self.printNumberedList(self.targetList)
                        targetNum = input(prefixString + "Adja meg a celpont sorszamat: ")
                        print(self.deleteTarget(self.targetList[int(targetNum) - 1][0]))
                        targetNum = None
                    else:
                        print(self.deleteTarget(self.targetList[int(targetNum)-1][0]))
                        targetNum = None
                    target = ""
                elif command == "5":
                    if targetNum is None:
                        print("\n" + prefixString + "Eloszor valassza ki a celpontot.")
                        self.buildOpenvasTargetList()
                        self.printNumberedList(self.targetList)
                        targetNum = input(prefixString + "Adja meg a celpont sorszamat: ")
                        print(self.getTargetXML(self.targetList[int(targetNum) - 1][0]))
                        targetNum = None
                    else:
                        print(self.getTargetXML(self.targetList[int(targetNum) - 1][0]))
                        targetNum = None
                    target = ""
                else:
                    print(prefixString + "Hibas input, probalja ujra.")
            except ValueError as v:
                print("Hiba a bevitel soran: {0}".format(v))
                if targetNum is not int:
                    print("Nem szamot adott meg!")
                    if targetNum == "exit":
                        print("Exit parancs miatt kilepes!")
                        end = True
        return

    def modifyTarget(self, targetUUID):
        """Implementalva: comment, name, hosts"""
        # opcionalisan ide lehet implementalni az ssh-t
        prefixString = "<openvasController/manageTargets/modifyTarget> "

        print("\n" + prefixString + "A kivalasztott celpont adatai:")
        rawXML = self.getTargetXML(targetUUID)
        parsedXmlOutput = minidom.parseString(rawXML)

        creationTime = str(parsedXmlOutput.firstChild.getElementsByTagName("creation_time")[0].firstChild.nodeValue)
        modificationTime = str(parsedXmlOutput.firstChild.getElementsByTagName("modification_time")[0].firstChild.nodeValue)
        owner = str(parsedXmlOutput.firstChild.getElementsByTagName("name")[0].firstChild.nodeValue)

        if parsedXmlOutput.firstChild.getElementsByTagName("comment")[0].firstChild is None:
            comment = ""
        else:
            comment = str(parsedXmlOutput.firstChild.getElementsByTagName("comment")[0].firstChild.nodeValue)

        name = str(parsedXmlOutput.firstChild.getElementsByTagName("name")[1].firstChild.nodeValue)

        hosts = []
        for i in parsedXmlOutput.firstChild.getElementsByTagName("hosts"):
            hosts.append(i.firstChild.nodeValue)
        excludedHosts = []
        for i in parsedXmlOutput.firstChild.getElementsByTagName("exclude_hosts"):
            excludedHosts.append(i.firstChild.nodeValue)


        print("Letrehozas idopontja: " + creationTime)
        print("Modositas idopontja: " + modificationTime)
        print("Letrehozo felhasznalo: " + owner)
        print("[1] Celpont megjegyzese: " + comment)
        print("[2] Celpont neve: " + name)
        print("[3] A celponthoz tartozo hostok: ")
        for i in hosts:
            print(i)
        print("[3] valamint a celponthoz tartozo kivetelek: ")
        for i in excludedHosts:
            print(i)

        end = False
        while not end:
            selection = (input(prefixString + "A modositashoz adja meg az attributum sorszamat. Kilepes: exit"))

            try:
                if selection == "exit":
                    end = True
                elif int(selection) == 1:
                    comment = input("Uj komment: ")
                    print(self.passCommandToOMP(" --xml='<modify_target target_id=\"" + targetUUID + "\"><comment>" + comment + "</comment></modify_target>'"))
                elif int(selection) == 2:
                    name = input("Uj nev: ")
                    print(self.passCommandToOMP(" --xml='<modify_target target_id=\"" + targetUUID + "\"><name>" + name + "</name></modify_target>'"))
                elif int(selection) == 3:
                    cmd = input(prefixString + "A modositassal a osszes korabbi celpont host es kivetel IP cime torlodik. Folytatja?\n[1] Igen\n[2] Nem")
                    if int(cmd) == 1:
                        print("Elso lepes: a hostok megadasa")
                        hosts = self.addHostsToTarget(prefixString)
                        print("Masodik lepes: a kivetelek megadasa")
                        excludedHosts = self.addHostsToTarget(prefixString)
                        print(self.passCommandToOMP(" --xml='<modify_target target_id=\"" + targetUUID + "\"><hosts>" + hosts + "</hosts><exclude_hosts>" + excludedHosts + "</exclude_hosts></modify_target>'"))
                        end = False
                    elif int(cmd) == 2:
                        print(prefixString + "Megszakitva.")
                    else:
                        print(prefixString + "Helytelen bevitel")
                else:
                    end = False
            except:
                print(prefixString + "Helytelen bevitel. Probalja ujra.")
                end = False
        return

    msg6 = "Portlistak kiirasa\t\t\t[1]\nPortlista adatai\t\t\t[2]\nPortlista letrehozasa\t\t[3]\nPortlista torlese\t\t\t[4]\nKilepes/megsem\t\t\t\t[exit]"
    def managePorts(self):
        prefixString = "<openvasController/managePorts> "
        end = False
        while (end == False):
            selectedPortIdx = -1
            try:
                print("\n" + prefixString + "\n" + self.msg6)
                command = input(prefixString + "Parancs:")
                command = command.upper()
                if (command == "EXIT"):
                    end = True
                elif (command == "1"):
                    self.getOpenVasPortLists()
                    input("Nyomjon ENTER-t a folytatashoz.")
                elif (command == "2"):
                    self.getOpenVasPortLists()
                    selectedPortIdx = int(input(prefixString + "Adja meg a portlista sorszamat: "))
                    if not (1 <= selectedPortIdx <= len(self.openvasPortList)):
                        print(prefixString + "Nem adott meg ervenyes sorszamot.")
                    else:
                        self.getSingleOpenVasPortList(self.openvasPortList[selectedPortIdx-1][0], True)
                    input("Nyomjon ENTER-t a folytatashoz.")
                elif (command == "3"):
                    id = self.createOpenVasPortList()
                    input("Nyomjon ENTER-t a folytatashoz.")
                elif (command == "4"):
                    self.getOpenVasPortLists()
                    selectedPortIdx = int(input(prefixString + "Adja meg a torlendo portlistat: "))
                    if not (1 <= selectedPortIdx <= len(self.openvasPortList)):
                        print(prefixString + "Nem adott meg ervenyes sorszamot.")
                    else:
                        self.deleteOpenVasPortList(self.openvasPortList[selectedPortIdx-1][0])
                    input("Nyomjon ENTER-t a folytatashoz.")
                else:
                    print(prefixString + "Nem adott meg ervenyes parancsot.")
                    #time.sleep(1)
            except ValueError as v:
                print("Hiba a bevitel soran: {0}".format(v))
                if selectedPortIdx is not int:
                    print("Nem szamot adott meg!")
                    if selectedPortIdx == "exit":
                        print("Exit parancs miatt kilepes!")
                        end = True
        return

    def getSingleOpenVasPortList(self, listID = None, printEnabled = True):
        if listID is None:
            print("Nem adott meg azonositot! Kilepes.")
            return
        elif len(self.openvasPortList) == 0:
            print("Ures/feltotletlen a portlista! Kilepes.")
            return
        else:
            response = self.passCommandToOMP(" -iX '<get_port_lists port_list_id=\"" + listID + "\"/>'")
            if str(response).__contains__("status=\"40"):
                print("A [" + listID+ "]-vel rendelkezo portlista nem letezik. Kilepes.")
                return
            else:
                xmlPortList = minidom.parseString(response)
                portList = xmlPortList.getElementsByTagName('port_list')[0]
                currentOVPorts = []

                id = portList.getAttribute('id')
                name = portList.getElementsByTagName('name')[1].firstChild.nodeValue
                writable = portList.getElementsByTagName('writable')[0].firstChild.nodeValue
                inUse = portList.getElementsByTagName('in_use')[0].firstChild.nodeValue
                allportCount = portList.getElementsByTagName('port_count')[0].getElementsByTagName('all')[0].firstChild.nodeValue
                tcpportCount = portList.getElementsByTagName('port_count')[0].getElementsByTagName('tcp')[0].firstChild.nodeValue
                udpportCount = portList.getElementsByTagName('port_count')[0].getElementsByTagName('udp')[0].firstChild.nodeValue
                currentOVPorts.append(id)
                currentOVPorts.append(name)
                currentOVPorts.append(writable)
                currentOVPorts.append(inUse)
                currentOVPorts.append(allportCount)
                currentOVPorts.append(tcpportCount)
                currentOVPorts.append(udpportCount)

                if printEnabled:
                    print("Lista ID:".ljust(20, ' ') + currentOVPorts[0])
                    print("Lista neve:".ljust(20, ' ') + currentOVPorts[1])
                    print("Irhato:".ljust(20, ' ') + self.numToBool(currentOVPorts[2]))
                    print("Hasznalatban van:".ljust(20, ' ') + self.numToBool(currentOVPorts[3]))
                    print("Portok szama:".ljust(20, ' ') + currentOVPorts[4])
                    print("TCP portok szama:".ljust(20, ' ') + currentOVPorts[5])
                    print("UDP portok szama:".ljust(20, ' ') + currentOVPorts[6] + "\n")

        return currentOVPorts

    def createOpenVasPortList(self, portList = None, listName = None, comment = None):

        if listName == None:
            listName = input("Adja meg a portlista nevet: ")
            if str(listName).upper() == 'EXIT':
                return False

        if comment == None:
            comment = input("Adja meg a megjegyzest: ")
            if str(comment).upper() == 'EXIT':
                return False

        if portList == None:
            print("Adja meg a portokat vesszovel elvalasztva es/vagy porttartomanyt kotojellel, majd nyomjon entert:")
            portListString = input()
            if str(portList).upper() == 'EXIT':
                return False
        else:
            portListString = ""
            for port in portList:
                portListString+= str(port + ",")
            # utolso vesszo eltavolitasa
            portListString = portListString[:-1]

        result = self.passCommandToOMP(" -iX '<create_port_list><name>" + listName + "</name><comment>" + comment + "</comment><port_range>" + portListString + "</port_range></create_port_list>'")
        if str(result).__contains__("status=\"40"):
            print((minidom.parseString(result)).childNodes[0].getAttribute('status_text'))
            print("Hiba a portlista megadasa soran! Kilepes.")
            return False
        else:
            id = (minidom.parseString(result)).childNodes[0].getAttribute('id')
            print("Sikeresen letrehozva a kovetkezo ID-vel: " + id)
            return id

    def deleteOpenVasPortList(self, id = None):
        if id == None:
            print("Nem adott meg torlendo portlistat! Kilepes.")
            return
        else:
            result = self.passCommandToOMP(" -iX '<delete_port_list port_list_id=\"" + id + "\"/>'")
            if str(result).__contains__("status=\"40"):
                print((minidom.parseString(result)).childNodes[0].getAttribute('status_text'))
                print("Hiba a portlista megadasa soran! Kilepes.")
                return False
            else:
                print("Portlista sikeresen torolve.")
        return

    def getOpenVasPortLists(self):
        response = self.passCommandToOMP(" -iX '<get_port_lists/>'")
        xmlPortList = minidom.parseString(response)
        portLists = xmlPortList.getElementsByTagName('port_list')

        currentOVPorts = []
        c = 0
        for portList in portLists:
            id = portList.getAttribute('id')
            name = portList.getElementsByTagName('name')[1].firstChild.nodeValue
            writable = portList.getElementsByTagName('writable')[0].firstChild.nodeValue
            inUse = portList.getElementsByTagName('in_use')[0].firstChild.nodeValue
            allportCount = portList.getElementsByTagName('port_count')[0].getElementsByTagName('all')[0].firstChild.nodeValue
            tcpportCount = portList.getElementsByTagName('port_count')[0].getElementsByTagName('tcp')[0].firstChild.nodeValue
            udpportCount = portList.getElementsByTagName('port_count')[0].getElementsByTagName('udp')[0].firstChild.nodeValue
            currentOVPorts.append([])
            currentOVPorts[c].append(id)
            currentOVPorts[c].append(name)
            currentOVPorts[c].append(writable)
            currentOVPorts[c].append(inUse)
            currentOVPorts[c].append(allportCount)
            currentOVPorts[c].append(tcpportCount)
            currentOVPorts[c].append(udpportCount)
            c += 1

        c = 1
        l = len(currentOVPorts)
        for portList in currentOVPorts:
            print(str(l) + "/" + str(c))
            print("Lista ID:".ljust(20, ' ') + portList[0])
            print("Lista neve:".ljust(20, ' ') + portList[1])
            print("Irhato:".ljust(20, ' ') + self.numToBool(portList[2]))
            print("Hasznalatban van:".ljust(20, ' ') + self.numToBool(portList[3]))
            print("Portok szama:".ljust(20, ' ') + portList[4])
            print("TCP portok szama:".ljust(20, ' ') + portList[5])
            print("UDP portok szama:".ljust(20, ' ') + portList[6] + "\n")
            c += 1

        self.openvasPortList = currentOVPorts

        return

    def numToBool(self, num, stringMode = True):
        if stringMode:
            if int(num) == 0:
                return "Nem"
            elif int(num) == 1:
                return "Igen"
            else:
                return "n/a"
        else:
            if int(num) == 0:
                return False
            elif int(num) == 1:
                return True
            else:
                return None

    nmapFileList = []
    def useNMAPScans(self):
        prefixString = "<openvasController/useNMAPScans> "
        nmapDateTimeInfo = []

        if not os.path.exists(self.nmapPath):
            print(prefixString + "Az NMAP munkakonyvtar nem letezik. Kilepes.\n")
            return False

        xmlFileList = glob.glob(self.nmapPath + "/*.xml")
        if xmlFileList == []:
            print(prefixString + "Az NMAP munkakonyvtar letezik, de nem talalhato benne XML scan.")
            return False
        else:
            for x in xmlFileList:
                self.nmapFileList.append(os.path.basename(x))
            for n in self.nmapFileList:
                nmapDateTimeInfo.append(self.getTimeDateInfoFromNMAPXml(n))

        end = False
        while (end == False):
            try:
                print("\n" + prefixString + "\n" + self.msg4)
                command = input(prefixString + "Parancs:")
                command = command.upper()
                if (command == "EXIT"):
                    end = True
                elif (command == "1"):
                    self.printNMAPDataList(prefixString, self.nmapFileList, nmapDateTimeInfo)
                    input("Nyomjon ENTER-t a folytatashoz.")
                elif (command == "2"):
                    self.printNMAPDataList(prefixString, self.nmapFileList, nmapDateTimeInfo)
                    selectedScanIdx = int(input(prefixString + "Adja meg az olvasando scan sorszamat: "))
                    if str(self.nmapFileList[int(selectedScanIdx)-1]).__contains__("port"):
                        self.readNMAPPortScanResult(xmlFileList[(int(selectedScanIdx)-1)], False)
                    elif str(self.nmapFileList[int(selectedScanIdx)-1]).__contains__("host"):
                        self.readNMAPHostScanResult(xmlFileList[(int(selectedScanIdx)-1)], False)
                    input("Nyomjon ENTER-t a folytatashoz.")
                elif (command == "3"):
                    self.printNMAPDataList(prefixString, self.nmapFileList, nmapDateTimeInfo)
                    selectedScanIdx = int(input(prefixString + "Adja meg az olvasando scan sorszamat: "))
                    if str(self.nmapFileList[int(selectedScanIdx) - 1]).__contains__("port"):
                        print(prefixString + "Port scant valasztott ki.")
                        nmapPortList = self.readNMAPPortScanResult(xmlFileList[(int(selectedScanIdx) - 1)], True)
                        if nmapPortList is False:
                            print(prefixString + "Valasszon masik fajlt!")
                            command = None
                        else:
                            portsToAdd = []
                            for item in nmapPortList:
                                portList = item[1]
                                for ports in portList:
                                    portsToAdd.append(ports[0])

                            """Portlista felvetel:"""
                            name = "fromNMAP-"
                            name += input("Adja meg az uj portlista nevet:")
                            self.createOpenVasPortList(portsToAdd, name)

                    elif str(self.nmapFileList[int(selectedScanIdx) - 1]).__contains__("host"):
                        print(prefixString + "Host scant valasztott ki.")
                        nmapHostList = self.readNMAPHostScanResult(xmlFileList[(int(selectedScanIdx) - 1)], True)
                        self.fullStackUsingNmap(nmapHostList)
                    input("Nyomjon ENTER-t a folytatashoz.")
                else:
                    print(prefixString + "Nem adott meg ervenyes parancsot")
                    #time.sleep(1)
            except ValueError as v:
                print("Hiba a bevitel soran: {0}".format(v))
                if selectedScanIdx is not int:
                    print("Nem szamot adott meg!")
                    if selectedScanIdx == "exit":
                        print("Exit parancs miatt kilepes!")
                        end = True

        return

    def readNMAPPortScanResult(self, path, makeList=False):
        DOMTree = minidom.parse(path)
        hosts = DOMTree.getElementsByTagName('host')
        try:
            results = []
            c = 0
            for host in hosts:
                # host-hoz tartozo alap infok:
                if len(host.getElementsByTagName('port')) != 0:
                    """Vagyis, van hozza tartozo relevans portinformacio"""
                    status = host.getElementsByTagName('status')[0].getAttribute('state')
                    ipaddr = host.getElementsByTagName('address')[0].getAttribute('addr')
                    if len(host.getElementsByTagName('address')) == 2:
                        macaddr = host.getElementsByTagName('address')[1].getAttribute('addr')
                    else:
                        macaddr = "n/a"
                    hostInfo = []
                    hostInfo.append(ipaddr)
                    hostInfo.append(macaddr)
                    hostInfo.append(status)

                    # host-hoz tartozo portok infoi:
                    portInfo = []
                    k = 0
                    foundports = host.getElementsByTagName('port')
                    for port in foundports:
                        portNumber = port.getAttribute('portid')
                        portState = port.getElementsByTagName('state')[0].getAttribute('state')
                        reason = port.getElementsByTagName('state')[0].getAttribute('reason')
                        portInfo.append([])
                        portInfo[k].append(portNumber)
                        portInfo[k].append(portState)
                        portInfo[k].append(reason)
                        k += 1

                    results.append([])
                    results[c].append(hostInfo)
                    results[c].append(portInfo)
                    c += 1

                for result in results:
                    print("HOST IP:".ljust(25, ' ') + "HOST MAC:".ljust(25, ' ') + "ALLAPOT:".ljust(25, ' '))
                    print(str(result[0][0]).ljust(25, ' ') + str(result[0][1]).ljust(25, ' ') + str(result[0][2]).ljust(25, ' '))

                    print("\nPORTSZAM:".ljust(25, ' ') + "ALLAPOT:".ljust(25, ' ') + "INDOK:".ljust(25, ' '))
                    for foundPorts in result[1]:
                        print(str(foundPorts[0]).ljust(25, ' ') + str(foundPorts[1]).ljust(25, ' ') + str(foundPorts[2]).ljust(25, ' '))
                    print("********************************************************************************")

            if makeList:
                return results
            else:
                return hosts
        except:
            print("Hiba tortent a beolvasas soran! Megszakitva.")
            pass
        return False

    def readNMAPHostScanResult(self, path, makeList = False):
        """Ha a makeList = True, akkor felepit es visszaad egy listat, 1: state, 2: IP addr. Egyebkent az XML-t domtree-t adja vissza"""
        DOMTree = minidom.parse(path)
        hosts = DOMTree.getElementsByTagName('host')

        if not makeList:
            for host in hosts:
                status = host.childNodes[0].getAttribute('state')
                ipaddr = host.childNodes[2].getAttribute('addr')
                macaddr = host.childNodes[4].getAttribute('addr')
                vendor = host.childNodes[4].getAttribute('vendor')
                print(status + " " + " " + ipaddr + " " + " " + macaddr + " " + vendor)
            return hosts
        else:
            num = 0
            nmapHostList = []
            for host in hosts:
                status = host.childNodes[0].getAttribute('state')
                ipaddr = host.childNodes[2].getAttribute('addr')
                macaddr = host.childNodes[4].getAttribute('addr')
                vendor = host.childNodes[4].getAttribute('vendor')
                print(status + " " + " " + ipaddr + " " + " " + macaddr + " " + vendor)

                nmapHostList.append([])
                nmapHostList[num].append(status)
                nmapHostList[num].append(ipaddr)
                num += 1
            return nmapHostList
        return

    def getTimeDateInfoFromNMAPXml(self, filename):
        s = str(filename).split('-')
        time = s[1]
        formattedTime = time[:2] + ":" + time[2:4] + ":" + time[4:6]
        date = (s[2].split('.'))[0]
        formattedDate = "20" + date[4:6] + "." + date[:2] + "." + date[2:4]
        result = formattedDate + ", " + formattedTime
        return result

    def printNMAPDataList(self, prefixString, nmapFileList, nmapDateTimeInfo):
        print(prefixString + "NMAP scanfile-ok:")
        print("SORSZAM\tTIPUS\tDATUM\tFAJLNEV")

        for i in range(len(self.nmapFileList)):
            type = ""
            if str(self.nmapFileList[i]).__contains__("host"):
                type = "host scan"
            elif str(self.nmapFileList[i]).__contains__("port"):
                type = "host es portscan"
            print("[" + str(i + 1) + "]" + "\t" + type + "\t" + nmapDateTimeInfo[i] + "\t" + nmapFileList[i])

        return

    def printOpenVASDataList(self, prefixString, openVASFileList, openVASDateTimeInfo):
        print(prefixString + "OpenVAS scanfile-ok:")
        print("SORSZAM\tTIPUS\tDATUM\tFAJLNEV")

        type = "normal"

        for i in range(len(self.openVASFileList)):
            print("[" + str(i + 1) + "]" + "\t" + type + "\t" + openVASDateTimeInfo[i] + "\t" + openVASFileList[i])

        return

    def fullStackUsingNmap(self, nmapHostList = None, excludeList = None):
        prefixString = "<useNMAPScans/fullStackUsingNmap> "
        #select a scan, pass hostlist to create target. ez megtortenik hivas elott, mert eleve a hostlist-et kerem be

        #create target from hostlist +NAME:nmap.
        #TODO: datum legyen benne
        targetName = "fromNMAP-"
        s = str(input(prefixString + "Adja meg a celpont nevet: fromNMAP-"))
        targetName += s
        targetUUID = self.createNewTarget(nmapHostList, targetName, excludeList)
        if targetUUID != "":
            print(prefixString + "A celpont letrejott a kovetkezo UUID-val: " + targetUUID)
        else:
            print(prefixString + "Celpont letrehozas sikertelen! Kilepes.")
            return

        #create task + bind target to it
        taskName = "fromNMAP-"
        s = str(input(prefixString + "Adja meg a feladat nevet: fromNMAP-"))
        taskName += s
        taskUUID = self.createNewTask(None, targetUUID, taskName, "NMAP scan alapjan letrehozva.")
        if targetUUID != "":
            print(prefixString + "A feladat letrejott a kovetkezo UUID-val: " + taskUUID)
        else:
            print(prefixString + "Celpont letrehozas sikertelen! Kilepes.")
            return

        return

    def saveScanResults(self, data, fileLoc = None, fileName = None, fileExt = ".xml"):
        """Timeformat az NMAP time outputhoz igazitva."""
        fileHeader = ""
        if fileExt == ".xml":
            fileHeader = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        if fileLoc == None:
            fileLoc = self.openVASWorkDirPath
        if fileName == None:
            fileName = "openvas-"
        fileName += time.strftime("%H%M%S") + "-" + time.strftime("%m%d%y")
        fullPath = fileLoc+fileName+fileExt
        fileObject = open(fullPath, 'w')
        fileObject.write(fileHeader + data)
        fileObject.close()
        return fullPath

    msg5 = "OpenVAS scan-ek listazasa \t\t\t[1]\nOpenVAS scan olvasasa\t\t\t\t[2]\nSerulekenyseg olvasasa scan-bol\t\t[3]\nKilepes/megsem\t\t\t\t\t[exit]"
    openVASFileList = []
    def manageScanResults(self):
        prefixString = "<openvasController/manageScanResults> "
        openVASDateTimeInfo = []

        if not os.path.exists(self.openVASWorkDirPath):
            print(prefixString + "Az OpenVAS munkakonyvtar nem letezik. Kilepes.\n")
            return False

        xmlFileList = glob.glob(self.openVASWorkDirPath + "/*.xml")
        xmlFileList += glob.glob(self.openVASWorkDirPath + "/*.xml.gz")
        if xmlFileList == []:
            print(prefixString + "Az OpenVAS munkakonyvtar letezik, de nem talalhato benne XML scan.")
            return False
        else:
            for x in xmlFileList:
                self.openVASFileList.append(os.path.basename(x))
            for o in self.openVASFileList:
                openVASDateTimeInfo.append(self.getTimeDateInfoFromNMAPXml(o))

        end = False
        while (end == False):
            try:
                print("\n" + prefixString + "\n" + self.msg5)
                command = input(prefixString + "Parancs:")
                command = command.upper()
                if (command == "EXIT"):
                    end = True
                elif (command == "1"):
                    self.printOpenVASDataList(prefixString, self.openVASFileList, openVASDateTimeInfo)
                    input("Nyomjon ENTER-t a folytatashoz.")
                elif (command == "2"):
                    self.printOpenVASDataList(prefixString, self.openVASFileList, openVASDateTimeInfo)
                    selectedScanIdx = int(input(prefixString + "Adja meg az olvasando scan sorszamat: "))

                    """Ketszeres vedelem, nem csak xml es xml.gz fileokat olvasunk fel, de scak azokat engedjuk kiirni"""
                    if str(self.openVASFileList[selectedScanIdx-1]).endswith(".xml"):
                        selectedFile = open(self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx-1], 'r')
                        for lines in selectedFile:
                            print(selectedFile.readline())
                        selectedFile.close()

                    elif str(self.openVASFileList[selectedScanIdx-1]).endswith(".xml.gz"):
                        """1. Tomoritett fajlt talaltunk, kitomorites"""
                        print(prefixString + "A fajl kitomoritese elkezdodott. Kerem, varjon.")
                        decompressSuccess = self.decompressWithGZIP(self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx-1])
                        if decompressSuccess:
                            """2. Sikerult a kitomorites, kiiras kepernyore."""
                            print(prefixString + "Kitomorites befejezve!")
                            """Ezen a ponton mar biztosan letezik egy .gz nelkuli kitomoritett fajl"""
                            selectedFile = (self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx - 1]).rstrip('.gz')
                            if str(selectedFile).endswith(".xml"):
                                selectedFile = open((self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx - 1]).rstrip('.gz'),'r')
                                for lines in selectedFile:
                                    print(selectedFile.readline())
                                selectedFile.close()
                            input("Nyomjon ENTER-t a folytatashoz.")
                            """3. Befejezodott a kiiras, a text file torlese"""
                            fullPath = self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx-1]
                            os.remove(fullPath.rstrip('.gz'))

                elif (command == "3"):
                    self.printOpenVASDataList(prefixString, self.openVASFileList, openVASDateTimeInfo)
                    selectedScanIdx = int(input(prefixString + "Adja meg az olvasando scan sorszamat: "))

                    if str(self.openVASFileList[selectedScanIdx-1]).endswith(".xml"):
                        """Ebben az esetben minden marad a regiben, mert csak egy xml-t talaltunk"""
                        self.analyzeScanResult(xmlFileList[(int(selectedScanIdx) - 1)], prefixString, False)

                    elif str(self.openVASFileList[selectedScanIdx-1]).endswith(".xml.gz"):
                        """1. Tomoritett fajlt talaltunk, kitomorites"""
                        print(prefixString + "A fajl kitomoritese elkezdodott. Kerem, varjon.")
                        decompressSuccess = self.decompressWithGZIP(self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx-1])
                        if decompressSuccess:
                            """2. Sikerult a kitomorites, a fajlt at kell adni a DomTree-nek"""
                            print(prefixString + "Kitomorites befejezve!")
                            """Ezen a ponton mar biztosan letezik egy .gz nelkuli kitomoritett fajl"""
                            selectedFile = (self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx - 1]).rstrip('.gz')
                            if str(selectedFile).endswith(".xml"):
                                self.analyzeScanResult(selectedFile, prefixString, False)
                            input("Nyomjon ENTER-t a folytatashoz.")
                            """3. Befejezodott a kiiras, a text file torlese"""
                            fullPath = self.openVASWorkDirPath + self.openVASFileList[selectedScanIdx-1]
                            os.remove(fullPath.rstrip('.gz'))

                    #self.analyzeScanResult(xmlFileList[(int(selectedScanIdx) - 1)], prefixString, False)

                    input("Nyomjon ENTER-t a folytatashoz.")
                else:
                    print(prefixString + "Nem adott meg ervenyes parancsot")
                    #time.sleep(1)
            except ValueError as v:
                print("Hiba a bevitel soran: {0}".format(v))
                if selectedScanIdx is not int:
                    print("Nem szamot adott meg!")
                    if selectedScanIdx == "exit":
                        print("Exit parancs miatt kilepes!")
                        end = True

        return

    def analyzeScanResult(self, path, prefixString, makeList=False):
        """Ha a makeList = True, akkor fajlba irja az eredmenyeket. Egyebkent kepernyore ir."""
        DOMTree = minidom.parse(path)
        #reportCount = DOMTree.getElementsByTagName('report_count').item(0).firstChild.nodeValue
        #reportCount = int(str(reportCount).rstrip('\n'))
        reportChildrenFromDOM = DOMTree.getElementsByTagName('report')
        reportCount = len(reportChildrenFromDOM)-1 # az elso csak egy "ures" osszefoglalo

        severities = []
        scanStatuses = []
        vulnCounts = []
        associatedTask = []
        foundPorts = []
        scanResults = []

        print(prefixString + "Anilizis elinditva, kerem varjon.")
        try:
            safetyCounter = 0
            for reportItem in reversed(reportChildrenFromDOM):
                """Severity ertekek lekerdezese"""
                severity = reportItem.getElementsByTagName('severity_range')
                num = 0
                for s in severity:
                    sname = s.getElementsByTagName('name')[0].childNodes[0].nodeValue
                    smin = float(s.getElementsByTagName('min')[0].childNodes[0].nodeValue)
                    smax = float(s.getElementsByTagName('max')[0].childNodes[0].nodeValue)
                    severities.append([])
                    severities[num].append(sname)
                    severities[num].append(smin)
                    severities[num].append(smax)
                    num +=1

                """Scan statuszok lekerdezese"""
                statuses = reportItem.getElementsByTagName('scan_run_status')
                num = 0
                for s in statuses:
                    state = s.firstChild.nodeValue
                    scanStatuses.append([])
                    scanStatuses[num].append(state)
                    num +=1

                """Talalt serulekenyseg fajtak szamanak lekerdezese"""
                vulns = reportItem.getElementsByTagName('vulns')
                num = 0
                for v in vulns:
                    if v.getElementsByTagName('count')[0].childNodes[0] is not None:
                        vulnCount = v.getElementsByTagName('count')[0].childNodes[0].nodeValue
                    else:
                        vulnCount = "n/a"
                    vulnCounts.append([])
                    vulnCounts[num].append(vulnCount)
                    num +=1

                """Asszocialt feladat adatainak lekerdezese"""
                tasks = reportItem.getElementsByTagName('task')
                num = 0
                for t in tasks:
                    if t.hasAttribute('id') == True:
                        tname = t.getElementsByTagName('name')[0].childNodes[0].nodeValue
                        tcomment = t.getElementsByTagName('comment')[0].childNodes[0].nodeValue
                        tTargetId = t.getElementsByTagName('target')[0].getAttribute('id')
                        associatedTask.append([])
                        associatedTask[num].append("Nev: " + tname)
                        associatedTask[num].append("Megjegyzes: " + tcomment)
                        associatedTask[num].append("Celpont ID: " + tTargetId)
                        num +=1

                """Serulekeny portok adatainak lekerdezese"""
                ports = reportItem.getElementsByTagName('ports')
                num = 0
                for p in ports:
                    pnode = p.getElementsByTagName('port')
                    for n in pnode:
                        pname = str(n.firstChild.nodeValue).rpartition('\n')[0]
                        host = n.getElementsByTagName('host')[0].childNodes[0].nodeValue
                        severity = n.getElementsByTagName('severity')[0].childNodes[0].nodeValue
                        threat = n.getElementsByTagName('threat')[0].childNodes[0].nodeValue #TODO: fix threatvalue
                        foundPorts.append([])
                        foundPorts[num].append(pname)
                        foundPorts[num].append(host)
                        foundPorts[num].append(severity)
                        foundPorts[num].append(threat)
                        num +=1

                """Talalt serulekenysegek lekerdezese"""
                results = reportItem.getElementsByTagName('results')
                num = 0
                for node in results:
                    rnode = node.getElementsByTagName('result')
                    for r in rnode:
                        if r.hasAttribute('id') == True:
                            """Alapveto result adatok lekerese"""
                            resultId = r.getAttribute('id')
                            rName = r.getElementsByTagName('name')[0].firstChild.nodeValue
                            rCreationTime = r.getElementsByTagName('creation_time')[0].firstChild.nodeValue
                            rHost = r.getElementsByTagName('host')[0].firstChild.nodeValue
                            rPort = r.getElementsByTagName('port')[0].firstChild.nodeValue

                            """NVT adatok lekerese"""
                            nvt = r.getElementsByTagName('nvt')
                            for n in nvt:
                                if n.getElementsByTagName('name')[0].firstChild is not None:
                                    nvtName = n.getElementsByTagName('name')[0].firstChild.nodeValue
                                else:
                                    nvtName = "n/a"
                                if n.getElementsByTagName('family')[0].firstChild is not None:
                                    nvtFamily = n.getElementsByTagName('family')[0].firstChild.nodeValue
                                else:
                                    nvtFamily = "n/a"
                                if n.getElementsByTagName('cvss_base')[0].firstChild is not None:
                                    nvtCvssBaseScore = n.getElementsByTagName('cvss_base')[0].firstChild.nodeValue
                                else:
                                    nvtCvssBaseScore = "n/a"
                                if n.getElementsByTagName('cve')[0].firstChild is not None:
                                    assoiciatedCVE = n.getElementsByTagName('cve')[0].firstChild.nodeValue
                                else:
                                    assoiciatedCVE = "n/a"
                                if n.getElementsByTagName('bid')[0].firstChild is not None:
                                    assoiciatedBID = n.getElementsByTagName('bid')[0].firstChild.nodeValue
                                else:
                                    assoiciatedBID = "n/a"
                                if n.getElementsByTagName('xref')[0].firstChild is not None:
                                    externalReference = n.getElementsByTagName('xref')[0].firstChild.nodeValue
                                else:
                                    externalReference = "n/a"
                                if n.getElementsByTagName('tags')[0].firstChild is not None:
                                    tags = n.getElementsByTagName('tags')[0].firstChild.nodeValue
                                else:
                                    tags = "n/a"

                            """Veszelyesseg, pontossag lekerese"""
                            if r.getElementsByTagName('threat')[0].firstChild is not None:
                                rThreat = r.getElementsByTagName('threat')[0].firstChild.nodeValue
                            else:
                                rThreat = "n/a"
                            if r.getElementsByTagName('severity')[0].firstChild is not None:
                                rSeverity = r.getElementsByTagName('severity')[0].firstChild.nodeValue
                            else:
                                rSeverity = "n/a"

                            rQOD = r.getElementsByTagName('qod')[0]
                            if rQOD.getElementsByTagName('value')[0].firstChild is not None:
                                rQuallityOfDetectionValue = rQOD.getElementsByTagName('value')[0].firstChild.nodeValue
                            else:
                                rQuallityOfDetectionValue = "n/a"
                            if rQOD.getElementsByTagName('type')[0].firstChild is not None:
                                rDetectionType = rQOD.getElementsByTagName('type')[0].firstChild.nodeValue
                            else:
                                rDetectionType = "n/a"

                            """Leiras lekerese"""
                            if r.getElementsByTagName('description')[0].firstChild is not None:
                                rDesctiption = r.getElementsByTagName('description')[0].firstChild.nodeValue
                            else:
                                rDesctiption = "n/a"

                            scanResults.append([])
                            scanResults[num].append(resultId)
                            scanResults[num].append(rName)
                            scanResults[num].append(rCreationTime)
                            scanResults[num].append(rHost)
                            scanResults[num].append(rPort)

                            scanResults[num].append(nvtName)
                            scanResults[num].append(nvtFamily)
                            scanResults[num].append(nvtCvssBaseScore)
                            scanResults[num].append(assoiciatedCVE)
                            scanResults[num].append(assoiciatedBID)
                            scanResults[num].append(externalReference)
                            scanResults[num].append(tags)

                            scanResults[num].append(rThreat)
                            scanResults[num].append(rSeverity)
                            scanResults[num].append(rQuallityOfDetectionValue)
                            scanResults[num].append(rDetectionType)
                            scanResults[num].append(rDesctiption)

                            num += 1

                safetyCounter+=1
                if safetyCounter == reportCount:
                    """Erre azert van szukseg, mert tobb report element is szerepel azonoskent a DOM-ban"""
                    break
        except AttributeError as a:
            print("Hiba a beolvasas soran: {0}".format(a))
        print(prefixString + "Analizis kesz!")

        message = prefixString + "\nRovid osszefoglalo kiirasa \t[1]\nEredmeny reszletezese\t[2]\nEredmeny fajlba irasa\t[3]"
        print(message)
        if makeList == False:
            c = input("Adja meg az listazasi modot:")
            if (c == "1" or c =="2"):

                print("\nSulyossagi index:")
                s = "Szint\t\tMin\t\tMax\n"
                for i in range(len(severities)):
                    for j in range(len(severities[i])):
                        s+= (str(severities[i][j]) + "\t\t")
                    s+="\n"
                print(s, end="")

                for i in range(reportCount):
                    print("Riport: " + str(reportCount) + "/" + str(i+1))

                    for s in scanStatuses[i]:
                        print("\nScan statusz: " + str(s))

                    for v in vulnCounts[i]:
                        print("\nTalalt serulekenysegek (differencialt):" + str(v))

                    print("\nAsszocialt OpenVAS feladat:", end="")
                    for j in range(len(associatedTask[i])):
                        print(associatedTask[i][j])

                    print("\nSerulekeny portok:\nPort\t\tHost IP:\t\tSulyossagi index:\t\tFenyegetesi index:")
                    for j in range(len(foundPorts)):
                        print(foundPorts[j][0] + "\t\t" + foundPorts[j][1] + "\t\t" + foundPorts[j][2] + "\t\t" + foundPorts[j][3])
                        if j % 10 == 0:
                            cmd = input("Nyomjon ENTER-t a listazas folytatashoz, vagy 'exit' a megszakitashoz.")
                            if str(cmd).upper() == 'EXIT':
                                break

                    """Ide csak akkor lepunk be, ha a felhasznalo reszletes leirast kert."""
                    if c == "2":
                        resultCount = len(scanResults)
                        for j in range(len(scanResults)):
                            print("********************************************************************************")
                            print("\nRiport: " + str(resultCount) + "/" + str(j + 1) + "\n")
                            print("Eredmeny ID: " + scanResults[j][0])
                            print("Nev: " + scanResults[j][1])
                            print("Letrehozas datuma: " + scanResults[j][2])
                            print("Asszocialt host: " + scanResults[j][3])
                            print("Asszocialt port: " + scanResults[j][4])

                            print("NVT nev: " + scanResults[j][5])
                            print("NVT csalad: " + scanResults[j][6])
                            print("NVT CVSS ertek: " + scanResults[j][7])
                            print("Asszocialt CVE: " + scanResults[j][8])
                            print("Asszocialt BID: " + scanResults[j][9])
                            print("Kulso hivatkozas: " + scanResults[j][10])

                            print("\nLeiras: " + scanResults[j][11] + "\n")

                            print("Fenyegetesi index: " + scanResults[j][12])
                            print("Veszelyessegi index: " + scanResults[j][13])
                            print("Vizsgalat pontossaga: " + scanResults[j][14])
                            print("Vizsgalat tipusa: " + scanResults[j][15])
                            print("Vizsgalat leirasa: " + scanResults[j][16])
                            if j % 10 == 0:
                                cmd = input("Nyomjon ENTER-t a listazas folytatashoz, vagy 'exit' a megszakitashoz.")
                                if str(cmd).upper() == 'EXIT':
                                    break
            elif (c == "3"):
                print(prefixString + "A fajlba iras elkezdodott. Kerem, varjon.")
                fileText = ""
                fileText+= "\nSulyossagi index:" + "\n"
                fileText += "Szint\t\tMin\t\tMax\n"
                for i in range(len(severities)):
                    for j in range(len(severities[i])):
                        fileText += (str(severities[i][j]) + "\t\t")
                    fileText += "\n"

                for i in range(reportCount):
                    fileText += "\nRiport: " + str(reportCount) + "/" + str(i + 1) + "\n"

                    for s in scanStatuses[i]:
                        fileText += "Scan statusz: " + str(s) + "\n"

                    for v in vulnCounts[i]:
                        fileText += "Talalt serulekenysegek (differencialt):" + str(v) + "\n"

                    fileText +="\nAsszocialt OpenVAS feladat:" + "\n"
                    for j in range(len(associatedTask[i])):
                        fileText += associatedTask[i][j] + "\n"

                    fileText += "\nSerulekeny portok:\nPort\t\t\t\tHost IP:\t\tSulyossagi index:\t\tFenyegetesi index:" + "\n"
                    for j in range(len(foundPorts)):
                        fileText += str(foundPorts[j][0]).ljust(25, ' ') + str(foundPorts[j][1]).ljust(25,' ') + str(foundPorts[j][2]).ljust(15,' ') + str(foundPorts[j][3]).ljust(15,' ') + "\n"

                    resultCount = len(scanResults)
                    for j in range(len(scanResults)):
                        fileText += "********************************************************************************" + "\n"
                        fileText += "\nRiport: " + str(resultCount) + "/" + str(j + 1) + "\n"
                        fileText += "Eredmeny ID: " + scanResults[j][0] + "\n"
                        fileText += "Nev: " + scanResults[j][1] + "\n"
                        fileText += "Letrehozas datuma: " + scanResults[j][2] + "\n"
                        fileText += "Asszocialt host: " + scanResults[j][3] + "\n"
                        fileText += "Asszocialt port: " + scanResults[j][4] + "\n"

                        fileText += "NVT nev: " + scanResults[j][5] + "\n"
                        fileText += "NVT csalad: " + scanResults[j][6] + "\n"
                        fileText += "NVT CVSS ertek: " + scanResults[j][7] + "\n"
                        fileText += "Asszocialt CVE: " + scanResults[j][8] + "\n"
                        fileText += "Asszocialt BID: " + scanResults[j][9] + "\n"
                        fileText += "Kulso hivatkozas: " + scanResults[j][10] + "\n"

                        fileText += "\nLeiras: " + scanResults[j][11] + "\n"

                        fileText += "Fenyegetesi index: " + scanResults[j][12] + "\n"
                        fileText += "Veszelyessegi index: " + scanResults[j][13] + "\n"
                        fileText += "Vizsgalat pontossaga: " + scanResults[j][14] + "\n"
                        fileText += "Vizsgalat tipusa: " + scanResults[j][15] + "\n"
                        fileText += "Vizsgalat leirasa: " + scanResults[j][16] + "\n"

                fullPath = self.saveScanResults(fileText, None, "analizis-", ".txt")
                print(prefixString + "Fajlba iras befejezbe!")

                print(prefixString + "A fajl tomoritese elkezdodott. Kerem, varjon.")
                compressSuccess = self.compressWithGZIP(fullPath)
                if (compressSuccess):
                    print(prefixString + "Tomorites befejezbe!")
                    delete = input(prefixString + "Torli a felesleges, tomoritetlen fajlt?\n[1]\tIgen\n[2]\tNem")
                    if delete == "1":
                        os.remove(fullPath)
                    else:
                        print(prefixString + "Torles mellozve.")

            else:
                print(prefixString + "Nem adott meg ervenyes parancsot. Kilepes.")

        return

    def compressWithGZIP(self, fullPath):
        """Ha a hiba tortent: return False, vagyis a tomoritendo fajlt nem engedje torolni a muvelet vegen."""
        try:
            with open(fullPath, 'rb') as f_in:
                with gzip.open(fullPath + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return True
        except IOError as e:
            print("Hiba tortent a tomorites soran: {0}".format(e))
            return False
        except OSError as e:
            print("Hiba tortent a tomorites soran: {0}".format(e))
            return False
        return

    def decompressWithGZIP(self, fullPath):
        """Ha a hiba tortent: return False, vagyis a tomoritendo fajlt nem engedje torolni a muvelet vegen."""
        try:
            inFile = gzip.open(fullPath, 'rb')
            outFile = open(fullPath.rstrip('.gz'), 'wb')
            outFile.write(inFile.read())
            inFile.close()
            outFile.close()
            return True
        except IOError as e:
            print("Hiba tortent a tomoritett fajl olvasasa soran: {0}".format(e))
            return False
        except OSError as e:
            print("Hiba tortent a tomoritett fajl olvasasa soran: {0}".format(e))
            return False
        return