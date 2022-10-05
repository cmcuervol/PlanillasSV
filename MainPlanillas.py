#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from Plany import DataIEF, MetasIndividules, MetasTotales, ResumeInfo
from Plany import WriteIEF, WriteMetas

Path = os.getcwd()

Year_Eval = 2015
Desgaste  = 0.68
Meta_dim1 = 0.20
Meta_dim2 = 0.55


Info  = DataIEF(Year_Eval=Year_Eval, Desgaste=Desgaste, Path=Path)
WriteIEF(Info)
Goal, NameNIT = MetasIndividules(Info,Meta_dim1=Meta_dim1,Meta_dim2=Meta_dim2)
Meta_t = MetasTotales(Info,Meta_dim1=Meta_dim1,Meta_dim2=Meta_dim2)

WriteMetas(Goal, NameNIT,Meta_t)

Resume = ResumeInfo(Info.copy())
WriteIEF(Resume, nameFile='ResumenPlantillaInformacionIEF.xlsx')
