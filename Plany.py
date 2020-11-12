#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import datetime as dt

from tqdm import tqdm
import xlsxwriter
import random
from Utils import Listador

Year_Eval = 2020

Path = os.getcwd()

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
             # 'Bicicletas Eléctricas'                         :871160,
             'Bicicletas'                                    :8712,
             'CKD moto de combate'                           :9801,
              }


dimensions = {401110   :2,
              401120   :2,
              401140   :1,
              401150   :1,
              401170   :1,
              401180   :1,
              40129010 :1,
              40129020 :1,
              40129030 :1,
              401190   :1,
              8702     :2,
              8703     :2,
              8704     :2,
              8705     :1,
              8711     :1,
              # 871160   :1,
              8712     :1,
              9801     :1,
              }

Peso_relation = {8702     :[401120],
                 8703     :[401110],
                 8704     :[401120],
                 8705     :[401170,401180,401190],
                 8711     :[401140],
                 8712     :[401150],
                 9801     :[401140],
                 }

PesoUnit = {8702: 24.713224368499258,
            8703: 5,
            8704: 40,
            8705: 50,
            8711: 2.5,
            8712: 0.7882352941176471,
            9801: 2.5}

Tire_units = {8702     :6,
              8703     :4,
              8704     :4 ,
              8705     :4,
              8711     :2,
              8712     :2,
              9801     :2,
              }


def start_with(ID, List):
    """
    Find positions where a list start with an id
    INPUTS
    ID   : integer to search in the starts of the list
    List : List with the indexes where search te id
    """
    return [i for i in range(len(List)) if str(List[i]).startswith(str(ID))]

def SplitPartidas(DF, Year_Eval=Year_Eval, Partidas=Positions, Dimensiones=dimensions,):
    """
    Split BACEX DataFrame
    INPUTS
    DF         : DataFrame with the readed data from BACEX database
    Year_Eval  : year of the evaluation
    Partidas   : dictionary with the inital numbers of arancelary partidas
    Dimensiones: dictionary with the number of dimensions asociated with partida

    """

    split = pd.DataFrame([])
    for i in range(len(Partidas)):
        idx = start_with(list(Partidas.values())[i],DF.PARTIDA.values)
        if len(idx) != 0:
            Dim = [Dimensiones[list(Partidas.values())[i]]]*len(idx)
            if Year_Eval - DF.ANIO.iloc[idx[0]] == 1:
                Par = [u'Primer año inmediatamente anterior al año de evaluación']*len(idx)
            elif Year_Eval - DF.ANIO.iloc[idx[0]] == 2:
                # Par = [u'SEGUNDO AÑO ANTERIOR AL AÑO DE EVALUACIÓN']*len(idx)
                Par = [u'Segundo año anterior al año de evaluación']*len(idx)
            else:
                continue

            fechas = []
            for t in range(len(idx)):
                fechas.append(dt.datetime(DF.ANIO.iloc[idx[t]],DF.MES.iloc[idx[t]],DF.DIA.iloc[idx[t]]))

            df =  DF.iloc[idx]
            df.insert(0, 'Dimension',Dim, True)
            df.insert(1, 'Parametro',Par, True)
            df.insert(2, 'Fecha', fechas, True)
            if len(split) == 0:
                split = df
            else:
                split = split.append(df)

    return split

def FixWeigthUnits(DF, weigth=Peso_relation, PesoUnit=PesoUnit, Units=Tire_units):
    """
    Change the weiths and units in the items related
    INPUTS
    DF     :   DataFrame with the data
    weigth : dictionary to search te min weigth in a item class
    units  : dictionary with te relation of units of tires per item
    """
    # uw = DF['peso neto'].values.astype(float)/DF['cantidad'].values.astype(float)
    # PesoUnit = {}
    # for i in range(len(weigth)):
    #     tires = list(weigth.values())[i]
    #     Pmin  = []
    #     for j in range(len(tires)):
    #         idx = start_with(tires[j],DF.PARTIDA.values)
    #         Pmin.append(uw[idx].min())
    #     PesoUnit.update({list(weigth.keys())[i]: np.min(Pmin)})

    for i in range(len(Units)):
        idx = start_with(list(Units.keys())[i],DF.PARTIDA.values)
        if list(Units.keys())[i] != 8704:
            DF['cantidad'].iloc[idx] = DF['cantidad'].iloc[idx].values * list(Units.values())[i]
        else:
            DF['cantidad'].iloc[idx] = DF['cantidad'].iloc[idx].values * random.choices([6,10], weights=(80,20))[0]

        # DF['peso neto'].iloc[idx] = DF['cantidad'].iloc[idx] * PesoUnit[list(Units.keys())[i]] * Units[list(Units.keys())[i]]
        DF['peso neto'].iloc[idx] = DF['cantidad'].iloc[idx] * PesoUnit[list(Units.keys())[i]]

    return DF


