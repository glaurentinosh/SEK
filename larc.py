#!/usr/bin/env python3
# coding: utf-8

import ev3dev.ev3 as ev3
#from multiprocessing import Process
from time import sleep
from time import time


motorEsq = ev3.LargeMotor('outC'); assert motorEsq.connected
motorDir = ev3.LargeMotor('outB'); assert motorDir.connected
motorGarra = ev3.MediumMotor('outA'); assert motorGarra.connected
motorCatapulta =  ev3.MediumMotor('outD'); assert motorCatapulta.connected

corEsq = ev3.ColorSensor('in4'); assert corEsq.connected
corEsq.mode = 'COL-COLOR'

corDir = ev3.ColorSensor('in1'); assert corDir.connected
corDir.mode = 'COL-COLOR'

corCheck = ev3.Sensor(address = 'in2', driver_name = 'ht-nxt-color-v2')
corCheck.mode = 'ALL'

ultrassom = ev3.UltrasonicSensor('in3'); assert ultrassom.connected
ultrassom.mode = 'US-DIST-CM'


velocidade = -500
v_ajeita = -100

deltaDir = -200         # delta de velocidade ao ajeitar caminho
deltaEsq = -200
v_curva = -300          # velocidade em curvas

pos_dir = 413           # as curvas
pos_esq = 411
pos_volta = 842         # quantidade angular de giro dos motores para

t = 100                 # tempo do andaReto()
x_avancar = -300        # avanco ao chegar na lajota (ideal 250)
x_cor = -340
x_inicio = -550

avanco_bonecos = 500
avanco_pre_0 = 320
avanco_pre_1 = 320

dist_bonecos = 180
max_bonecos = 1

branco = [11, 12, 13, 14, 15, 16, 17]
corLat = [0, 2, 3, 4, 5]

class Robot:
    def __init__(self):
        self.corAntiga = 47      # ao chegar em cor, indica o valor da cor vista antes (pode ser preto)
        self.contador = -1       ## conta quantas vezes o robot testou a cor; se acertar a direcao, zera o contador
        self.ida = 0            # Faremos ida += 1 quando chegarmos no fim do percurso
        self.ladrilhos = 0      # Checa numero de ladrilhos
        self.bonecos = 0
        self.rampa_pos = -1
        self.rampa_bool = False
        self.plaza = True
        self.variavel = -1      # para fazer o botao de ativar o script
        self.andaRetoRe = -1    # pra andaretore
        self.aprendizado = [47, 47, 47]

robot = Robot()

def abrirAprendizado():
    ## try: tenta abrir um arquivo de aprendizado
    try:
        with open("aprendizado.txt", "r") as ft:            # a lista de aprendizado serah "azul, verde, vermelho"
            robot.aprendizado = ft.read().split(',')              # aqui, criamos uma lista de strings, cada elemento eh a cor
            robot.aprendizado.pop()
            for x in robot.aprendizado:
                print("x", x, "int(x)", int(x))
            robot.aprendizado = [int(x) for x in robot.aprendizado]     # tornamos as strings em inteiros
    except:
        robot.aprendizado = [47, 47, 47]                         # caso nao haja arquivo, criamos a lista
    return robot.aprendizado                                  # Retorna a lista "aprendizado"

def salvarAprendizado(aprendizado):
    with open("aprendizado.txt", "w") as fw:
        for cor in aprendizado:
            fw.write("%s," % cor)

def reverte(aprendizado):
    return [(-1)*i for i in aprendizado]

robot.aprendizado = abrirAprendizado()

