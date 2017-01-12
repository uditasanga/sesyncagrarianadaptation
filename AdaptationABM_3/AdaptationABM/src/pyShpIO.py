"""
A Pure Python ShapeFile Reader and Writer (selfcontained).
This module returns and expects dictionary based data strucutres.
This module should be wrapped into your native data strcutures.

Developer: Charles Schmidt, GeoDa Center, Arizona State University
Tempe, AZ, http://geodacenter.asu.edu
"""
import unittest
from struct import calcsize,unpack,pack
from cStringIO import StringIO
from itertools import izip,islice

import dbfUtils
    
#SHAPEFILE Globals
HEADERSTRUCT = (\
    ('File Code','i','>'),\
    ('Unused','5i','>'),\
    ('File Length','i','>'),\
    ('Version','i','<'),\
    ('Shape Type','i','<'),\
    ('BBOX Xmin','d','<'),\
    ('BBOX Ymin','d','<'),\
    ('BBOX Xmax','d','<'),\
    ('BBOX Ymax','d','<'),\
    ('BBOX Zmin','d','<'),\
    ('BBOX Zmax','d','<'),\
    ('BBOX Mmin','d','<'),\
    ('BBOX Mmax','d','<'))
RHEADERSTRUCT = (\
    ('Record Number','i','>'),\
    ('Content Length','i','>'))

def noneMax(a,b):
    if a is None:
        return b
    if b is None:
        return a
    return max(a,b)

def noneMin(a,b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a,b)

def _unpackDict(structure,fileObj):
    """Utility Function, Requires a Tuple of tuples that desribes the element structure...

    _unpackDict(structure tuple, fileObj file) -> dict
    
    Arguments:
        structure -- tuple of tuples -- (('FieldName 1','type','byteOrder'),
                                         ('FieldName 2','type','byteOrder'))
        fileObj -- file -- an open file at the correct position!
    Returns:
        {'FieldName 1': value, 'FieldName 2': value}
    Side Effects: 
        #file at new position """
    d = {}
    for name,dtype,order in structure:
        result = unpack(order+dtype,fileObj.read(calcsize(dtype)))
        if len(result) == 1:
            result = result[0]
        d[name] = result
    return d

def _packDict(structure,d):
    """Utility Function

    _packDict(structure tuple, d dict) -> str
    
    Arguments:
        structure -- tuple of tuples -- (('FieldName 1','type','byteOrder'),
                                         ('FieldName 2','type','byteOrder'))
        d -- dict -- {'FieldName 1': value, 'FieldName 2': value} """
    string = ''
    for name,dtype,order in structure:
        if len(dtype) > 1:
            string += pack(order+dtype,*d[name])
        else:
            string += pack(order+dtype,d[name])
    return string