def DataIEF(Year_Eval=Year_Eval, Partidas=Positions, Dimensiones=dimensions, Path=Path ):
    """
    get IEF data
    INPUTS
    Year_Eval  : year of the evaluation
    Partidas   : dictionary with the inital numbers of arancelary partidas
    Dimensiones: dictionary with the number of dimensions asociated with partida
    Path       : absolute path to search the data
    """
    Path_data = os.path.join(Path, 'BACEX')
    Empresas = Listador(Path_data)

    if  '.DS_Store' in Empresas:
        Empresas.remove('.DS_Store')

    S = pd.DataFrame([])
    pbar = tqdm(total=len(Empresas), desc='Leyendo BACEX: ')
    for i in range(len(Empresas)):
        Path_empresa = os.path.join(Path_data,Empresas[i])
        archivos = Listador(Path_empresa)
        company= pd.DataFrame([])
        for j in range(len(archivos)):
            Data = pd.read_excel(os.path.join(Path_empresa,archivos[j]))
            Data.insert(0, 'Empresa',[i]*len(Data), True)
            Data.insert(0, 'Nombre',[Empresas[i]]*len(Data), True)
            Split = SplitPartidas(DF=Data[['Empresa', 'Nombre','ANIO', 'MES', 'DIA', 'PARTIDA', 'NIT','cantidad', 'peso neto',]],
                                  Year_Eval=Year_Eval,
                                  Partidas=Partidas,
                                  Dimensiones=Dimensiones)
            if len(Split) != 0:
                if len(company) == 0:
                    company = Split
                else:
                    company = company.append(Split, ignore_index=True)
        # print(Empresas[i])
        if len(company) != 0:
            if len(S) == 0:
                S = company.sort_values(by=['Fecha'])
            else:
                S = S.append(company.sort_values(by=['Fecha']) , ignore_index=True)
        pbar.update(1)
    pbar.close()
    S['cantidad'] = S['cantidad'].values.astype(float).astype(int)
    S = FixWeigthUnits(S)
    return S

def ResumeInfo(Data):
    """
    Resume the data acumulate by partida, company and year
    INPUTS
    Data : DataFrame with total information
    """
    Res = pd.DataFrame([],columns=Data.columns)
    Empresas = np.unique(Data.Empresa)
    pbar = tqdm(total=len(Empresas), desc='Acumulando por partidas: ')
    for Emp in Empresas:
        Company = Data[Data.Empresa==Emp]
        # print(f'Empresa: {Emp}')
        for y in np.unique(Company.ANIO):
            Year = Company[Company.ANIO==y]
            # print(f'Year {y}')
            for P in np.unique(Year.PARTIDA):
                Part = Year[Year.PARTIDA==P]
                Res = Res.append(Part.iloc[0])
                Res['Fecha']    .iloc[-1] = dt.datetime(y,12,31)
                Res['MES']      .iloc[-1] = 12
                Res['DIA']      .iloc[-1] = 31
                Res['cantidad'] .iloc[-1] = Part['cantidad'].sum()
                Res['peso neto'].iloc[-1] = Part['peso neto'].sum()
        pbar.update(1)
    pbar.close()
    return Res
