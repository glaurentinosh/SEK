#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from multiprocessing import Process
from time import sleep

################################################################
##################### SENSORES E MOTORES #######################
################################################################

motorEsq = ev3.LargeMotor('outC'); assert motorEsq.connected
motorDir = ev3.LargeMotor('outB'); assert motorDir.connected
##motorGarra = ev3.MediumMotor('outA'); assert motorGarra.connected

## Sensores de cor
corEsq = ev3.ColorSensor('in1'); assert corEsq.connected
corEsq.mode = 'COL-COLOR'

corDir = ev3.ColorSensor('in4'); assert corDir.connected
corDir.mode = 'COL-COLOR'

corCheck = ev3.ColorSensor('in2'); assert corCheck.connected
corCheck.mode = 'COL-COLOR'

#################################################################
######################### VALORES ###############################
#################################################################

velocidade = -400    
delta = 150         # delta de velocidade ao ajeitar caminho
v_curva = -100      # velocidade em curvas

pos_volta = 8 * 360     # quantidade angular de giro dos motores para
pos_dir = 4 * 360       # as curvas
pos_esq = 4 * 360

aprendizado = [0, 0, 0]         # [direita, frente, esquerda] com o codigo da cor
                                # basta reverter a lista pra usar pra volta

cores = [0, 0, 0]              # usa o codigo de cor

t = 100                 # tempo do andaReto()
t_recuo = 300           # tempo de recuo
x_avancar = 200         # avanco ao chegar na lajota

ida = True

def andaReto():
    # Testar NO-COLOR nos sensores para ajeitar o caminho
    if corDir.value() == 0:
        motorEsq.run_timed(speed_sp = velocidade + delta, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade - delta, time_sp = t)

    if corEsq.value() == 0:
        motorDir.run_timed(speed_sp = velocidade + delta, time_sp = t)
        motorEsq.run_timed(speed_sp = velocidade - delta, time_sp = t)
    
    else:
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade, time_sp = t)

def saindoReto():
    while(corCheck.value() != 6): 
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade, time_sp = t)
            
            # Testar NO-COLOR nos sensores para ajeitar o caminho
        if corDir.value() == 0:
            motorEsq.run_timed(speed_sp = velocidade + delta, time_sp = t)
            motorDir.run_timed(speed_sp = velocidade - delta, time_sp = t)
            
        if corEsq.value() == 0:
            motorDir.run_timed(speed_sp = velocidade + delta, time_sp = t)
            motorEsq.run_timed(speed_sp = velocidade - delta, time_sp = t)

#funcao seguir frente dependendo da necessidade

def avancar():
    motorDir.run_to_rel_pos(position_sp = -x_avancar, speed_sp = velocidade)
    motorEsq.run_to_rel_pos(position_sp = -x_avancar, speed_sp = velocidade)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva direita

def curvaDir():
    motorDir.run_to_rel_pos(position_sp = pos_dir, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = pos_dir, speed_sp = (-1) * v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva esquerda

def curvaEsq():
    motorDir.run_to_rel_pos(position_sp = pos_esq, speed_sp = (-1) * v_curva)
    motorEsq.run_to_rel_pos(position_sp = pos_esq, speed_sp = v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

def recuar():
    motorEsq.run_timed(speed_sp = -velocidade, time_sp = t_recuo, stop_action = "brake")
    motorDir.run_timed(speed_sp = -velocidade, time_sp = t_recuo, stop_action = "brake")
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

def meiaVolta():
    motorDir.run_to_rel_pos(position_sp = pos_volta, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = pos_volta, speed_sp = (-1) * v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#função parar

def parar():
    motorDir.stop()
    motorEsq.stop()
    
def traduzCor(cor):
    return {
        0: "no-color",
        1: "preto",
        2: "azul",
        3: "verde",
        4: "amarelo",
        5: "vermelho",
        6: "branco",
        7: "marrom"
    }[cor]

def imprimeCores():
    corAtual = corCheck.value()
    print( traduzCor(corAtual) )
    while True:
        if corCheck.value() != corAtual:
            corAtual = corCheck.value()
            print( traduzCor(corAtual) )

def sabeCor(cor):
    return cor in aprendizado     # retorna True se a cor foi aprendida

def executaCor(cor):
    if aprendizado.index(cor) == 0:         # aprendizado.index(cor) dá o índice da 'cor'
        curvaDir()                          # temos índice 0 pra direita, 1 pra frente, 2 pra esquerda 
        saindoReto()
    if aprendizado.index(cor) == 1:
        saindoReto()
    if aprendizado.index(cor) == 2:
        curvaEsq()
        saindoReto()

def aprender():
    pass

def vendoBranco():
    andaReto()

def vendoPreto():
    parar()
    recuar()
    meiaVolta()
    saindoReto()

def vendoCor():
    parar()
    avancar()
    if sabeCor( corCheck.value() ):
        executaCor( corCheck.value() )
    else:
        aprender()

def vendoNada():
    pass

def interpretaCor(cor):
    if cor == 0:
        vendoNada()
    if cor == 1:
        vendoPreto()
    if cor == 6:
        vendoBranco()
    else:
        vendoCor()


while ida:
    interpretaCor( corCheck.value() )