class shp_file:
    """
    Reads and Writes the SHP compenent of a ShapeFile

    Attributes:
    header -- dict -- Contents of the SHP header. #For contents see: HEADERSTRUCT
    shape -- int -- ShapeType.

    Notes: The header of both the SHP and SHX files are indentical.

    """
    SHAPE_TYPES = {'POINT':1, 'ARC':3, 'POLYGON':5, 'MULTIPOINT':8, \
                   'POINTZ':11, 'ARCZ':13, 'POLYGONZ':15, \
                   'MULTIPOINTZ':18, 'POINTM':21, 'ARCM':23, \
                   'POLYGONM':25, 'MULTIPOINTM':28, 'MULTIPATCH':31}
    
    def __iswritable(self):
        try:
            assert self.__mode=='w'
        except AssertionError:
            raise IOError, "[Errno 9] Bad file descriptor"
        return True
    
    def __isreadable(self):
        try:
            assert self.__mode=='r'
        except AssertionError:
            raise IOError, "[Errno 9] Bad file descriptor"
        return True
    
    def __init__(self, fileName, mode = 'r', shape_type = None):
        self.__mode = mode
        if fileName.endswith('.shp') or fileName.endswith('.shx') or fileName.endswith('.dbf'):
            fileName = fileName[:-4]
        self.fileName = fileName

        if mode == 'r':
            self._open_shp_file()
        elif mode == 'w':
            if shape_type not in self.SHAPE_TYPES:
                raise Exception, 'Attempt to create shp/shx file of invalid type'
            self._create_shp_file(shape_type)
        else:
            raise Exception, 'Only "w" and "r" modes are supported'
        
    def _open_shp_file(self):
        """ 
        Opens a shp/shx file.

        shp_file(fileName string, 'r') -> Shpfile

        Arguments:
        filename -- the name of the file to create
        mode -- string -- 'r'
        shape_type -- None
        """
        self.__isreadable()
        fileName = self.fileName
        self.fileObj = open(fileName+'.shp', 'rb')
        self._shx = shx_file(fileName)
        self.header = _unpackDict(HEADERSTRUCT,self.fileObj)
        self.shape = TYPE_DISPATCH[self.header['Shape Type']]
        self.__lastShape = 0
        # localizing for convenience
        self.__numRecords = self._shx.numRecords
        # constructing bounding box from header
        h=self.header
        self.bbox=[h['BBOX Xmin'],h['BBOX Ymin'], 
                   h['BBOX Xmax'],h['BBOX Ymax']]
        self.shapeType = self.header['Shape Type']
        
    def _create_shp_file(self,shape_type):
        """ 
        Creates a shp/shx file.

        shp_file(fileName string, 'w', shape_type string) -> Shpfile

        Arguments:
        filename -- the name of the file to create
        mode -- string -- must be 'w'
        shape_type -- string -- the type of shp/shx file to create. must be one of  
                the following: 'POINT', 'POINTZ', 'POINTM',
                'ARC', 'ARCZ', 'ARCM', 'POLYGON', 'POLYGONZ', 'POLYGONM',
                'MULTIPOINT', 'MULTIPOINTZ', 'MULTIPOINTM', 'MULTIPATCH'
        """
        self.__iswritable()
        fileName = self.fileName
        self.fileObj = open(fileName+'.shp', 'wb')
        self._shx = shx_file(fileName,'w')
        self.header = {}
        self.header['Shape Type'] = self.SHAPE_TYPES[shape_type]
        self.header['Version'] = 1000
        self.header['Unused'] = (0,0,0,0,0)
        self.header['File Code'] = 9994
        self.__file_Length = 100
        self.header['File Length'] = 0
        self.header['BBOX Xmax'] = None
        self.header['BBOX Ymax'] = None
        self.header['BBOX Mmax'] = None
        self.header['BBOX Zmax'] = None
        self.header['BBOX Xmin'] = None
        self.header['BBOX Ymin'] = None
        self.header['BBOX Mmin'] = None
        self.header['BBOX Zmin'] = None
        self.shape = TYPE_DISPATCH[self.header['Shape Type']]
        #self.__numRecords = self._shx.numRecords
        
    def __len__(self):
        return self.__numRecords
    
    def __iter__(self):
        return self
    
    def type(self):
        return self.shape.String_Type
    
    def next(self):
        """returns the next Shape in the shapeFile
        """
        self.__isreadable()
        nextShape = self.__lastShape
        if nextShape == self._shx.numRecords:
            self.__lastShape = 0
            raise StopIteration
        else:
            self.__lastShape = nextShape+1
            return self.get_shape(nextShape)
        
    def __seek(self,pos):
        if pos != self.fileObj.tell():
            self.fileObj.seek(pos)
            
    def __read(self,pos,size):
        self.__isreadable()
        if pos != self.fileObj.tell():
            self.fileObj.seek(pos)
        return self.fileObj.read(size)
    
    def get_shape(self, shpId):
        self.__isreadable()
        if shpId+1 > self.__numRecords:
            raise IndexError
        fPosition,bytes = self._shx.index[shpId]
        self.__seek(fPosition)
        #the index does not include the 2 byte record header
        #(which contains, Record ID and Content Length)
        rec_id,con_len = _unpackDict(RHEADERSTRUCT,self.fileObj)
        return self.shape.unpack(StringIO(self.fileObj.read(bytes)))

    def __update_bbox(self,s):
        h = self.header
        if s.get('Shape Type') == 1:
            h['BBOX Xmax'] = noneMax( h['BBOX Xmax'], s.get('X') )
            h['BBOX Ymax'] = noneMax( h['BBOX Ymax'], s.get('Y') )
            h['BBOX Mmax'] = noneMax( h['BBOX Mmax'], s.get('M') )
            h['BBOX Zmax'] = noneMax( h['BBOX Zmax'], s.get('Z') )
            h['BBOX Xmin'] = noneMin( h['BBOX Xmin'], s.get('X') )
            h['BBOX Ymin'] = noneMin( h['BBOX Ymin'], s.get('Y') )
            h['BBOX Mmin'] = noneMin( h['BBOX Mmin'], s.get('M') )
            h['BBOX Zmin'] = noneMin( h['BBOX Zmin'], s.get('Z') )
        else:
            h['BBOX Xmax'] = noneMax( h['BBOX Xmax'], s.get('BBOX Xmax') )
            h['BBOX Ymax'] = noneMax( h['BBOX Ymax'], s.get('BBOX Ymax') )
            h['BBOX Mmax'] = noneMax( h['BBOX Mmax'], s.get('BBOX Mmax') )
            h['BBOX Zmax'] = noneMax( h['BBOX Zmax'], s.get('BBOX Zmax') )
            h['BBOX Xmin'] = noneMin( h['BBOX Xmin'], s.get('BBOX Xmin') )
            h['BBOX Ymin'] = noneMin( h['BBOX Ymin'], s.get('BBOX Ymin') )
            h['BBOX Mmin'] = noneMin( h['BBOX Mmin'], s.get('BBOX Mmin') )
            h['BBOX Zmin'] = noneMin( h['BBOX Zmin'], s.get('BBOX Zmin') )
        if not self.shape.HASM:
            self.header['BBOX Mmax'] = 0.0
            self.header['BBOX Mmin'] = 0.0
        if not self.shape.HASZ:
            self.header['BBOX Zmax'] = 0.0
            self.header['BBOX Zmin'] = 0.0

    def add_shape(self,s):
        self.__iswritable()
        self.__update_bbox(s)
        rec = self.shape.pack(s)
        con_len = len(rec)
        self.__file_Length += con_len+8
        rec_id,pos = self._shx.add_record(con_len)
        self.__seek(pos)
        self.fileObj.write(pack('>ii',rec_id,con_len/2))
        self.fileObj.write(rec)

    def close(self):
        self._shx.close(self.header)
        if self.__mode=='w':
            self.header['File Length'] = self.__file_Length / 2
            self.__seek(0)
            self.fileObj.write(_packDict(HEADERSTRUCT,self.header))
        self.fileObj.close()
        
