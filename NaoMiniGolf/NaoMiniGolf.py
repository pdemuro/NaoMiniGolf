#!/usr/bin/env python
# -*- coding:utf-8 -*-
from naoqi import ALProxy
import time
import math
import cv2
import numpy as np


def StiffnessOn(proxy):  # corpo in posizione rigida
    proxy.stiffnessInterpolation("Body", 1, 1)

def PrimaRicercaPalla():
    global numRicercaPalle, passoRobotLungo
    numRicercaPalle += 1  # viene incrementato il tempo di ricerca ogni secondo
    camProxy.setActiveCamera(1)  # impostazione della camera di sotto del robot

    if numRicercaPalle <= 3:
        rangeRicerca = -60
    else:
        rangeRicerca = -120

    ricerca = rangeRicerca
    while ricerca <= -rangeRicerca:  # finchè non raggiunge l'angolazione opposta continua a richiamare la funzione di ricerca
        risRicercaPalla = trovaPalla(ricerca)  # ricerca palla in base alla posizione del collo
        if risRicercaPalla != []:
            return risRicercaPalla
        else:
            ricerca += 60
    print("Nessuna palla rossa")
    motionProxy.angleInterpolationWithSpeed("HeadYaw", 0.0, 0.5)
    motionProxy.setMoveArmsEnabled(False, False)  # ferma le mani
    motionProxy.moveTo(0.5, 0.0, 0.0, passoRobotCorto)
    risRicerca = [0, 0, 1]
    return risRicerca


def trovaPalla(angolo, angolo2=0):  # Restituisce i dati della palla rossa
    camProxy.setActiveCamera(1)
    # angleinterpolation -> 1)nome del corpo 2)angolo di interpolazione 3)velocita
    # headyaw: rotazione della testa da destra a sinistra o viceversa
    motionProxy.angleInterpolationWithSpeed("HeadYaw", angolo * math.pi / 180,
                                            0.8)  # angolo * math.pi Pi / 180 è la formula di conversione radiante
    # headpitch: inclinazione della testa dal basso verso l'alto e viceversa
    motionProxy.angleInterpolationWithSpeed("HeadPitch", angolo2 * math.pi / 180, 0.8)
    redballProxy.subscribe("redBallDetected")
    # Inserisce una coppia chiave-valore in memoria, dove valore è un int parametri: chiave - Nome del valore da inserire. valore - L'int da inserire
    memoryProxy.insertData("redBallDetected", [])  # Inserisci i dati in memoria

    # Aggiungi il riconoscimento palla rossa e annulla il riconoscimento palla rossa
    time.sleep(2)
    for i in range(10):  # fa l'iterazione 10 volte
        datiPalla = memoryProxy.getData("redBallDetected")  # se trova la palla
        # [TimeStamp,BallInfo,CameraPose_InTorsoFrame,CameraPose_InRobotFrame, Camera_I]

    # redballProxy.unsubscribe("redBallDetected")
    if (datiPalla != []):
        print("La palla rossa è distante")
        print(datiPalla)
        angoloTesta = motionProxy.getAngles("HeadYaw", True)  # salva angolo collo
        InfoPalla = [angoloTesta, datiPalla,
                     0]  # ritorna l'angolo del collo,i dati dell palla e 0 per far finire l'iterazione della ricerca
        return InfoPalla
    else:
        print("Non trovato")
        return []


