#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import datetime as dt

import xlwt
import xlsxwriter
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
            df.insert(1, 'Parametro',Par, True )

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
            else:
                company = company.append(Split, ignore_index=True)
    print(Empresas[i])
    if len(company) != 0:
        if len(S) == 0:
            S = company
        else:
            S = S.append(company, ignore_index=True)


Info  = S


header = ['Dimension','NIT','Parámetro','año','Subpartida arancelaria','I (Importación)','E (Exportación)','Fabricación Nacional','No de declaración de exportación','Fecha','Número de unidades importadas','Número de unidades exportadas','Número de unidades Fabricadas en Colombia','Peso bruto en kilogramos importados','Peso bruto en kilogramos exportados','Peso bruto en kilogramos de unidades Fabricadas en Colombia']

workbook  = xlsxwriter.Workbook('test.xlsx')
worksheet = workbook.add_worksheet()

date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
head_format = workbook.add_format()
head_format.set_align('center')
head_format.set_align('vcenter')
head_format.set_bold(True)
head_format.set_text_wrap()
# bold = workbook.add_format({'bold': True})

worksheet.set_row(0,111)
worksheet.set_column(0,0,  15.17)
worksheet.set_column(1,1,  10.67)
worksheet.set_column(2,2,  36.50)
worksheet.set_column(3,3,   6.33)
worksheet.set_column(4,4,  27.00)
worksheet.set_column(5,8,  18.50)
worksheet.set_column('J:J',11.00)
worksheet.set_column('K:K',20.17)
worksheet.set_column('L:N',15.17)
worksheet.set_column('O:P',14.17)

# for column, heading in enumerate(header):
#     worksheet.write(0, column, heading, bold)
worksheet.write_row(0,0, header, head_format)

worksheet.write_column(1,0, Info['Dimension'].values)
worksheet.write_column(1,1, Info['NIT']      .values)
worksheet.write_column(1,2, Info['Parámetro'].values)
worksheet.write_column(1,3, Info['ANIO']     .values)
worksheet.write_column(1,4, Info['PARTIDA']  .values)
worksheet.write_column(1,10,Info['cantidad'] .values.astype(float).astype(int))
worksheet.write_column(1,13,Info['peso neto'].values)

worksheet.write_column(1,5, ['x']*len(Info))
worksheet.write_column(1,11,[0]*len(Info))
worksheet.write_column(1,12,[0]*len(Info))
worksheet.write_column(1,14,[0]*len(Info))
worksheet.write_column(1,15,[0]*len(Info))

for i in range(Info.shape[0]):
    fecha = dt.datetime(Info['ANIO'].values[i], Info['MES'].values[i], Info['DIA'].values[i])
    worksheet.write_datetime(i+1, 9,fecha,date_format)
    try:
        worksheet.write_number(i+1,8,int(Info['numero de manifiesto'].values[i]))
    except:
        worksheet.write_string(i+1,8,'')

workbook.close()

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