class shx_file:
    """
    Reads and Writes the SHX compenent of a ShapeFile

    Attributes:
    index -- list -- Contains the file offset and len of each recond in the SHP component
    numRecords -- int -- Number of records

    """

    def __iswritable(self):
        try:
            assert self.__mode=='w'
        except AssertionError:
            raise IOError, "[Errno 9] Bad file descriptor"
        return True

    def __isreadable(self):
        try:
            assert self.__mode=='r'
        except AssertionError:
            raise IOError, "[Errno 9] Bad file descriptor"
        return True

    def __init__(self, fileName = None, mode = 'r'):
        self.__mode = mode
        if fileName.endswith('.shp') or fileName.endswith('.shx') or fileName.endswith('.dbf'):
            fileName = fileName[:-4]
        self.fileName = fileName

        if mode == 'r':
            self._open_shx_file()
        elif mode == 'w':
            self._create_shx_file()

    def _open_shx_file(self):
        """ Opens the SHX file.
    
        shx_file(filename,'r') --> shx_file
        
        Arguments:
        filename -- string -- extension is optional, will remove '.dbf','.shx','.shp' and append '.shx'
        mode -- string -- Must be 'r'
        """
        self.__isreadable()
        self.fileObj = open(self.fileName+'.shx', 'rb')
        self._header = _unpackDict(HEADERSTRUCT,self.fileObj)
        self.numRecords = numRecords = (self._header['File Length'] - 50)/4
        index = {}
        fmt = '>%di'%(2*numRecords)
        size = calcsize(fmt)
        dat = unpack(fmt,self.fileObj.read(size))
        self.index = [(dat[i]*2,dat[i+1]*2) for i in xrange(0,len(dat),2)]

    def _create_shx_file(self):
        """ Creates the SHX file.
    
        shx_file(filename,'w') --> shx_file
        
        Arguments:
        filename -- string -- extension is optional, will remove '.dbf','.shx','.shp' and append '.shx'
        mode -- string -- Must be 'w'
        """
        self.__iswritable()
        self.fileObj = open(self.fileName+'.shx', 'wb')
        self.numRecords = 0
        self.index = []
        self.__offset = 100 #length of header
        self.__next_rid = 1 #record IDs start at 1
        
    def add_record(self,size):
        """ Add a record to the shx index.

        add_record(size int) --> RecordID int

        Arguments:
        size -- int -- the length of the record in bytes NOT including the 8byte record header
    
        Returns:
        rec_id -- int -- the sequential record ID, 1-based.

        Note: the SHX records contain (Offset, Length) in 16-bit words.
        """
        self.__iswritable()
        pos = self.__offset
        rec_id = self.__next_rid
        self.index.append((self.__offset,size))
        self.__offset += size+8 #the 8byte record Header.
        self.numRecords += 1
        self.__next_rid += 1
        return rec_id,pos
    
    def close(self,header):
        if self.__mode=='w':
            self.__iswritable()
            header['File Length'] = (self.numRecords*calcsize('>ii')+100)/2
            self.fileObj.seek(0)
            self.fileObj.write(_packDict(HEADERSTRUCT,header))
            fmt = '>%di'%(2*self.numRecords)
            values = []
            for off,size in self.index:
                values.extend([off/2,size/2])
            self.fileObj.write(pack(fmt,*values))
        self.fileObj.close()