def DistanzaRobotPalla(datiPalla):
    lunCamminata = 0.7

    angoloPalla = datiPalla[0]  # Angolo di deflessione della testa
    wzCamera = datiPalla[1][1][0]  # angolo alfa
    wyCamera = datiPalla[1][1][1]  # angolo beta
    isenabled = False
    x = 0.0
    y = 0.0
    if (angoloPalla[0] + wzCamera < 0.0):
        theta = angoloPalla[0] + wzCamera
    else:
        theta = angoloPalla[0] + wzCamera

    motionProxy.setMoveArmsEnabled(False, False)
    # Poi, per la prima volta, il robot si gira verso la palla rossa.
    motionProxy.angleInterpolationWithSpeed("HeadYaw", 0.0, 0.5)
    motionProxy.moveTo(x, y, theta,passoRobotCorto)  # x=y=0

    time.sleep(1.5)
    currPalla = memoryProxy.getData("redBallDetected")  # dati correnti palla dopo che si è spostato
    infoPalla = currPalla[1]
    thetah = infoPalla[0]
    thetav = infoPalla[1] + (40 * math.pi / 180.0)  # centro della palla + 40 gradi
    x = lunCamminata  # Minimo 40 cm
    if (x >= 0):
        theta = 0.0
        motionProxy.setMoveArmsEnabled(False, False)
        print("Mosso in direzione della palla rossa")
        # Successivamente, per la seconda volta, il robot cammina in una posizione a 20 cm dalla palla rossa,
        # con un programma di 40 cm, perché il robot fa troppi errori nella camminata reale per calciare la palla
        motionProxy.moveTo(x, y, theta,passoRobotCorto)
    motionProxy.waitUntilMoveIsFinished()
    # Abbassa la testa di 30 gradi.
    nomeArto = ["HeadPitch"]
    tempo = [0.5]
    angolo = [30 * math.pi / 180.0]
    motionProxy.angleInterpolation(nomeArto, angolo, tempo, isenabled)
    time.sleep(1.5)
    currPalla = memoryProxy.getData("redBallDetected")
    infoPalla = currPalla[1]
    thetah = infoPalla[0]
    thetav = infoPalla[1] + (70 * math.pi / 180.0)
    x = 0.0
    y = 0.0
    theta = thetah
    motionProxy.setMoveArmsEnabled(False, False)
    print("Camminare fino a 20cm dalla palla rossa")
    # Poi, per la terza volta, il robot corregge l'angolo alla palla rossa.
    motionProxy.moveTo(x, y, theta,passoRobotCorto)
    time.sleep(1.5)

    currPalla = memoryProxy.getData("redBallDetected")
    infoPalla = currPalla[1]
    thetah = infoPalla[0]
    thetav = infoPalla[1] + (70 * math.pi / 180.0)
    x = (lunCamminata - 0.03) / (
        math.tan(thetav)) - 0.15  # La linea a tre punti, in ultima analisi, rivede i punti chiave
    theta = thetah
    motionProxy.setMoveArmsEnabled(False, False)
    print("Correzione dell'angolo completata")
    # Poi, per la quarta volta, il robot cammina a 10 centimetri dalla palla rossa
    motionProxy.moveTo(x, y, theta,passoRobotCorto)
    time.sleep(1.5)
    print("Raggiunti i 10cm")
    currPalla = memoryProxy.getData("redBallDetected")
    infoPalla = currPalla[1]
    thetah = infoPalla[0]
    print(thetah)
    thetav = infoPalla[1] + (70 * math.pi / 180.0)
    x = 0.0
    y = 0.0
    theta = thetah
    motionProxy.setMoveArmsEnabled(False, False)
    print("Cammino fino a 20cm dalla palla rossa")
    # Poi, per la quinta volta, il robot ha finalmente corretto l'angolo con la palla rossa
    motionProxy.moveTo(x, y, theta,passoRobotCorto)
    time.sleep(1.5)
    # Successivamente, per la sesta e ultima volta, rilevare la distanza tra la palla e il robot dx
    currPalla = memoryProxy.getData("redBallDetected")
    infoPalla = currPalla[1]
    thetah = infoPalla[0]
    thetav = infoPalla[1] + (70 * math.pi / 180.0)
    dx = (lunCamminata - 0.03) / (math.tan(thetav))  # dx come lato di un triangolo
    print (dx)
    return dx
    # print("dx="+dx)


