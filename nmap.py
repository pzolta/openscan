# -*- coding: latin-1 -*-
import os
import subprocess
import time
from xml.dom import minidom
from IPy import IP
#Kulon telepiteni kell az IPy 0.83-at hozza! site: https://pypi.python.org/pypi/IPy/

class nmap(object):
    """nmap-et kezelo osztaly"""
    msg1 = "A futo NMAP vizsgalatokat barmikor megszakithatja a [CTRL + C] billentyukombinacioval."
    msg2 = "Allomas felderites\t\t[1]\nKapuletapogatas\t\t\t[2]\nKozvetlen iranyitas\t\t[3]\nKilepes:\t\t\t\t[exit]"
    msg3 = "Visszhang letapogato vizsgalatok:\nICMP echo, TCP/80\t\t\t\t[1]\nTCP SYN echo [kapulista]\t\t[2]\nTCP ACK echo\t\t\t\t\t[3]\nUDP echo\t\t\t\t\t\t[4]\nICMP ping/timestamp/mask echo\t[5]\nIPProto echo\t\t\t\t\t[6]\nARP echo\t\t\t\t\t\t[7]\nKilepes\t\t\t\t\t\t\t[exit]"
    msg4 = "Kozvetlen iranyitas. Kilepes: [exit]"
    msg5 = "Kapuletapogato vizsgalatok:\nTCP SYN letapogatas\t\t\t\t[1]\nTCP connect letapogatas\t\t\t[2]\nUDP letapogatas\t\t\t\t\t[3]\nTCP null/fin/xmas letapogatas\t[4]\nMaimon letapogatas\t\t\t\t[5]\nIPProto letapogatas\t\t\t\t[6]\nFTP bounce tamadas\t\t\t\t[7]\nKilepes\t\t\t\t\t\t\t[exit]"
    nmapWorkDirPath = ""

    def __init__(self):
        """Teendok, mielott a scanneles lefutna"""
        self.createNmapDir()
        return

    def createNmapDir(self, path=os.getcwd()):
        strPath = str(path)
        try:
            if not os.path.exists(strPath + "/NmapScans"):
                os.makedirs(strPath + "/NmapScans")

            self.nmapWorkDirPath = strPath + "/NmapScans/"
        except OSError as e:
            print("Hiba tortent az NMAP munkakonyvtar letrehozasa soran: {0}".format(e))
        return

    def nmapController(self):
        prefixString = "<nmapController> "
        print("\n" + self.msg1)
        end = False
        while (end == False):
            print(prefixString + "\n" + self.msg2)
            command = input(prefixString + "Parancs:")
            command = command.upper()
            if (command == "EXIT"):
                end = True
            elif (command == "1"):
                self.discoverHosts()
            elif (command == "2"):
                self.portScan()
            elif (command == "3"):
                self.freeRun()
            else:
                print(prefixString + "Nem adtal meg ervenyes parancsot")
                #time.sleep(1)
        return

    def passCommandToNMAP(self, command, fileName=""):
        """Atadja az input parancsot az NMAP CLI-nek, minden esetben fajlt ment, datummal, folytathato feladatot indit"""
        output = subprocess.getoutput("nmap " + command + " -oA " + self.nmapWorkDirPath + fileName + "-%T-%D")
        return output

    def passRawCommandToNMAP(self, command):
        """Atadja az input parancsot az NMAP CLI-nek. A teljes kontroll a felhasznaloe, semmilyen beallitast nem tesz a program az 'nmap' prefixen kivul"""
        output = subprocess.getoutput("nmap " + command)
        return output

    def printList(self, list):
        for i in list:
            print(i)
        return

    commandToSchedule = None
    fileNamePrefixForSchedule = None
    #TODO: ide is kellene IP cim vizsgalat
    def discoverHosts(self, operateRemotely = False):
        #print("\n"*120)
        prefixString = "<nmapController/discoverHosts> "
        fileNamePrefix = "host"

        end = False
        while (end == False):
            try:
                if not operateRemotely:
                    print("\n" + prefixString + "\n" + self.msg3)
                    command = input(prefixString + "Parancs:")
                    command = command.upper()
                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn", fileNamePrefix))
                        input("Nyomjon ENTER-t a folytatashoz.")
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(prefixString + "Az alapertelmezett port: [80]. Ha mast szeretne hasznalni, szokoz nelkul, vesszo es kotojel segitsegevel adhatja meg azokat. ")
                        ports = str(input(prefixString + "Adja meg a portokat (ENTER az alapertelmezetthez)"))
                        #print(self.passCommandToNMAP(target + " -sn -PS", fileNamePrefix) + ports)
                        print(self.passCommandToNMAP(target + " -sn -PS" + ports, fileNamePrefix))
                        input("Nyomjon ENTER-t a folytatashoz.")
                    elif (command == "3"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(prefixString + "Portokat szokoz nelkul, vesszo es kotojel segitsegevel adhat meg. ")
                        ports = str(input(prefixString + "Adja meg a portokat (ENTER az alapertelmezetthez)"))
                        #print(self.passCommandToNMAP(target + " -sn -PA", fileNamePrefix) + ports)
                        print(self.passCommandToNMAP(target + " -sn -PA" + ports, fileNamePrefix))
                        input("Nyomjon ENTER-t a folytatashoz.")
                    elif (command == "4"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(prefixString + "Az alapertelmezett port: [31338]. Ha mast szeretne hasznalni, szokoz nelkul, vesszo es kotojel segitsegevel adhatja meg azokat. ")
                        ports = str(input(prefixString + "Adja meg a portokat (ENTER az alapertelmezetthez)"))
                        #print(self.passCommandToNMAP(target + " -sn -PU", fileNamePrefix) + ports)
                        print(self.passCommandToNMAP(target + " -sn -PU" + ports, fileNamePrefix))
                        input("Nyomjon ENTER-t a folytatashoz.")
                    elif (command == "5"):
                        self.askForICMPEchos()
                        if not end:
                            input("Nyomjon ENTER-t a folytatashoz.")
                    elif (command == "6"):
                        print(prefixString + "Az alapertelmezett protokollok:\t1 (ICMP), 2 (IGMP), 3 (IP-in-IP)")
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PO", fileNamePrefix))
                        input("Nyomjon ENTER-t a folytatashoz.")
                    elif (command == "7"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PR", fileNamePrefix))
                        input("Nyomjon ENTER-t a folytatashoz.")
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")
                        #time.sleep(1)
                else:
                    self.commandToSchedule = ""
                    self.fileNamePrefixForSchedule = fileNamePrefix

                    print("\n" + prefixString + "\n" + self.msg3)
                    command = input(prefixString + "Parancs:")
                    command = command.upper()
                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        #print(self.passCommandToNMAP(target + " -sn", fileNamePrefix))
                        self.commandToSchedule = (target + " -sn")
                        return True
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(prefixString + "Az alapertelmezett port: [80]. Ha mast szeretne hasznalni, szokoz nelkul, vesszo es kotojel segitsegevel adhatja meg azokat. ")
                        ports = str(input(prefixString + "Adja meg a portokat (ENTER az alapertelmezetthez)"))
                        self.commandToSchedule = (target + " -sn -PS" + ports)
                        return True
                    elif (command == "3"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(prefixString + "Portokat szokoz nelkul, vesszo es kotojel segitsegevel adhat meg. ")
                        ports = str(input(prefixString + "Adja meg a portokat (ENTER az alapertelmezetthez)"))
                        self.commandToSchedule = (target + " -sn -PA" + ports)
                        return True
                    elif (command == "4"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(prefixString + "Az alapertelmezett port: [31338]. Ha mast szeretne hasznalni, szokoz nelkul, vesszo es kotojel segitsegevel adhatja meg azokat. ")
                        ports = str(input(prefixString + "Adja meg a portokat (ENTER az alapertelmezetthez)"))
                        self.commandToSchedule = (target + " -sn -PU" + ports)
                        return True
                    elif (command == "5"):
                        self.askForICMPEchos(operateRemotely=True)
                        return True
                    elif (command == "6"):
                        print(prefixString + "Az alapertelmezett protokollok:\t1 (ICMP), 2 (IGMP), 3 (IP-in-IP)")
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PO")
                        return True
                    elif (command == "7"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PR")
                        return True
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")
            except (KeyboardInterrupt, SystemExit):
                # ne lepjen ki a ciklusbol, csak az esetleges folyamatok allnak le (nmap ctrl+C) miatt
                # alapertelmezesek visszaallitasa
                command = None
                print(prefixString + "Megszakitva.")
                pass
        return

    def askForICMPEchos(self, operateRemotely = False):
        prefixString = "<discoverHosts/askForICMPEchos> "
        fileNamePrefix = "host"
        print("\n" + prefixString + "Valassza ki, mely keresek keruljenek elkuldesre. Tobbet is megadhat egyszerre (pl. 12, 23, 123)")
        print(prefixString + "\nVisszhang kerese (PING echo)\t[1]\nIdobelyeg kerese\t\t\t\t[2]\nCimmaszk kerese\t\t\t\t\t[3]\nMegsem\t\t\t\t\t\t\t[exit]")

        end = False
        while (end == False):
            try:
                if not operateRemotely:
                    command = input(prefixString + "Adja meg a PING keres(eke)t:")
                    command = command.upper()
                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PE", fileNamePrefix))
                        end = True
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PP", fileNamePrefix))
                        end = True
                    elif (command == "3"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PM", fileNamePrefix))
                        end = True
                    elif (command == "12"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PE -PP", fileNamePrefix))
                        end = True
                    elif (command == "23"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PP -PM", fileNamePrefix))
                        end = True
                    elif (command == "13"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PE -PM", fileNamePrefix))
                        end = True
                    elif (command == "123"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sn -PE -PP -PM", fileNamePrefix))
                        end = True
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")
                        #time.sleep(1)
                else:
                    command = input(prefixString + "Adja meg a PING keres(eke)t:")
                    command = command.upper()
                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PE")
                        end = True
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PP")
                        end = True
                    elif (command == "3"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PM")
                        end = True
                    elif (command == "12"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PE -PP")
                        end = True
                    elif (command == "23"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PP -PM")
                        end = True
                    elif (command == "13"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PE -PM")
                        end = True
                    elif (command == "123"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sn -PE -PP -PM")
                        end = True
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")
            except (KeyboardInterrupt, SystemExit):
                # a megszakitast nem engedjuk felbuborekozni magasabb szintre
                command = None
                print(prefixString + "Megszakitva.")
                pass
        return end

    def freeRun(self):
        prefixString = "<nmapController/freeRun> "
        print("\n" + prefixString + "\n" + self.msg4)

        end = False
        while (end == False):
            command = input(prefixString + "Parancs:")
            command = command.upper()
            if (command == "EXIT"):
                end = True
            else:
                print(self.passRawCommandToNMAP(command))
        return

    def portScan(self, operateRemotely = False):
        #print("\n"*120)
        prefixString = "<nmapController/portScan> "
        fileNamePrefix = "port"

        end = False
        while (end == False):
            try:
                if not operateRemotely:
                    print("\n" + prefixString + "\nBe szeretne kapcsolni az OS felderitest?\nNem\t\t\t\t\t[1]\nIgen (alap)\t\t\t[2]\nIgen (reszletes)\t[3]")
                    detect = input("Parancs:")
                    suffix = ""
                    if detect == "2":
                        suffix = " -O "
                    elif detect == "3":
                        suffix = " -A "
                    else:
                        print(prefixString + "Folytatas OS felderites nelkul.")

                    print(prefixString + "\n" + self.msg5 + "\n")
                    command = input(prefixString + "Parancs:")
                    command = command.upper()

                    interrupt = ""

                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sS" + suffix, fileNamePrefix))
                        interrupt = input("Nyomjon ENTER-t a folytatashoz, 'exit'-et kilepeshez.")
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sT" + suffix, fileNamePrefix))
                        interrupt = input("Nyomjon ENTER-t a folytatashoz, 'exit'-et kilepeshez.")
                    elif (command == "3"):
                        #TODO: felgyorsitani --host-timeout funkcioval
                        print(prefixString + "Figyelem, az UDP scan kifejezetten hosszu idobe kerulhet.")
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sU -sV" + suffix, fileNamePrefix))
                        interrupt = input("Nyomjon ENTER-t a folytatashoz, 'exit'-et kilepeshez.")
                    elif (command == "4"):
                        self.nullFinXmas(suffix)
                        if not end:
                            input("Nyomjon ENTER-t a folytatashoz, 'exit'-et kilepeshez.")
                    elif (command == "5"):
                        # TODO: openvast felkesziteni, hogy itt a closed kell nekem
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sM" + suffix, fileNamePrefix))
                        interrupt = input("Nyomjon ENTER-t a folytatashoz, 'exit'-et kilepeshez.")
                    elif (command == "6"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sO" + suffix, fileNamePrefix))
                        interrupt = input("Nyomjon ENTER-t a folytatashoz, 'exit'-et kilepeshez.")
                    elif (command == "7"):
                        self.ftpBounceAttack()
                        if not end:
                            interrupt = input("Nyomjon ENTER-t a folytatashoz, 'exit'-et kilepeshez.")
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")
                        #time.sleep(1)

                    if (str(interrupt).capitalize() == "EXIT"):
                        end = True
                else:
                    self.commandToSchedule = ""
                    self.fileNamePrefixForSchedule = fileNamePrefix
                    print("\n" + prefixString + "\nBe szeretne kapcsolni az OS felderitest?\nNem\t\t\t\t\t[1]\nIgen (alap)\t\t\t[2]\nIgen (reszletes)\t[3]")
                    detect = input("Parancs:")
                    suffix = ""
                    if detect == "2":
                        suffix = " -O "
                    elif detect == "3":
                        suffix = " -A "
                    else:
                        print(prefixString + "Folytatas OS felderites nelkul.")

                    print(prefixString + "\n" + self.msg5 + "\n")
                    command = input(prefixString + "Parancs:")
                    command = command.upper()

                    interrupt = ""

                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        #print(self.passCommandToNMAP(target + " -sS" + suffix, fileNamePrefix))
                        self.commandToSchedule = (target + " -sS" + suffix)
                        return True
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule =(target + " -sT" + suffix)
                        return True
                    elif (command == "3"):
                        print(prefixString + "Figyelem, az UDP scan kifejezetten hosszu idobe kerulhet.")
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sU -sV" + suffix)
                        return True
                    elif (command == "4"):
                        self.nullFinXmas(suffix, operateRemotely=True)
                        return True
                    elif (command == "5"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sM" + suffix)
                        return True
                    elif (command == "6"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sO" + suffix)
                        return True
                    elif (command == "7"):
                        self.ftpBounceAttack(operateRemotely=True)
                        return True
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")

            except (KeyboardInterrupt, SystemExit):
                # megszakitas felbuborekoztatasanak megakadalyozasa, alapertelemezesek visszaallitasa
                detect = None
                suffix = None
                command = None
                print(prefixString + "Megszakitva.")
                pass
        return

    def nullFinXmas(self, suffix="", operateRemotely = False):
        prefixString = "<portScan/nullFinXmas> "
        fileNamePrefix = "port"
        print(
            prefixString + "\nTCP NULL\t\t\t\t[1]\nTCP FIN flag\t\t\t[2]\nXmas: FIN,PSH,URG flags\t[3]\nMegsem\t\t\t\t\t[exit]")

        end = False
        while (end == False):
            try:
                if not operateRemotely:
                    command = input(prefixString + "Adja meg vizsgalat tipusat")
                    command = command.upper()
                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sN" + suffix, fileNamePrefix))
                        end = True
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sF" + suffix, fileNamePrefix))
                        end = True
                    elif (command == "3"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        print(self.passCommandToNMAP(target + " -sX" + suffix, fileNamePrefix))
                        end = True
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")
                        #time.sleep(1)
                else:
                    command = input(prefixString + "Adja meg vizsgalat tipusat")
                    command = command.upper()
                    if (command == "EXIT"):
                        end = True
                    elif (command == "1"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sN" + suffix)
                        end = True
                    elif (command == "2"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule = (target + " -sF" + suffix)
                        end = True
                    elif (command == "3"):
                        target = input(prefixString + "Adja meg a celpontot (IP cim): ")
                        self.commandToSchedule(target + " -sX" + suffix)
                        end = True
                    else:
                        print(prefixString + "Nem adott meg ervenyes parancsot")
            except (KeyboardInterrupt, SystemExit):
                command = None
                print(prefixString + "Megszakitva.")
                pass
        return end

    def ftpBounceAttack(self, operateRemotely=False):
        prefixString = "<portScan/ftpBounceAttack> "
        fileNamePrefix = "port"

        print(prefixString + "FTP bounce tamadas. Eloszor adja meg a bejelentkezes modjat, majd az FTP szervert (es a portszamot), vegul a celpontot.")

        end = False
        while (end == False):
            try:
                command = input(prefixString + "Adja meg vizsgalat tipusat\nAnonym bejelentkezes\t\t\t\t\t[1]\nBejelentkezes felh.nev/jelszo parossal\t[2]\nMegsem\t\t\t\t\t\t\t\t\t[exit]")
                command = command.upper()
                if (command == "EXIT"):
                    print(prefixString + "Megszakitva.\n")
                    end = True
                elif (command == "1" or command == "2"):
                    cmdStr = "-v -b "

                    if command == "2":
                        un = str(input(prefixString + "Adja meg a felhasznalonevet:"))
                        c = un.upper()
                        if c == "EXIT":
                            print(prefixString + "Megszakitva.\n")
                            return True
                        pw = str(input(prefixString + "Adja meg a jelszot"))
                        c = pw.upper()
                        if c == "EXIT":
                            print(prefixString + "Megszakitva.\n")
                            return True
                        cmdStr += un + ":" + pw

                    addr = str(input(prefixString + "Adja meg az FTP szerver cimet:"))
                    c = addr.upper()
                    if c == "EXIT":
                       print(prefixString + "Megszakitva.\n")
                       return True
                    cmdStr += "@" + addr

                    targ = str(input(prefixString + "Adja meg a letapogatando celpont cimet:"))
                    c = targ.upper()
                    if c == "EXIT":
                        print(prefixString + "Megszakitva.\n")
                        return True
                    cmdStr += " " + targ + " -Pn"

                    if not operateRemotely:
                        print(self.passCommandToNMAP(cmdStr, fileNamePrefix))
                    else:
                        self.commandToSchedule = cmdStr
                        self.fileNamePrefixForSchedule = fileNamePrefix
                    end = True

                else:
                    print(prefixString + "Nem adott meg ervenyes parancsot")
                    #time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                # ne lepjen ki a ciklusbol, csak az esetleges folyamatok allnak le (nmap ctrl+C) miatt
                # alapertelmezesek visszaallitasa
                command = None
                cmdStr = None
                pw = None
                un = None
                addr = None
                targ = None
                print(prefixString + "Megszakitva.")
                pass
        return end