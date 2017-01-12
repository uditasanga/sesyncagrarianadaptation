"""
reads point shapefile features (*.shp) and their attribute data (dBase)
Arika Ligmann-Zielinska, Michigan State University

Sources for readers:
pyShpIO.py
    Charles Schmidt, GeoDa Center
    Arizona State University, http://geodacenter.asu.edu
dbfUtils.py
    Raymond Hettinger
    http://code.activestate.com/recipes/users/178123/
"""

import pyShpIO as shploader
import dbfUtils as dbfloader

def readShpPointData(shpfile):
    if shpfile[-4:] != ".shp": # add the extension, if necessary
        shpfile += ".shp"
    shp=shploader.shp_file(shpfile)
    shapebase = []
    for i in shp:
        shapebase.append((i['X'],i['Y']))
    return shapebase

def readShpHeader(shpfile):
    if shpfile[-4:] != ".shp": # add the extension, if necessary
        shpfile += ".shp"
    shp=shploader.shp_file(shpfile)
    return shp.header 

def readDbfData(dbfile):
    if dbfile[-4:] != ".dbf": # add the extension, if necessary
        dbfile += ".dbf"
    dbf = open(dbfile,'rb')
    data_iter = dbfloader.dbfreader(dbf)
    data_iter.next(); data_iter.next() # skip the first two lines
    database = []
    for data in data_iter:
        data = [str(item).strip() for item in data]
        database.append(data)
    dbf.close()
    return database

if __name__ == "__main__":
    f_shp = "../data/shp/cows"
    header = readShpHeader(f_shp)
    points = readShpPointData(f_shp)
    data = readDbfData(f_shp)
    print "points",points[:3]
    print
    print "db",data[:3]
    print
    print "header info",header