def correzionePos():
    global passoRobotCorto
    h = 0.7

    motionProxy.setMoveArmsEnabled(False, False)
    val = trovaPalla(0, 30)
    while val == []:
        motionProxy.moveTo(-0.2, 0.2, 0, passoRobotCorto)
        val = trovaPalla(0, 30)
    ballinfo = val[1][1]
    thetah = ballinfo[0]  # center X
    thetav = ballinfo[1] + (70 * math.pi / 180.0)  # center Y
    x = (h - 0.03) / (math.tan(thetav)) - 0.11
    y = ((h - 0.03) / math.sin(thetav)) * math.tan(thetah)
    if (y > 0):
        y = ((h - 0.03) / math.sin(thetav)) * math.tan(thetah) + 0.3
    else:
        y = ((h - 0.03) / math.sin(thetav)) * math.tan(thetah) + 0.3
    motionProxy.setMoveArmsEnabled(False, False)
    motionProxy.moveTo(x, 0.0, 0.0,passoRobotCorto)

    motionProxy.moveTo(0.0, y, 0.0,passoRobotCorto)


def colpo():
    motionProxy.angleInterpolationWithSpeed(NomiArtoDestro, sollevaBraccio, 0.2)
    time.sleep(1)
    motionProxy.angleInterpolationWithSpeed(NomiArtoDestro, inclinaPolso, 0.1)
    time.sleep(1)
    wristYaw = ["RWristYaw"]
    tempo = [1]
    angolazione = [65 * math.pi / 180.0]
    motionProxy.angleInterpolation(wristYaw, angolazione, tempo, True)


def colpoInizio():
    motionProxy.angleInterpolationWithSpeed(NomiArtoDestro, sollevaBraccio, 0.2)
    time.sleep(1)
    motionProxy.angleInterpolationWithSpeed(NomiArtoDestro, inclinaPolso, 0.1)
    time.sleep(1)
    wristYaw = ["RWristYaw"]
    tempo = [1.8]
    angolazione = [65 * math.pi / 180.0]
    motionProxy.angleInterpolation(wristYaw, angolazione, tempo, True)