class NullShape:
    Shape_Type = 0
    STRUCT = (('Shape Type','i','<'))
    def unpack(self):
        return None
    def pack(self,x=None):
        return pack('<i',0)
    
class Point(object):
    """ Packs and Unpacks a ShapeFile Point Type 
    """
    Shape_Type = 1
    String_Type = 'POINT'
    HASZ = False
    HASM = False
    STRUCT = (('Shape Type','i','<'),\
              ('X','d','<'),\
              ('Y','d','<'))
    @classmethod
    def unpack(cls,dat):
        return _unpackDict(cls.STRUCT,dat)
    @classmethod
    def pack(cls,record):
        rheader = _packDict(cls.STRUCT,record)
        return rheader
    
class PolyLine:
    """ Packs and Unpacks a ShapeFile PolyLine Type 
    """
    HASZ = False
    HASM = False
    String_Type = 'ARC'
    STRUCT = (('Shape Type','i','<'),\
              ('BBOX Xmin','d','<'),\
              ('BBOX Ymin','d','<'),\
              ('BBOX Xmax','d','<'),\
              ('BBOX Ymax','d','<'),\
              ('NumParts','i','<'),\
              ('NumPoints','i','<'))
    @classmethod
    def unpack(cls,dat):
        record = _unpackDict(cls.STRUCT,dat)
        contentStruct = (('Parts Index','%di'%record['NumParts'],'<'),\
                         ('Vertices','%dd'%(2*record['NumPoints']),'<'))
        record.update(_unpackDict(contentStruct,dat))
        #record['Vertices'] = [(record['Vertices'][i],record['Vertices'][i+1]) for i in xrange(0,record['NumPoints']*2,2)]
        verts = record['Vertices']
        #Next line is equivalent to: zip(verts[::2],verts[1::2])
        record['Vertices'] = list(izip( islice(verts,0,None,2), islice(verts,1,None,2) ))
        if not record['Parts Index']:
            record['Parts Index'] = [0]
        return record
    @classmethod
    def pack(cls,record):
        rheader = _packDict(cls.STRUCT,record)
        contentStruct = (('Parts Index','%di'%record['NumParts'],'<'),\
                         ('Vertices','%dd'%(2*record['NumPoints']),'<'))
        content = {}
        content['Parts Index'] = record['Parts Index']
        verts = []
        [verts.extend(vert) for vert in record['Vertices']]
        content['Vertices'] = verts
        content = _packDict(contentStruct,content)
        return rheader+content

class Polygon(PolyLine):
    """ Packs and Unpacks a ShapeFile Polygon Type
    Indentical to PolyLine.
    """
    String_Type = 'POLYGON'


class MultiPoint:
    def __init__(self):
        raise NotImplementedError, "No MultiPoint Support at this time."
class PointZ:
    def __init__(self):
        raise NotImplementedError, "No PointZ Support at this time."
class PolyLineZ:
    def __init__(self):
        raise NotImplementedError, "No PolyLineZ Support at this time."
class PolygonZ:
    def __init__(self):
        raise NotImplementedError, "No PolygonZ Support at this time."
class MultiPointZ:
    def __init__(self):
        raise NotImplementedError, "No MultiPointZ Support at this time."
class PointM:
    def __init__(self):
        raise NotImplementedError, "No PointM Support at this time."
class PolyLineM:
    def __init__(self):
        raise NotImplementedError, "No PolyLineM Support at this time."
class PolygonM:
    def __init__(self):
        raise NotImplementedError, "No PolygonM Support at this time."
class MultiPointM:
    def __init__(self):
        raise NotImplementedError, "No MultiPointM Support at this time."
class MultiPatch:
    def __init__(self):
        raise NotImplementedError, "No MultiPatch Support at this time."

TYPE_DISPATCH= {0:NullShape, 1:Point, 3:PolyLine, 5:Polygon, \
                8:MultiPoint, 11:PointZ, 13:PolyLineZ, 15:PolygonZ, \
                18:MultiPointZ, 21:PointM, 23:PolyLineM, 25:PolygonM, \
                28:MultiPointM, 31:MultiPatch, 'POINT':Point, \
                'POINTZ':PointZ, 'POINTM':PointM, 'ARC':PolyLine, \
                'ARCZ':PolyLineZ, 'ARCM':PolyLineM, 'POLYGON':Polygon, \
                'POLYGONZ':PolygonZ, 'POLYGONM':PolygonM, \
                'MULTIPOINT':MultiPoint, 'MULTIPOINTZ':MultiPointZ, \
                'MULTIPOINTM':MultiPointM, 'MULTIPATCH':MultiPatch}