def MetasIndividules(Info):
    """
    Calculate the total goals  for each company
    INPUTS
    Info : DataFrame with the data consolidated for all companies
    OUTPUTS
    Metas : Dictionary with thw folowing information
    IMPORTACIONES 2018				IMPORTACIONES 2019				META
    DIMENSIÓN 1		DIMENSIÓN 2		DIMENSIÓN 1		DIMENSIÓN 2		DIMENSIÓN 1		DIMENSIÓN 2
    UNIDADES	KG	UNIDADES	KG	UNIDADES	KG	UNIDADES	KG	UNIDADES	KG	UNIDADES	KG
    """

    Compn = np.unique(Info['Empresa'].values)
    goal = np.zeros((Compn.shape[0],12), dtype=float)
    Metas = []
    for i in range(Compn.shape[0]):
        idn   = np.where(Info['Empresa'].values == Compn[i])[0]
        name  = Info['Nombre'].iloc[idn[0]]
        NIT   = Info['NIT'].iloc[idn[0]]
        dim   = Info['Dimension'].iloc[idn].values
        years = Info['ANIO'].iloc[idn].values
        ndim  = np.unique(dim)
        nyear = np.unique(Info['ANIO'].iloc[idn].values)

        Metas.append([name, NIT])
        for d in ndim:
            idd = np.where(dim==d)[0]
            if d == 1:
                goal[i,-4] = 0.5*np.sum(Info['cantidad' ].iloc[idn[idd]]) * 0.25
                goal[i,-3] = 0.5*np.sum(Info['peso neto'].iloc[idn[idd]]) * 0.25
            if d == 2:
                goal[i,-2] = 0.5*np.sum(Info['cantidad' ].iloc[idn[idd]]) * 0.60
                goal[i,-1] = 0.5*np.sum(Info['peso neto'].iloc[idn[idd]]) * 0.60

            for j, y in enumerate(nyear):
                idy = np.where(years[idd] == y)[0]
                if d == 1:
                    goal[i,4*j+0] = 0.5*np.sum(Info['cantidad' ].iloc[idn[idd[idy]]]) * 0.25
                    goal[i,4*j+1] = 0.5*np.sum(Info['peso neto'].iloc[idn[idd[idy]]]) * 0.25
                if d == 2:
                    goal[i,4*j+2] = 0.5*np.sum(Info['cantidad' ].iloc[idn[idd[idy]]]) * 0.60
                    goal[i,4*j+3] = 0.5*np.sum(Info['peso neto'].iloc[idn[idd[idy]]]) * 0.60
    Metas = np.array(Metas)

    return goal, Metas

def MetasTotales(Info):
    """
    Calculate the total goals
    INPUTS
    Info : DataFrame with the data consolidated for all companies
    """

    dim  = Info['Dimension'].values
    n_dim = np.unique(dim)
    for j in n_dim:
        idd = np.where(dim==j)[0]
        if j == 1:
            Meta1_u = 0.5*np.sum(Info['cantidad' ].iloc[idd]) * 0.25
            Meta1_p = 0.5*np.sum(Info['peso neto'].iloc[idd]) * 0.25
        if j == 2:
            Meta2_u = 0.5*np.sum(Info['cantidad' ].iloc[idd]) * 0.60
            Meta2_p = 0.5*np.sum(Info['peso neto'].iloc[idd]) * 0.60

    return [Meta1_u,Meta1_p,Meta2_u,Meta2_p]

def WriteIEF(Info, nameFile='PlantillaInformacionIEF.xlsx', Path=Path):
    """
    Write planilla IEF
    INPUTS
    Info     : DataFrame with the information
    nameFile : Name to save excell workbook
    Path     : Absolute path to save file
    """
    header = ['Dimension','NIT','Parámetro','año','Subpartida arancelaria','I (Importación)','E (Exportación)','Fabricación Nacional','No de declaración de exportación','Fecha','Número de unidades importadas','Número de unidades exportadas','Número de unidades Fabricadas en Colombia','Peso bruto en kilogramos importados','Peso bruto en kilogramos exportados','Peso bruto en kilogramos de unidades Fabricadas en Colombia']

    workbook  = xlsxwriter.Workbook(os.path.join(Path,nameFile))
    worksheet = workbook.add_worksheet('Información Importaciones Ll')

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
    worksheet.write_column(1,2, Info['Parametro'].values)
    worksheet.write_column(1,3, Info['ANIO']     .values)
    worksheet.write_column(1,4, Info['PARTIDA']  .values)
    worksheet.write_column(1,10,Info['cantidad'] .values.astype(float).astype(int))
    worksheet.write_column(1,13,Info['peso neto'].values)

    worksheet.write_column(1,5, ['x']*len(Info))
    worksheet.write_column(1,11,[ 0 ]*len(Info))
    worksheet.write_column(1,12,[ 0 ]*len(Info))
    worksheet.write_column(1,14,[ 0 ]*len(Info))
    worksheet.write_column(1,15,[ 0 ]*len(Info))

    for i in range(Info.shape[0]):
        fecha = dt.datetime(Info['ANIO'].values[i], Info['MES'].values[i], Info['DIA'].values[i])
        worksheet.write_datetime(i+1, 9,fecha,date_format)
        # try:
        #     worksheet.write_number(i+1,8,int(Info['numero de manifiesto'].values[i]))
        # except:
        #     worksheet.write_string(i+1,8,'')

    workbook.close()