def afferraMazza():
    names = list()
    times = list()
    keys = list()

    names.append("HeadPitch")
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("HeadYaw")  # movimento dell'asse Z
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("LAnklePitch")  # Asse Z caviglia
    times.append([1, 2, 3, 4])
    keys.append([-0.349794, -0.349794, -0.349794, -0.349794])

    names.append("LAnkleRoll")  # Asse X caviglia
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("LElbowRoll")  # Asse Z del gomito
    times.append([1, 2, 3, 4, 8, 8.5])
    keys.append([-0.321141, -0.321141, -1.9, -1.9, -1.23490659, -1.11843645])

    names.append("LElbowYaw")  # Asse X
    times.append([1, 2, 3, 4])
    keys.append([-1.37757, -1.37757, -1.466076, -1.466076])

    names.append("LHand")  # Palmo sinistro
    times.append([1, 2, 3, 4, 5.2])
    keys.append([0.9800, 0.9800, 0.9800, 0.9800, 0.1800])

    names.append("LHipPitch")  # Asse Y della gamba
    times.append([1, 2, 3, 4])
    keys.append([-0.450955, -0.450955, -0.450955, -0.450955])

    names.append("LHipRoll")  # Asse X della gamba
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("LHipYawPitch")
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("LShoulderPitch")  # Asse Y del ginocchio
    times.append([1, 2, 3, 4, 5.2, 8, 8.5])
    keys.append([1.53885, 1.43885, 1.3, 1.3, 1.3, 1.43856, 1.88495559])

    names.append("LShoulderRoll")  # Asse Z della spalla
    times.append([1, 2, 3, 4, 5.2])
    keys.append([0.268407, 0.268407, -0.04014, -0.04014, -0.04014])

    names.append("LWristYaw")  # Asse X del polso

    times.append([1, 2, 3, 4])
    keys.append([-0.016916, -0.016916, -1.632374, -1.632374])

    names.append("RAnklePitch")  # Asse Y Caviglia
    times.append([1, 2, 3, 4])
    keys.append([-0.354312, -0.354312, -0.354312, -0.354312])

    names.append("RAnkleRoll")  # Asse X Caviglia
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("RElbowRoll")  # Asse Z del gomito
    times.append([1, 2, 3, 4, 8, 8.5])
    keys.append([0.958791, 0.958791, 0.958791, 0.958791, 1.23490659, 1.11843645])

    names.append("RElbowYaw")  # Asse X del gomito
    times.append([1, 2, 3, 4])
    keys.append([1.466076, 1.466076, 1.466076, 1.466076])

    names.append("RHand")
    times.append([1, 2, 3, 4])
    keys.append([0.0900, 0.0900, 0.0900, 0.0900])

    names.append("RHipPitch")  # Asse Y della gamba
    times.append([1, 2, 3, 4])
    keys.append([-0.451038, -0.451038, -0.451038, -0.451038])

    names.append("RHipRoll")  # Asse X della gamba
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("RHipYawPitch")
    times.append([1, 2, 3, 4])
    keys.append([0, 0, 0, 0])

    names.append("RShoulderPitch")  # Asse Y della spalla
    times.append([0.5, 1, 2, 3, 4, 5.2, 8, 8.5])
    # keys.append([1.03856, 1.03856, 1.03856, 1.03856, 1.03856])
    keys.append([0.9, 1.03856, 1.03856, 1.03856, 1.03856, 1.03856, 1.43856, 1.88495559])

    names.append("RShoulderRoll")  # Asse Z della spalla
    times.append([1, 2, 3, 4, 5.2])
    keys.append([0.04014, 0.04014, 0.04014, 0.04014, 0.04014])

    names.append("RWristYaw")  # Asse X del polso
    times.append([1, 2, 3, 4])
    keys.append([1.632374, 1.632374, 1.632374, 1.632374])
    motionProxy.setMoveArmsEnabled(False, False)
    motionProxy.angleInterpolation(names, keys, times, True)


