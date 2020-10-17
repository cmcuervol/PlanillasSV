#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import datetime as dt


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
#                                Basic and system functions
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
def Listador(directorio, inicio=None, final=None):
    """
    Return the elements (files and directories) of any directory,
    optionaly with filter by start o end of the name of the element
    INPUTS
    directorio : route of the directory
    inicio     : start of the elements
    final      : end of the elements
    OUTPUTS
    lf  : list of elements
    """
    lf = []
    lista = os.listdir(directorio)
    lista.sort()
    if inicio == final == None:
        return lista
    else:
        for i in lista:
            if inicio == None:
                if i.endswith(final):
                    lf.append(i)
            if final == None:
                if i.startswith(inicio):
                    lf.append(i)
            if (inicio is not None) & (final is not None):
                if i.startswith(inicio) & i.endswith(final):
                    lf.append(i)
        return lf

def WriteDict(dict, filename, sept):
    """
    Write dictionary to file
    INPUTS
    dict     : dictionary to Write
    filename : absolute path and name wiht extention to save te files
    sept     : character(s) to separate keys and elements
    """
    with open(filename, 'w') as f:
        for key in dict.keys():
            f.write(f"{key}{sept}{dict[key]}\n")

def WriteFile(Data, NameFile, separator, DOS=True):
    """
    Write data in string on plain text file
    INPUTS
    Data      : list of data, each line is a list with the correspondient data
    NameFile  : Name of file to save (recomended with the absolute path)
    separator : separator of elements
    DOS       : bolean to convert to windows format
    """
    f = open(NameFile, 'w')
    for i in range(len(Data)):
        str_join = separator.join(x for x in Data[i])
        f.write(str_join+'\n')

    f.close()
    if DOS == True:
        os.system("perl -Mopen=OUT,:crlf -pi.bak -e0 "+NameFile)

def AdjustNameLength(names, length=12):
    """
    Adjust the name lengths to write the header in SDDP files
    IMPUTS
    names  : list of plant names
    length : maximum length by column in the SDDP file
    OUTPUTS
    Names  : list of names with the specif length
    """
    Names = []
    for n in names:
        name = n.replace(' ', '_')
        if len(name) <= length: #add espaces to reach the length length
            x = length -len(name)
            name += x*' '
        else: # cut to have only length caracters
            name = name[:length]

        Names.append(name)

    return Names


def FillSpaces(lista, length):
    """
    fill with blank spaces each element of a list, to reach some length
    INPUTS
    lista  : list or array with elements to fill
    length : length of caracters to reach
    """

    filled = [(length-len(elem))*' '+'{}'.format(elem) for elem in lista]

    return filled

def RemoveAcents(Names):
    """
    Put the plant type in the initial caracter (S or E), and remove the acents
    INPUTS
    Names : list of  names
    OUTPUTS
    List of plant names corrected
    """

    acent = [u'\xe1',u'\xe9', u'\xed', u'\xf3',u'\xfa']
    vowel = ['a', 'e', 'i', 'o', 'u']
    Nam   = Names.copy()
    for i in range(len(Names)):
        if Names[i][-1] == ')':
            Nam[i] = Names[i][-2]+'_'+Names[i][:-4]
        for j in range(len(acent)):
            if acent[j] in Names[i]:
                Nam[i] = Nam[i].replace(acent[j], vowel[j])
    return Nam


def datetimer(begin, end, delta):
    """
    Make a list of datetimes since beging to end, both includes, in every delta step
    INPUTS:
    begin: datetime of the initial date
    end  : datetime of the final date
    delta: hours of the step pass time between begin and end
    OUTPUTS:
    dates: list of datetimes
    """
    dates = []
    now   = begin

    while now <= end:
        dates.append(now)
        now += dt.timedelta(hours=delta)

    return dates

def UTC2local(dates, delta=-5):
    """
    Convert list of UTC dates to local time
    INPUTS:
    dates : list of datetimes in UTC time
    delta : offset of local time in hours respect to UTC time
    OUTPUTS
    local_time : list of datetimes in local time
    """
    if isinstance(dates, list):
        local_time = list(map(lambda t : t+dt.timedelta(hours=delta), dates))
    else:
        local_time = dates+dt.timedelta(hours=delta)
    return local_time

# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
#                      stadistical and timeseries functions
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
def Diff(f,x, order=1, tiempo=None):
    """calculate the derived df/dx
    IMPUTS
    f: array to derivated respect to x
    x: array
    order: order of the derived
    tiempo: optional. If x is a time array put anything, then cacule the derivated
            in time, x must be a datetime object, and the derivate calcules the
            difference in seconds
    OUTPUTS
    g: derived of f respect to x
    """

    # df_dx = np.zeros((len(f)-order, ), dtype= float)
    g = f
    for i in range(order):
        dg_dx = np.zeros((len(f)-(i+1), ), dtype= float)
        if tiempo==None:
            for i in range(len(f)-(i+1)):
                dg_dx[i]= (g[i+1]-g[i])/(x[i+1]-x[i])
        else:
            for i in range(len(f)-(i+1)):
                dg_dx[i]= (g[i+1]-g[i])/(x[i+1]-x[i]).seconds

        g = dg_dx

    return g

def Nearest(point, vector):
    """
    Find the position of the nearest vector's value from a given point
    IMPUTS
    point : value to need find the nearest point
    vector: list or array with points to compare
    OUPUTS
    idx : Position of the original vector with less distance from the ginven point
    """
    dif = abs(vector - point)
    idx = np.where(dif == min(dif))[0][0]
    return idx

def Conditioner(array, Threshold, condition):
    """
    Finds where occur any logic conditon in an array/list
    IMPUTS
    array     : array, list or tuple of data
    Threshold : limit value, or array/list/tuple with limits inferior an superior
    condition : Logic condition to evaluate
               '!='   different to value
               '=='   equal to value
               '<'    minor to value
               '<='   minor equal to value
               '>'    major to value
               '>='   major equal to value
               '><'   between the values
               '>=<'  major equal to left and minor to right
               '><='  major to left and minor equal to right
               '>=<=' major equal to left and minor equal to right
               '<>'   outside the values
               '<=>'  minor equal to left and major to right
               '<>='  minor to left and major equal to right
               '<=>=' minor equial to left and major equal to right
    RETURNS
    pos   : position of the changes different of the spected value
    """
    if isinstance(array, list):
        array = np.array(array)

    if isinstance(Threshold, (list, np.ndarray, tuple)):
        try:
            left  = Threshold[0]
            right = Threshold[1]
        except:
            print("put correctly the limit values, [left, right]")
        if condition == '><':
            idx = np.where((array >  left)&(array <  right))
        if condition == '>=<':
            idx = np.where((array >= left)&(array <  right))
        if condition == '><=':
            idx = np.where((array >  left)&(array <= right))
        if condition == '>=<=':
            idx = np.where((array >= left)&(array <= right))
        if condition == '<>':
            idx = np.where((array <  left)|(array >  right))
        if condition == '<=>':
            idx = np.where((array <= left)|(array >  right))
        if condition == '<>=':
            idx = np.where((array <  left)|(array >= right))
        if condition == '<=>=':
            idx = np.where((array <= left)|(array >= right))
    else:
        if condition == '!=':
            idx = np.where(array != Threshold)
        if condition == '==':
            idx = np.where(array == Threshold)
        if condition == '<':
            idx = np.where(array <  Threshold)
        if condition == '<=':
            idx = np.where(array <= Threshold)
        if condition == '>':
            idx = np.where(array >  Threshold)
        if condition == '>=':
            idx = np.where(array >= Threshold)
    return idx

def Salto(x, delta, condition='=='):
    """
    Finds the changes in a datetime array
    IMPUTS
    x        : array
    delta    : array's spected evolution value or list/array of the range [minutes]
    condition: Logic condition to evaluate
               '!='   different to value
               '=='   equal to value
               '<'    minor to value
               '<='   minor equal to value
               '>'    major to value
               '>='   major equal to value
               '><'   between the values
               '>=<'  major equal to left and minor to right
               '><='  major to left and minor equal to right
               '>=<=' major equal to left and minor equal to right
               '<>'   outside the values
               '<=>'  minor equal to left and major to right
               '<>='  minor to left and major equal to right
               '<=>=' minor equial to left and major equal to right
    RETURNS
    pos   : position of the evaluate change
    """
    # a = np.array(map(lambda i: x[i+1]-x[i], range(len(x)-1)))
    if isinstance(x,list):
        x = np.array(x)
    dif =  x[1:]-x[:-1]
    try:
        # pos = np.where(a!=delta)[0][0]
        pos = Conditioner(dif, delta, condition)[0]+1 # use an index left
    except:
        pos = 0
    return pos