def WriteMetas(Vals_ind, NameNIT, Meta_total, nameFile='Metas.xlsx', Path=Path):
    """
    Write goals
    INPUTS
    Vals_ind : array with values of metas for each company
    NameNIT  : Name and NIT of each company
    Meta_ind : dictionary with goals per company ['Empresa','Dimension 1 [unidades]', 'Dimension 1 [kg]','Dimension 2 [unidades]', 'Dimension 2 [kg]']
    Meta_ind : List of goals of all companies ['Dimension 1 [unidades]', 'Dimension 1 [kg]','Dimension 2 [unidades]', 'Dimension 2 [kg]']
    nameFile : Name to save excell workbook
    Path     : Absolute path to save file
    """

    header_tot = ['Dimension 1 [unidades]', 'Dimension 1 [kg]','Dimension 2 [unidades]', 'Dimension 2 [kg]']

    workbook  = xlsxwriter.Workbook(os.path.join(Path,nameFile))
    merge_format = workbook.add_format({'align': 'center','valign':'vcenter','bold':True})
    date_format  = workbook.add_format({'num_format': 'd mmmm yyyy'})
    head_format  = workbook.add_format()
    head_format.set_align('center')
    head_format.set_align('vcenter')
    head_format.set_bold(True)
    head_format.set_text_wrap()
    # bold = workbook.add_format({'bold': True})

    worksheet = workbook.add_worksheet('MetasIndividules')
    # worksheet.set_row(0,50)
    worksheet.set_column(0,0,  100)
    worksheet.set_column(1,14,  15)

    worksheet.merge_range('A1:A3', 'Empresa', merge_format)
    worksheet.merge_range('B1:B3', 'NIT',     merge_format)

    worksheet.merge_range('C1:F1', f'IMPORTACIONES {Year_Eval-2}', merge_format)
    worksheet.merge_range('G1:J1', f'IMPORTACIONES {Year_Eval-1}', merge_format)
    worksheet.merge_range('K1:N1', 'META', merge_format)

    worksheet.merge_range('C2:D2', 'DIMENSION 1', merge_format)
    worksheet.merge_range('E2:F2', 'DIMENSION 2', merge_format)
    worksheet.merge_range('G2:H2', 'DIMENSION 1', merge_format)
    worksheet.merge_range('I2:J2', 'DIMENSION 2', merge_format)
    worksheet.merge_range('K2:L2', 'DIMENSION 1', merge_format)
    worksheet.merge_range('M2:N2', 'DIMENSION 2', merge_format)




    worksheet.write_row(2,2, ['UNIDADES', 'KG']*6, head_format)
    worksheet.write_column(3,0, NameNIT[:,0])
    worksheet.write_column(3,1, NameNIT[:,1])
    for i in range(Vals_ind.shape[1]):
        worksheet.write_column(3,2+i, Vals_ind[:,i])




    sheet = workbook.add_worksheet('MetasTotales')
    sheet.set_row(0,50)
    sheet.set_column(0,4,  20)


    sheet.write_row(0,0, header_tot, head_format)
    for i in range(len(Meta_total)):
        sheet.write(1,i, Meta_total[i])

    workbook.close()

Info  = DataIEF()
WriteIEF(Info)
Goal, NameNIT = MetasIndividules(Info)
Meta_t = MetasTotales(Info)

WriteMetas(Goal, NameNIT,Meta_t)

Resume = ResumeInfo(Info.copy())
WriteIEF(Resume, nameFile='ResumenPlantillaInformacionI EF.xlsx')