def rilasciaMazza():
    names = list()
    times = list()
    keys = list()

    names.append("HeadPitch")
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("HeadYaw")  # movimento dell'asse Z
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("LAnklePitch")  # Asse Z caviglia
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])

    keys.append([-0.349794, -0.349794, -0.349794, -0.349794, -0.349794, -0.349794, -0.349794])

    names.append("LAnkleRoll")  # Asse X caviglia
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("LElbowRoll")  # Asse Z del gomito
    # times.append([1, 2, 3, 4, 8, 8.5])
    # keys.append([-0.321141, -0.321141, -1.9, -1.9, -1.23490659, -1.51843645])
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([-1.51843645, -1.23490659, -1.23490659, -0.321141, -0.321141, -0.321141, -0.321141])

    names.append("LElbowYaw")  # Asse X
    # times.append([1, 2, 3, 4])
    # keys.append([-1.37757, -1.37757, -1.466076, -1.466076])
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([-1.466076, -1.466076, -1.466076, -1.37757, -1.37757, -1.37757, -1.37757])

    names.append("LHand")  # Palmo sinistro
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5, 9])
    keys.append([0.1800, 0.1800, 0.9800, 0.9800, 0.9800, 0.9800, 0.9800, 0.1800])

    names.append("LHipPitch")  # Asse Y della gamba
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([-0.450955, -0.450955, -0.450955, -0.450955, -0.450955, -0.450955, -0.450955])

    names.append("LHipRoll")  # Asse X della gamba
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("LHipYawPitch")
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("LShoulderPitch")  # Asse Y del ginocchio
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    # keys.append([1.53885, 1.43885, 1.3, 1.3, 1.3, 1.43856, 1.88495559])
    keys.append([1.88495559, 1.43856, 1.3, 1.3, 1.3, 1.43885, 1.53885])

    names.append("LShoulderRoll")  # Asse Z della spalla
    # times.append([1, 2, 3, 4, 5.2])
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    # keys.append([0.268407, 0.268407, -0.04014, -0.04014, -0.04014])
    keys.append([-0.04014, -0.04014, -0.04014, 0.268407, 0.268407, 0.268407, 0.268407])

    names.append("LWristYaw")  # Asse X del polso
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    # keys.append([-0.016916, -0.016916, -1.632374, -1.632374])
    keys.append([-1.632374, -1.632374, -1.632374, -1.632374, -1.632374, -0.016916, -0.016916])

    names.append("RAnklePitch")  # Asse Y Caviglia
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([-0.354312, -0.354312, -0.354312, -0.354312, -0.354312, -0.354312, -0.354312])

    names.append("RAnkleRoll")  # Asse X Caviglia
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("RElbowRoll")  # Asse Z del gomito
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    # keys.append([0.958791, 0.958791, 0.958791, 0.958791, 1.23490659, 1.51843645])
    keys.append([1.51843645, 1.23490659, 1.23490659, 0.958791, 0.958791, 0.958791, 0.958791])

    names.append("RElbowYaw")  # Asse X del gomito
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([1.466076, 1.466076, 1.466076, 1.466076, 1.466076, 1.466076, 1.466076])

    names.append("RHand")
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0.0900, 0.0900, 0.0900, 0.0900, 0.0900, 0.0900, 0.0900])

    names.append("RHipPitch")  # Asse Y della gamba
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([-0.451038, -0.451038, -0.451038, -0.451038, -0.451038, -0.451038, -0.451038])

    names.append("RHipRoll")  # Asse X della gamba
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("RHipYawPitch")
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0, 0, 0, 0, 0, 0, 0])

    names.append("RShoulderPitch")  # Asse Y della spalla
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5, 9])
    # keys.append([0.9, 1.03856, 1.03856, 1.03856, 1.03856, 1.03856, 1.43856, 1.88495559])
    keys.append([1.88495559, 1.43856, 1.03856, 1.03856, 1.03856, 1.03856, 1.03856, 0.9])

    names.append("RShoulderRoll")  # Asse Z della spalla
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([0.04014, 0.04014, 0.04014, 0.04014, 0.04014, 0.04014, 0.04014])

    names.append("RWristYaw")  # Asse X del polso
    times.append([1, 1.5, 4.3, 5.5, 6.5, 7.5, 8.5])
    keys.append([1.632374, 1.632374, 1.632374, 1.632374, 1.632374, 1.632374, 1.632374])
    motionProxy.setMoveArmsEnabled(False, False)
    motionProxy.angleInterpolation(names, keys, times, True)


def RotazioneRobot():
    motionProxy.angleInterpolationWithSpeed("HeadYaw", 0.0, 0.5)
    # Parametri di camminata del robot
    motionProxy.setMoveArmsEnabled(False, False)
    global passoRobotLungo
    motionProxy.moveTo(0.0, 0.0, 1, passoRobotCorto)
    time.sleep(0.5)
    motionProxy.moveTo(0.0, 0.0, 1, passoRobotCorto)
    motionProxy.setMoveArmsEnabled(False, False)
    motionProxy.waitUntilMoveIsFinished()
    motionProxy.moveTo(1, 0.0, 0.0, passoRobotLungo)
    time.sleep(0.5)