def andaReto(velocidade = velocidade):
    # Testar NO-COLOR nos sensores para ajeitar o caminho
    if corDir.value() in [0, 1]:
        motorEsq.run_timed(speed_sp = velocidade -20, time_sp = t, stop_action = 'coast')
        motorDir.run_timed(speed_sp = velocidade - deltaEsq, time_sp = t, stop_action = 'coast')

    if corEsq.value() in [0, 1]:
        motorDir.run_timed(speed_sp = velocidade -10, time_sp = t, stop_action = 'coast')
        motorEsq.run_timed(speed_sp = velocidade - deltaDir, time_sp = t, stop_action = 'coast')
    
    else:
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t, stop_action = 'coast')
        motorDir.run_timed(speed_sp = velocidade, time_sp = t, stop_action = 'coast')

def andaRetoRe(x):
    if x == 0:
        # Testar NO-COLOR nos sensores para ajeitar o caminho
        if corDir.value() in [0, 1]:
            motorEsq.run_timed(speed_sp = -velocidade +20, time_sp = t)
            motorDir.run_timed(speed_sp = -velocidade + deltaEsq, time_sp = t)
            if robot.andaRetoRe == -1:
                robot.andaRetoRe = 0 #direita

        if corEsq.value() in [0, 1]:
            motorDir.run_timed(speed_sp = -velocidade +10, time_sp = t)
            motorEsq.run_timed(speed_sp = -velocidade + deltaDir, time_sp = t)
            if robot.andaRetoRe == -1:
                robot.andaRetoRe = 2 #esquerda
        
        else:
            motorEsq.run_timed(speed_sp = -velocidade, time_sp = t)
            motorDir.run_timed(speed_sp = -velocidade, time_sp = t)

    if x == 1:
        if robot.andaRetoRe == 2:
            motorEsq.run_timed(speed_sp = -velocidade, time_sp = t)
#            motorDir.run_timed(speed_sp = 0, time_sp = t)

        if robot.andaRetoRe == 0:
            motorDir.run_timed(speed_sp = -velocidade, time_sp = t)
#            motorEsq.run_timed(speed_sp = 0, time_sp = t)
        
        if robot.andaRetoRe == -1:
            motorEsq.run_timed(speed_sp = -velocidade, time_sp = t)
            motorDir.run_timed(speed_sp = -velocidade, time_sp = t)

def saindoReto(velocidade = velocidade/1.5, branco = branco, lista = [0,1], listas = [6], alinhar = True, tempo = False):
    print("saindo reto")
    while(atribuiCor(corCheck.value()) not in branco):                                       ## MUDOU: era != 6 agora é not in branco 
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade, time_sp = t)
            
            # Testar NO-COLOR nos sensores para ajeitar o caminho
        if corDir.value() in lista:
            motorEsq.run_timed(speed_sp = velocidade - 20, time_sp = t)
            motorDir.run_timed(speed_sp = velocidade - deltaEsq, time_sp = t)
            
        if corEsq.value() in lista:
            motorDir.run_timed(speed_sp = velocidade - 10, time_sp = t)
            motorEsq.run_timed(speed_sp = velocidade - deltaDir, time_sp = t)

    #alinhaCor_sai()
    if alinhar == True:
        print("u")
        alinhamento_sai(listas = listas)
        saindoReto(alinhar = False)
#        while atribuiCor(corCheck.value()) not in branco:
#            avancar(-20, velocidade = -100)

#funcao seguir frente dependendo da necessidade

def avancar(x_avancar, velocidade = velocidade/1.5):
    print("avancando")
    motorDir.run_to_rel_pos(position_sp = x_avancar, speed_sp = velocidade)
    motorEsq.run_to_rel_pos(position_sp = x_avancar, speed_sp = velocidade)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva direita