def SaltoTime(x, delta, condition='=='):
    """
    Finds the changes in a datetime array
    IMPUTS
    x        : array of time
    delta    : array's spected evolution value or list/array of the range [minutes]
    condition: Logic condition to evaluate
               '!='   different to value
               '=='   equal to value
               '<'    minor to value
               '<='   minor equal to value
               '>'    major to value
               '>='   major equal to value
               '><'   between the values
               '>=<'  major equal to left and minor to right
               '><='  major to left and minor equal to right
               '>=<=' major equal to left and minor equal to right
               '<>'   outside the values
               '<=>'  minor equal to left and major to right
               '<>='  minor to left and major equal to right
               '<=>=' minor equial to left and major equal to right
    RETURNS
    pos   : position of the evaluate change
    """

    # time = np.array(list(map(lambda i: (x[i+1]-x[i]).days*24*60+(x[i+1]-x[i]).seconds // 60., range(len(x)-1))))
    if isinstance(x,list):
        x = np.array(x)
    time =  (x[1:]-x[:-1]).days*24*60 + (x[1:]-x[:-1]).seconds // 60.
    try:
        pos = Conditioner(time, delta, condition)[0]+1 # use an index left
    except:
        pos = 0
    return pos


def CleanArray(original, value=0, condition='==', mask_value='delete'):
    """
    Clean list or 1D array from te indicate values
    IMPUTS
    original : list or 1D array to Clean
    value    : value to clean, or array/list with limits inferior an superior
    condition: Logic condition to evaluate
               '!='   different to value
               '=='   equal to value
               '<'    minor to value
               '<='   minor equal to value
               '>'    major to value
               '>='   major equal to value
               '><'   between the values
               '>=<'  major equal to left and minor to right
               '><='  major to left and minor equal to right
               '>=<=' major equal to left and minor equal to right
               '<>'   outside the values
               '<=>'  minor equal to left and major to right
               '<>='  minor to left and major equal to right
               '<=>=' minor equial to left and major equal to right
    mask_value: Value to reemplace the select values, if is 'delete', delete the records
    OUTPUTS
    new : array cleaned
    """
    idx = Conditioner(original, value, condition)

    if mask_value == 'delete':
        new = np.delete(original, idx)
    else:
        new = original
        new[idx] = mask_value
    return new

def FindOutlier(serie,index=True,clean=True, xIQR=1.5, restrict_inf=None, restrict_sup=None):
    """
    Finds ouliers data in a series
    INPUTS
    serie : list or or 1d array
    index : boolean to return the indexes with outliers
    celar : boolean to return the serie without outliers
    xIQR  : Times of IQR are defined the limit to ouliers
    OUTPUTS
    ser : serie whitout ouliers if clean parameter are True
    idx : indexes of the oiliers if index parameter are True
    """
    Q25=np.nanpercentile(serie,25)
    Q75=np.nanpercentile(serie,75)
    IQR=(Q75-Q25)
    lim_inf = Q25 - xIQR*IQR
    lim_sup = Q75 + xIQR*IQR
    if restrict_inf is not None:
        if restrict_inf > lim_inf:
            lim_inf = restrict_inf
    if restrict_sup is not None:
        if restrict_sup > lim_sup:
            lim_sup = restrict_sup

    out = np.full(np.shape(serie),False, dtype=bool)
    out[serie>lim_sup] = True
    out[serie<lim_inf] = True

    if index == True:
        idx = np.where(out==True)[0]
        if clean == True:
            ser = serie[~out]
            return serie, idx
        else:
            return idx
    elif clean == True:
        ser = serie[~out]
        return serie
    else:
        return "Ashole, a least one of clean or index must be True"


def HistogramValues(Values, bins = 10):
    """
    Caclule the histogram of relative frecuencies, intervals change for bins middle points
    INPUTS
    Values : array of values
    bins   : integer of number bins
    OUTPUTS
    h      : relative frecuencies
    b      : Middle point of the histogram intervals
    """
    # Genera el histograma de valores
    val = Values[~np.isnan(Values)]
    h,b = np.histogram(val,bins=bins)
    h = h.astype(float); h = h / h.sum()
    b = (b[1:]+b[:-1])/2.0
    return h, b