def trovaAsta(rangeDimAsta=[75, 850]):
    TIME = time.strftime('%m-%d_%H-%M-%S', time.localtime(time.time()))
    print("Cercando l'asta")

    # range colore giallo
    low = np.array([15, 80, 80])
    up = np.array([36, 255, 255])
    camProxy.setActiveCamera(0)  # camera alta
    videoClient = camProxy.subscribe("python_client", 2, 11, 5)  # 640*480，RGB, FPS
    rowImgData = camProxy.getImageRemote(videoClient)  # restituisce info immagine catturata
    camProxy.unsubscribe(videoClient)
    imgWidth = rowImgData[0]  # lunghezza immagine
    imgHeight = rowImgData[1]  # altezza immagine

    image = np.zeros((imgHeight, imgWidth, 3),
                     dtype='uint8')  # settaggio predefinito di opencv per le colorazioni (BGR)

    image.data = rowImgData[6]  # array of size height * width * nblayers containing image data

    b, g, r = cv2.split(image)  # divide immagine nei tre canali e li assegna
    img = cv2.merge([r, g, b])  # riunisce i canali in una immagine

    frameHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # viene settato il colore dell'immagine da BGR a HSV
    frameBin = cv2.inRange(frameHSV, low, up)

    # frameBin debug
    cv2.imwrite("bin.jpg", frameBin)
    _, contours, _ = cv2.findContours(frameBin, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_NONE)  # restituisce i contorni dell'asta
    if len(contours) == 0:
        cv2.imwrite("asta_non_trovata%s.jpg" % TIME, img)
        print("Giallo non trovato in img")
        return []

    contornoValido = []

    perimetroAsta = cv2.arcLength(contours[0], True)  # calcolo della lunghezza del perimetro dell'asta
    if perimetroAsta <= rangeDimAsta[0] or perimetroAsta >= rangeDimAsta[1]:
        print ("trovaAsta(): troppo grande o piccola")

    rettangoloAsta = cv2.minAreaRect(contours[0])  # calcola l'area dell'asta
    w = 0
    h = 0

    if (rettangoloAsta[1][0] < rettangoloAsta[1][1]):
        w = rettangoloAsta[1][0]
    else:
        w = rettangoloAsta[1][1]

    if (rettangoloAsta[1][0] > rettangoloAsta[1][1]):
        h = rettangoloAsta[1][0]
    else:
        h = rettangoloAsta[1][1]

    print ("trovaAsta(): asta trovata", w, h)
    contornoValido.append(contours[0])

    if len(contornoValido) == 0:
        cv2.imwrite("asta_non_trovata%s.jpg" % TIME, img)
        print("l'asta è troppo grande")
        return []

    rettangoloAsta = cv2.minAreaRect(contornoValido[0])
    if rettangoloAsta[1][0] > rettangoloAsta[1][1]:
        w = rettangoloAsta[1][1]
        h = rettangoloAsta[1][0]
        center = rettangoloAsta[0]
        theta = -rettangoloAsta[2] * math.pi / 180
        alpha = theta + math.atan(1.0 * w / h)
        bevel = math.sqrt(w * w + h * h) / 2

        x1 = int(center[0] - bevel * math.cos(alpha))
        x2 = int(x1 - w * math.sin(theta))
        x = int((x1 + x2) / 2)
    else:
        w = rettangoloAsta[1][0]
        h = rettangoloAsta[1][1]
        center = rettangoloAsta[0]
        theta = -rettangoloAsta[2] * math.pi / 180
        alpha = theta + math.atan(1.0 * h / w)
        bevel = math.sqrt(w * w + h * h) / 2
        x1 = int(center[0] - bevel * math.cos(alpha))
        x2 = int(x1 + w * math.cos(theta))
        x = int((x1 + x2) / 2)

        # img è l'immagine, maxcontour sono i contorni, -1 è per disegnare tutti i contorni, colore contorno blu
    contorno = contornoValido[0]
    # cv2.drawContours(img, contorno, -1, (0, 0, 255), 1)
    cv2.imwrite("ok.jpg", img)
    # Questo valore è l'angolo orizzontale
    return (320.0 - x) / 640.0 * 61 * math.pi / 180