def curvaDir(pos_dir = pos_dir):
    print("curva direita")
    motorDir.run_to_rel_pos(position_sp = - pos_dir, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = pos_dir, speed_sp = v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva esquerda

def curvaEsq(pos_esq = pos_esq):
    print("curva esquerda")
    motorDir.run_to_rel_pos(position_sp = pos_esq, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = - pos_esq, speed_sp = v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

def meiaVolta():
    print("meia volta")
    curvaDir(pos_volta)

def parar():
    print("parou")
    sleep(0.2)
    motorDir.stop(stop_action = "coast")
    motorEsq.stop(stop_action = "coast")
    sleep(0.2)

def atribuiCor(cor):
    if cor in [2, 3]:
        return 2
    if cor in [8, 9, 10]:
        return 8
    if cor in [4, 5]:
        return 4
    if cor in branco:
        return 17
    if cor == 0:
        return 4        
    
def associaCor(corDoSensor):
    if atribuiCor(corDoSensor) == 2:
        return 0
    elif atribuiCor(corDoSensor) == 4:
        return 1
    elif atribuiCor(corDoSensor) == 8:
        return 2

def sabeCor(cor):
    # comeca com [47, 47, 47]
    if cor == 47:
        return True
    if robot.aprendizado[associaCor(cor)] == 47:
        return False
    else:
        return True


def executaCor(corr):
    corx = atribuiCor(corr)
    indice = associaCor(corx)
    avancar(x_cor + 150); sleep(0.2)
    if robot.rampa_pos != -1:
        avancar(x_avancar); sleep(0.2)

    if robot.aprendizado[indice] == -1:         # aprendizado.index(cor) da o indice da 'cor'
        #avancar(-x_cor); sleep(0.2)
        curvaDir()                          # temos indice 0 pra direita, 1 pra frente, 2 pra esquerda 
        saindoReto(lista = [0,6])
    elif robot.aprendizado[indice] == 0:
        saindoReto(lista=[0,6])
    elif robot.aprendizado[indice] == 1:
        #avancar(-x_cor); sleep(0.2)
        curvaEsq()
        saindoReto(lista = [0,6])
    print("Fim do executaCor")
    
def aprender(aprendizado):
    print("aprendeu", robot.corAntiga, "atribuindo", atribuiCor(robot.corAntiga))
    if atribuiCor(robot.corAntiga) != 17:
        aprendizado[associaCor(robot.corAntiga)] = robot.contador
    salvarAprendizado(aprendizado)
    robot.contador = -1

#############

v_alinhamento = -100

def alinha_recuando(x, lista = corLat, v_ajeita = v_alinhamento):
    start = time()
    if x == 0:
        while corDir.value() in lista and time() - start < 4:
            motorEsq.run_timed(speed_sp = -v_ajeita, time_sp = t)
            motorEsq.wait_while("running")

    if x == 1:
        while corEsq.value() in lista and time() - start < 4:
            motorDir.run_timed(speed_sp = -v_ajeita, time_sp = t)
            motorDir.wait_while("running")

def alinha_lado_oposto(x, lista = [6], v_ajeita = v_alinhamento):
    start = time()
    if x == 0:
        while corEsq.value() in lista and time() - start < 4:
            motorDir.run_timed(speed_sp = v_ajeita, time_sp = t)
            motorDir.wait_while("running")
    if x == 1:
        while corDir.value() in lista and time() - start < 4:
            motorEsq.run_timed(speed_sp = v_ajeita, time_sp = t)
            motorEsq.wait_while("running")

def alinha_final(x, lista = [6], v_ajeita = v_alinhamento):
    start = time()
    if x == 0:
        while corDir.value() in lista and time() - start < 4:
            motorEsq.run_timed(speed_sp = v_ajeita, time_sp = t)
            motorEsq.wait_while("running")
    if x == 1:
        while corEsq.value() in lista and time() - start < 4:
            motorDir.run_timed(speed_sp = v_ajeita, time_sp = t)
            motorDir.wait_while("running")


def alinhamento_entra(velocidade = velocidade/2):
    # andar ate encontrar cor em um dos sensores (chama esse sensor de A)
    while (corDir.value() not in corLat and corEsq.value() not in corLat):
        print("WAITING do alinhamento entra")
        motorDir.run_timed(time_sp = t, speed_sp = velocidade)
        motorEsq.run_timed(time_sp = t, speed_sp = velocidade)
        motorEsq.wait_while("running")
        motorDir.wait_while("running")
    
    # recuar o lado A ate ver branco
    # avancar o lado B ate ver cor
    # avancar o lado A ate ver cor
    if corDir.value() in corLat:
        alinha_recuando(0)
        alinha_lado_oposto(0)
        alinha_final(0)

    if corEsq.value() in corLat:
        alinha_recuando(1)
        alinha_lado_oposto(1)
        alinha_final(1)

def alinhamento_sai(velocidade = velocidade/2, listas = [0,6]):
    # anda ate encontrar branco com um dos sensores (lado A)
    start = time()
    while ( corDir.value() not in listas and corEsq.value() not in listas ) and time() - start < 5:
        motorDir.run_timed(time_sp = t, speed_sp = velocidade)
        motorEsq.run_timed(time_sp = t, speed_sp = velocidade)
        motorEsq.wait_while("running")
        motorDir.wait_while("running")
    # recua lado A ate ver cor
    # avancar o lado B ate ver branco
    # avanca lado A ate ver branco
    if corDir.value() == 6:
        alinha_recuando(0, [6])
        alinha_lado_oposto(0, corLat)
        alinha_final(0, corLat)

    if corEsq.value() == 6:
        alinha_recuando(1, [6])
        alinha_lado_oposto(1, corLat)
        alinha_final(1, corLat)

#############

def alinhaRampa():
    print("Alinha cor")
    parar()

    if corDir.value() not in corLat:
        print("vou ajeitar a direita", corDir.value(), "sendo esquerda", corEsq.value())
        while corEsq.value() in corLat:
            print("direita, esquerda", corDir.value(), corEsq.value())
            motorDir.run_timed(speed_sp = v_ajeita, time_sp = t)
    elif corEsq.value() not in corLat:
        print("vou ajeitar a esquerda", corEsq.value(), "sendo direita", corDir.value())
        while corDir.value() in corLat:
            print("direita, esquerda", corDir.value(), corEsq.value())
            motorEsq.run_timed(speed_sp = v_ajeita, time_sp = t)

    parar()#; sleep(0.1)

def alinhaCor():
    if corDir.value() not in corLat and corDir.value() != 0:
        print("vou ajeitar a direita", corDir.value(), "sendo esquerda", corEsq.value())
        while corDir.value() not in corLat:
            print("direita, esquerda", corDir.value(), corEsq.value())
            motorEsq.run_timed(speed_sp = v_ajeita, time_sp = t)
    elif corEsq.value() not in corLat and corEsq.value() != 0:
        print("vou ajeitar a esquerda", corEsq.value(), "sendo direita", corDir.value())
        while corEsq.value() not in corLat:
            print("direita, esquerda", corDir.value(), corEsq.value())
            motorDir.run_timed(speed_sp = v_ajeita, time_sp = t)


def rampa_ida():
    print("na rampa - rampa_bool - ", robot.rampa_bool)
    if robot.bonecos == 0:
        sleep(0.2); avancar(100); sleep(0.2)
        meiaVolta()
        print("rampa depois da meia volta")
        robot.ida += 1
        robot.aprendizado = reverte(robot.aprendizado)
        robot.rampa_bool = False
    else:
    
        if corDir.value() == 0 or corEsq.value() == 0:
            saindoReto()
            alinhaRampa()
            start = time()
            print("andaretore zero")
            while time() - start < 1.5:
                andaRetoRe(0)
                sleep(0.3)
            start = time()
            print("andaretore zuno", "robot andaretore", robot.andaRetoRe)
            while time() - start < 0.02:
                andaRetoRe(1)
            robot.andaRetoRe = -1
            sleep(0.3)
            start = time()
            while corCheck.value() in branco:
                andaReto()
            alinhaCor()
            saindoReto()
            #alinhaRampa()
            avancar(100)
        else:
            if robot.ida == 2:
                sleep(0.2)
                avancar(-x_avancar)
                sleep(0.2)

            alinhamento_entra(); sleep(0.2)

        avancar(100); sleep(0.2)
        curvaDir(); sleep(0.2)
        print("Ultrassom?", ultrassom.value())
        avancar(50); sleep(0.2)
        if ultrassom.value() < 300:
            while ultrassom.value() < 300:
                print(ultrassom.value())
                avancar(-10)
#        else:
#            while ultrassom.value() > 300:
#                print(ultrassom.value())
#                avancar(10)


        parar(); avancar(45)
        parar(); sleep(0.2)
        curvaEsq()
        while corCheck.value() in branco:
            andaReto(-200)
        alinhamento_entra()
        saindoReto(-200)
        robot.plaza = True
        plaza()    

def plaza():
    start = time()
    while time() - start < 12:
        andaRetoPlaza()
    sleep(0.2); avancar(50)

    while corCheck.value() != 0:
        avancar(20)
    desce()
    atiraBonecos()
    avancar(-500);        sobe();        avancar(500)
    curvaEsq(); sleep(0.2);    avancar(-1600); sleep(0.2)
    curvaDir(); sleep(0.2);    avancar(-3300); sleep(0.2); avancar(400); sleep(0.2)
    curvaDir(); sleep(0.2);   avancar(-700); sleep(0.2)
    while ultrassom.value() < 200:
        avancar(-10)
    sleep(0.1) 
    avancar(6); sleep(0.1); curvaEsq(); sleep(0.2)
    
    start = time()
    while time() - start < 4:
        andaRetoPlaza()

    sleep(0.1); avancar(200); sleep(0.2)
    curvaDir()
    while corCheck.value() in branco:
        andaReto(velocidade=velocidade/1.5)
    saindoReto()

    robot.ida += 1
    robot.plaza = False
    robot.rampa_bool = False
    robot.aprendizado = reverte(robot.aprendizado)
    
def andaRetoPlaza(velocidade = velocidade):
    motorEsq.run_timed(speed_sp = velocidade/1.2 , time_sp = t, stop_action = 'coast')
    motorDir.run_timed(speed_sp = velocidade/1.5, time_sp = t, stop_action = 'coast')

def saindoRetoPlaza():
    motorEsq.run_timed(speed_sp = -velocidade , time_sp = t)
    motorDir.run_timed(speed_sp = -velocidade, time_sp = t)

def testaRampa():
    if robot.rampa_pos == -1:
        cor1 = [-1,-1,-1]   # Vou testar 3 leituras de cor
        cor1[0] = atribuiCor( corCheck.value() )
        print("cores de rampa", cor1[0])
        avancar(x_avancar/2)
        cor1[1] = atribuiCor( corCheck.value() )
        print("cores de rampa", cor1[1])
        avancar(x_avancar/2)
        cor1[2] = atribuiCor( corCheck.value() )
        print("cores de rampa", cor1[2])

        if cor1[0] == cor1[1]:
            print("nao eh rampa")
            return False
        else:
            if cor1[1] == cor1[2]:
                print("nao eh rampa")
                return False
            else:
                robot.rampa_pos = robot.ladrilhos
                print("eh rampa")
                return True
    else:
        return robot.rampa_bool

def entrandoQuadrado():
    if corDir.value() in [0,1] or corEsq.value() in [0, 1]:
        start = time()
        print("andaretore zero")
        while time() - start < 1.5:
            andaRetoRe(0)
            sleep(0.3)
        start = time()
        print("andaretore zuno", "robot andaretore", robot.andaRetoRe)
        while time() - start < 0.02:
            andaRetoRe(1)
        robot.andaRetoRe = -1
        sleep(0.3)
        start = time()
        while corCheck.value() in branco:
            andaReto(velocidade = velocidade/1.5)
    alinhamento_entra()
    while atribuiCor(corCheck.value()) not in [2, 4, 8]:
        avancar(-20, -100)

def vendoBranco():
    andaReto()          # Quando ve branco, anda reto

def vendoPreto():
    meiaVolta()
    robot.corAntiga = 0                 # ao ver preto, o robot para

def testarDirecao(robot, aprendizado):          # 
    saindoReto(branco = [11, 12, 13, 14, 15, 16, 17, 0], lista = [0,6], listas = [0,1,6]); sleep(0.2); avancar(-x_cor); sleep(0.2)
    curvaDir()
    saindoReto(lista = [0,6])
        
def vendoCor():
    corAtual = atribuiCor(corCheck.value())
    print(corAtual)                            # corAtual eh a cor vista no ladrilho
    if sabeCor( corAtual ):
        print("sabe cor atual")                                 # testa se conhece a corAtual
        if not sabeCor( robot.corAntiga ) and robot.corAntiga != 47:
            aprender(robot.aprendizado)
        executaCor( corCheck.value() )
        if robot.ida % 2 == 0:
            robot.ladrilhos += 1
        if robot.ida % 2 == 1:
            robot.ladrilhos -= 1
        robot.corAntiga = corAtual
    else:
        print("Nao sabe cor atual")
        if robot.corAntiga == 0:                ## PRETO EH ZERO
            robot.contador += 1
            testarDirecao(robot, robot.aprendizado)
            robot.corAntiga = corAtual

        else:
            robot.ladrilhos += 1
            if not sabeCor( robot.corAntiga ):
                aprender(robot.aprendizado)
            
            if robot.corAntiga == 47:
                testarDirecao(robot, robot.aprendizado)
            else:
                if atribuiCor(robot.corAntiga) != atribuiCor(corAtual):
                    testarDirecao(robot, robot.aprendizado)
                else:
                    executaCor(corAtual)
            robot.corAntiga = corAtual


def alinhaCor_sai():
    print("Alinha cor saindo")
    parar()#; sleep(0.1)

    if corDir.value() in corLat:
        print("vou ajeitar a direita", corDir.value(), "sendo esquerda", corEsq.value())
        while corDir.value() in corLat:
            print("direita, esquerda", corDir.value(), corEsq.value())
            motorEsq.run_timed(speed_sp = v_ajeita, time_sp = t)
            motorDir.run_timed(speed_sp = -30, time_sp = t)

    elif corEsq.value() in corLat:
        print("vou ajeitar a esquerda", corEsq.value(), "sendo direita", corDir.value())
        while corEsq.value() in corLat:
            print("direita, esquerda", corDir.value(), corEsq.value())
            motorDir.run_timed(speed_sp = v_ajeita, time_sp = t)
            motorEsq.run_timed(speed_sp = -30, time_sp = t)

    parar()#; sleep(0.1)


def interpretaCor(cs):         # sendo 'cor' a cor vista por corCheck
    cor = cs.value()
    if cor == 0:
        if cs.value(2) > 9:
            cor = 4

    if cor == 0:
        vendoPreto()            # se cor == 0 (preto), executa vendoPreto()
    elif cor in branco:
        vendoBranco()           # se cor in branco, executa vendoBranco() ( andaReto() )
    elif type(cor) == type(None):
        ev3.Sound.beep(); sleep(0.2); print("viu None")
    else:
        entrandoQuadrado()
        if testaRampa() == False:
            vendoCor()              # qualquer outra vai ser uma cor: executa vendoCor()
            if robot.rampa_pos == robot.ladrilhos:
                robot.rampa_bool = True
        else:
            if not sabeCor( robot.corAntiga ):
                aprender(robot.aprendizado)
            rampa_ida()

def sobe(time = 800, garra_speed = 1500):
    motorGarra.run_timed(time_sp = time, speed_sp = garra_speed)
    motorGarra.wait_while("running")

def desce(time = 800, garra_speed = 1500):
    motorGarra.run_timed(time_sp = time, speed_sp = -garra_speed)
    motorGarra.wait_while("running")

def desceCatapulta(time = 400,  garra_pos = 300, garra_speed = 1500):
    motorCatapulta.run_timed(time_sp = time, speed_sp = garra_speed)
    motorCatapulta.wait_while("running")

def sobeCatapulta(time = 400, garra_pos = 300, garra_speed = 1500):
    motorCatapulta.run_timed(time_sp = time, speed_sp = -garra_speed)
    motorCatapulta.wait_while("running")

def atiraBonecos():
    desceCatapulta()
    avancar(100); avancar(-100)
    sobeCatapulta()
    robot.bonecos = 0

def pegaBonecos():
    if robot.ladrilhos == robot.rampa_pos:
        pass
    else:
        if robot.bonecos == 0:
            parar()
            avancar(avanco_pre_0)
            parar()
        else:
            parar()
            avancar(avanco_pre_1)
            parar()

        sleep(0.2); curvaDir(415); sleep(0.2);  avancar(-100, -300); sleep(0.2); desce(); sleep(0.1)
        avancar(avanco_bonecos);  parar(); sleep(0.2);  sobe(800)
        if robot.bonecos == 0:
            desce(140)
        else:
            desce(90)
        sobe(140)
        desce(120); sobe(200);  desce(120);        sobe(200)
        avancar(-avanco_bonecos); sleep(0.3);  avancar(100, 400); sleep(0.3)
        robot.bonecos += 1
        if robot.bonecos >= max_bonecos and robot.ida % 2 == 1:
            curvaDir(415)
            robot.ida += 1
            robot.aprendizado = reverte(robot.aprendizado)

        else:    
            curvaEsq(415)
    
def imprimeCores():
    cl = corCheck
    while True:
        print(cl.value(0), '(',  cl.value(1), cl.value(2), cl.value(3), ')', "ultrassom", ultrassom.value())
        sleep(0.4)

def imprimiDistancia():
    while True:
        print(ultrassom.value())
        sleep(0.5)

# -------------------------------------
#------- Main comeca aqui! ------------
# -------------------------------------

#p1 = Process(target = imprimeCores)
#p1.start()

#p2 = Process(target = imprimiDistancia)
#p2.start()

btn = ev3.Button()

def right(state):
    if state == True:
        sleep(1)
        robot.variavel *= -1
    return robot.variavel

btn.on_right = right  

robot.ida = 2
#robot.rampa_pos = 1
robot.variavel = 1
#robot.bonecos = 2

while True:
    btn.process()
    if robot.variavel == -1:
        print("--- Em espera ---")
        sleep(1)
    else:
        if robot.ida == 0:                            # Enquanto o robot estiver na ida
            interpretaCor( corCheck )       # interpreta a cor do corCheck (veja interpretaCor)
        if robot.ida == 1:
            print("vou voltar")
            while robot.ladrilhos != 0:
                interpretaCor( corCheck )
            avancar(x_inicio)
            meiaVolta()
            robot.aprendizado = reverte(robot.aprendizado)
            robot.ida = 2
        
        if robot.ida > 1:
            if robot.ida % 2 == 0:
                if ultrassom.value() < dist_bonecos and robot.bonecos < max_bonecos and corCheck.value() in branco and robot.ladrilhos != robot.rampa_pos:
                    print("pegarei")
                    pegaBonecos()
                else:
                    interpretaCor(corCheck)
            if robot.ida % 2 == 1:
                if ultrassom.value() < dist_bonecos and robot.ladrilhos != robot.rampa_pos:
                    pegaBonecos()
                    
                else:
                    interpretaCor(corCheck)
                    if robot.ladrilhos == 0:
                        avancar(x_inicio)
                        meiaVolta()
                        robot.aprendizado = reverte(robot.aprendizado)
                        robot.ida += 1
                        print("robot.ida - ", robot.ida)