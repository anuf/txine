# -*- coding: utf-8 -*-
"""
@author: Adolfo Núñez Fernández
Outono 2015
"""

from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

        
def menu():
    print("\nEscolla unha opción:\n\
    [1] Cotización por pantalla\n\
    [2] Cotización a fichero\n\
    [3] Cotización dun valor concreto\n\
    [4] Saír")
        
def getBolsa():
    ''' 
    Obtén as cotizacións de bolsa a partires da url de referencia, devolvendo
    os resultados nun obxecto dataframe    
    '''
    
    # url de referencia
    url = "http://www.invertia.com/mercados/bolsa/indices/ibex-35/acciones-ib011ibex35"

    # obtemos unha response mediante a libraría request
    r = requests.get(url)

    # Extraemos texto HTML coa libraría BeautifulSoup
    soup = BeautifulSoup(r.text)
    t = soup.find("table", { "class" : "tb_fichas" })

    # Crease unha táboa personalizada nun obxecto lista    
    myTable = []
    
    # Atopamos as filas da táboa HTML
    filas = t.find_all("tr")
    
    # Percorremos as filas
    for idFila in range(len(filas)):
        
        # Créase unha fila personalizada nun obxecto lista
        myRow =[]
        if idFila == 0: # Cabeceiras
            # Atopamos as cabeceiras da primeira fila
            cabeceiras = filas[idFila].find_all("th")
            # Percorremos as columnas
            for idCabeceira in range(len(cabeceiras)):
                if idCabeceira != 4: # obviamos esta columna sen valores
                    # Eliminanse os retornos de carro do texto das cabeceiras                
                    cabeceiraLimpa = cabeceiras[idCabeceira].text.replace("\n", "")
                    myRow.append(cabeceiraLimpa)
        else:
            # Atopamos as celdas de cada fila
            celas = filas[idFila].find_all("td")
            # Percorremos as columnas
            for idCela in range(len(celas)):
                if idCela != 4: # obviamos esta columna sen valores
                    myRow.append(celas[idCela].text)
        # Engádese a fila á táboa
        myTable.append(myRow)

    # Créase un dataframe a partires da táboa para manexar os datos        
    df = pd.DataFrame(myTable[1:], index=None, columns=myTable[0])
    
    return df
    
def getIdentificadorBursatil(identificador):
    ''' Obtén as cotizacións de bolsa dun índice seleccionado '''    
    
    # Obtén as cotizacións de bolsa totais    
    df = getBolsa()
    
    # Comproba se existe o índice
    for indice in range(len(df)): 
        if df.ix[indice]["TKR*"] == identificador:
            '''
            Devolve a data (ano, mes, día,  hora, minuto, segundo) xunto 
            co resultado da consulta
            '''
            print("{0}\n{1} {2}\n{3}\n{4}\n".format("*"*80, \
                  time.strftime("%d/%m/%Y %H:%M:%S"), "*"*60, "*"*80, \
                  df.ix[indice:indice]))           
            '''
            # Outro formato alternativo
            print("{0}".format(df.ix[indice:indice]))
            '''
            return True
            
    print('\nÍndice "{0}" non atopado\n'.format(identificador))
    return False
        
if __name__ == "__main__":
    ''' Programa principal. Chamada ao menú de opcións '''

    # Opción inicial para que entre no bucle
    opcion = 0
    
    while opcion != 4:
        if opcion == 1: # escritura por pantalla
            df = getBolsa()
            print(df)
            
        elif opcion == 2: # escritura a ficheiro
            df = getBolsa()            

            # O usuario pode seleccionar o nome do ficheiro CSV
            fname = input('Nome do ficheiro: ')
            if len(fname) == 0:
                fname = "bolsa_{0}.csv".format(time.strftime("%Y%m%d_%H%M%S"))
            else:
                fname += '.csv'
            df.to_csv(fname)
                
            print('Táboa de valores gardada correctamente no ficheiro '\
            '"{0}"'.format(fname))

        elif opcion == 3: # Consulta cada X segs
            valor = input('Identificador do valor '\
            'bursatil que desexa consultar:')
            
            segundos = 0

            # O usuario é forzado a facer unha consulta cun retardo mínimo
            while segundos < 5:
                segundos = int(input('Periodicidade (s) [mínimo 5 segundos]:'))

            print('Prema "Ctrl+c" se desexa voltar ao menú')
            
            # Se existe o índice, devolvemos so seus valores cada X segundos
            try:
                while getIdentificadorBursatil(valor):            
                    time.sleep(segundos)
            except KeyboardInterrupt:
                pass
        else:
            pass
     
        #chamada ao menú
        menu()
        # Recóllese a opción do usuario
        opcion = int(input('Opción: '))
        
    if opcion == 4:
        print("Adeus")


     