def CalcolaPosAsta():
    angoloTesta = -120 * math.pi / 180.0 # 120 gradi
    maxAngle = 60
    motionProxy.angleInterpolationWithSpeed("HeadPitch", 0, 0.5)
    motionProxy.angleInterpolationWithSpeed("HeadYaw", angoloTesta, 0.5)
    time.sleep(0.5)
    angoloAsta = trovaAsta([300, 850])
    while angoloAsta == []:
        angoloTesta += 1.0 / 3 * math.pi  # +60 gradi
        if angoloTesta > maxAngle:
            return -100
        motionProxy.angleInterpolationWithSpeed("HeadYaw", angoloTesta, 0.5)
        motionProxy.angleInterpolationWithSpeed("HeadPitch", 0, 0.5)
        time.sleep(0.5)
        angoloAsta = trovaAsta([300, 850])
    angoloRobot = motionProxy.getAngles("HeadYaw", True)
    # Dopo averlo calcolato, gira a sinistra di 90 gradi
    angoloFinale = angoloRobot[0] + angoloAsta - 0.5 * math.pi
    rotPostAsta(angoloFinale)
    return angoloFinale


def rotPostAsta(angolo):
    motionProxy.angleInterpolationWithSpeed("HeadYaw", 0, 0.5)
    motionProxy.angleInterpolationWithSpeed("HeadPitch", 0, 0.5)
    motionProxy.setMoveArmsEnabled(False, False)
    z = 0.4
    if angolo >= 0:
        while angolo > z:
            angolo -= z
            motionProxy.moveTo(0, 0, z)
            time.sleep(1)
    else:
        while angolo < -z:
            angolo += z
            motionProxy.moveTo(0, 0, -z)
    motionProxy.moveTo(0, 0, angolo)


PORT = 9559
robotIP = "127.0.0.1"
memoryProxy = ALProxy("ALMemory", robotIP, PORT)
motionProxy = ALProxy("ALMotion", robotIP, PORT)
postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
redballProxy = ALProxy("ALRedBallDetection", robotIP, PORT)
camProxy = ALProxy("ALVideoDevice", robotIP, PORT)

numRicercaPalle = 0
# Andatura e battuta
maxstepx = 0.04
maxstepy = 0.14
maxsteptheta = 0.3
maxstepfrequency = 0.6
stepheight = 0.01
torsowx = 0.0
torsowy = 0.0
passoRobotLungo = [["MaxStepX", 0.04], ["MaxStepY", 0.14], ["MaxStepTheta", 0.3], ["MaxStepFrequency", 0.6],
                   ["StepHeight", 0.01], ["TorsoWx", 0], ["TorsoWy", 0]]
passoRobotCorto = [["MaxStepX", 0.02], ["MaxStepY", 0.14], ["MaxStepTheta", 0.3], ["MaxStepFrequency", 0.6],
                   ["StepHeight", 0.01], ["TorsoWx", 0], ["TorsoWy", 0]]
NomiArtoDestro = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
NomiArtoSinistro = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand"]
inclinaPolso = [1.35792, 0.05766, 1.50110, 1.50982, -0.667955, 0.0900]
sollevaBraccio = [1.02599, 0.321235, 1.63107, 1.48231, 0.230070, 0.0900]
estendiBraccio = [1.02599, 1.6, 1.63107, 1.48231, 0.230070, 0.0900]

# ------------------------------------------------------------------------------------------------------------#
StiffnessOn(motionProxy)
postureProxy.goToPosture("StandInit", 1.0)
alpha = -math.pi / 2  # valore iniziale

colpoInizio()
time.sleep(1)
afferraMazza()
time.sleep(1)
RotazioneRobot()
while True:
    while True:
        datiPalla = PrimaRicercaPalla()  # Posizionamento palla rossa Restituisce informazioni sulla posizione della palla rossa
        if (datiPalla[2] == 0):
            break
    DistanzaRobotPalla(datiPalla)
    correzionePos()
    CalcolaPosAsta()
    correzionePos()
    time.sleep(1)
    CalcolaPosAsta()
    correzionePos()
    time.sleep(1)
    rilasciaMazza()
    colpo()
    RotazioneRobot()
