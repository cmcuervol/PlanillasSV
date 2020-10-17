#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import datetime as dt

import xlwt
from Utils import Listador

Year_Eval = 2020

Path = os.getcwd()

Path_data = os.path.join(Path, 'BACEX')

Empresas = Listador(Path_data)

if  '.DS_Store' in Empresas:
    Empresas.remove('.DS_Store')

Positions = {'Llantas Automóvil'                             :401110,
             'Llantas Camión'                                :401120,
             'Llantas Moto'                                  :401140,
             'Llantas Bicicleta'                             :401150,
             'Llantas Especiales 1'                          :401170,
             'Llantas Especiales 2'                          :401180,
             'Llantas Especiales 3'                          :40129010,
             'Llantas Especiales 4'                          :40129020,
             'Llantas Especiales 5'                          :40129030,
             'Llantas Especiales 6'                          :401190,
             'Vehículos para transporte de 10 o más personas':8702,
             'Vehículos turismo'                             :8703,
             'Vehículos transporte de mercancías'            :8704,
             'Especiales'                                    :8705,
             'CVU cuatrimoto y moto de alto cilindraje'      :8711,
             'Bicicletas Eléctricas'                         :871160,
             'Bicicletas'                                    :8712,
             'CKD moto de combate'                           :9801,
              }


dimensions = {401110   :2,
              401120   :2,
              401140   :1,
              401150   :2,
              401170   :2,
              401180   :2,
              40129010 :2,
              40129020 :2,
              40129030 :2,
              401190   :2,
              8702     :2,
              8703     :2,
              8704     :2,
              8705     :2,
              8711     :1,
              871160   :1,
              8712     :1,
              9801     :1,
              }


def start_with(ID, List):
    """
    Find positions where a list start with an id
    INPUTS
    ID   : integer to search in the starts of the list
    List : List with the indexes where search te id
    """
    return [i for i in range(len(List)) if str(List[i]).startswith(str(ID))]

def SplitPartidas(DF, Partidas=Positions, Dimensiones=dimensions,):
    """
    Split BACEX DataFrame
    INPUTS
    indexes : List or array with indexes
    ids     : List of ids to search
    """

    split = pd.DataFrame([])
    for i in range(len(Partidas)):
        idx = start_with(list(Partidas.values())[i],DF.PARTIDA.values)
        if len(idx) != 0:
            Dim = [Dimensiones[list(Partidas.values())[i]]]*len(idx)
            if Year_Eval - DF.ANIO.iloc[idx[0]] == 1:
                Par = [u'Primer año inmediatamente anterior al año de evaluación']*len(idx)
            elif Year_Eval - DF.ANIO.iloc[idx[0]] == 2:
                Par = [u'SEGUNDO AÑO ANTERIOR AL AÑO DE EVALUACIÓN']*len(idx)

            df =  DF.iloc[idx]
            df.insert(0, 'Dimension',Dim, True )
            df.insert(1, 'Parámetro',Par, True )

            if len(split) == 0:
                split = df
            else:
                split.append(df)

    return split

S = pd.DataFrame([])
for i in range(len(Empresas)):
    Path_empresa = os.path.join(Path_data,Empresas[i])
    archivos = Listador(Path_empresa)
    company= pd.DataFrame([])
    for j in range(len(archivos)):
        Data = pd.read_excel(os.path.join(Path_empresa,archivos[j]))
        Split = SplitPartidas(DF=Data[['ANIO', 'MES', 'DIA', 'PARTIDA', 'NIT','cantidad', 'peso neto', 'numero de manifiesto',]])
        if len(Split) != 0:
            if len(company) == 0:
                company = Split
            else: company.append(Split, ignore_index=True)
    print(Empresas[i])
    if len(company) != 0:
        print('check')
        if len(S) == 0:
            S = company
            print('Initialized')
        else:
            S.append(company, ignore_index=True)
            print('Hello')












def AnlgWriter(P, DatesAnlg, YearsAnlg, BeginDate, EndDate, PlantNames, SheetNames, FileName):
    """
    Write file to flexibility analysis
    INPUTS
    P          : Array with forecast plant power  with dimensions [time, plants, scenario]
    DatesAnlg  : Array wit the indexes of each analogue years for each escenario,
    YearsAnlg  : list of year of the analogue
    BeginDate  : Initial date, to sort the results of the analogues
    EndDate    : End date, to sort the results of the analogues
    PlantNames : lis or array with the names of the plant
    SheetNames : names of the scenarios to write in each sheet
    FileName   : name of the file to save
    """

    dates = datetimer(BeginDate, EndDate, 1)

    wb = xlwt.Workbook()
    for s in range(len(SheetNames)):
        sheet = wb.add_sheet(SheetNames[s])  # Crear hoja decálculo
        sheet.write(0, 0, 'Fecha')

        for column, heading in enumerate(PlantNames, 1):
            sheet.write(0, column, str(heading))

        for i in range(P.shape[0]):
            sheet.write(i+1, 0, dates[i].strftime('%Y-%m-%d %H:00:00'))
            m = dates[i].month
            d = dates[i].day
            h = dates[i].hour
            try:
                # idx = np.where(DatesAnlg[s]==f'{YearsAnlg[s]}-{m}-{d} {h}:00:00')[0][0]
                idx = np.where(DatesAnlg[s]==pd.Timestamp(YearsAnlg[s],m,d,h))[0][0]
            except:
                # february 29th
                # idx = np.where(DatesAnlg[s]==f'{YearsAnlg[s]}-{m}-{d-1} {h}:00:00')[0][0]
                idx = np.where(DatesAnlg[s]==pd.Timestamp(YearsAnlg[s],m,d-1,h))[0][0]

            for j in range(P.shape[1]):
                sheet.write(i+1, j+1, P[idx,j,s])
    wb.save(FileName)
