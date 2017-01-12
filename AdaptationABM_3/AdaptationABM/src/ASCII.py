#------------- SPECIFICATION ------------------------------------
#
# AUTHOR: Arika Ligmann-Zielinska
# CREATED ON: August 27, 2006
# LAST UPDATED: Feb 2016
#
# DESRCIPTION
#   Handles ASCII raster objects, requires numpy
#------------- FUNCTIONS ----------------------------------------
import numpy
import os.path

class Raster:

    def __init__(self,asciifile,datatype=int):
        """ASCII grid file full path name, (datatype = int, float)"""
        self.type = datatype
        self.file = asciifile
        if not os.path.exists(asciifile):
            raise IOError("File "+asciifile+" does not exist.")
        self.name = os.path.basename(asciifile)[:-4]
        self.ncols = None; self.nrows = None
        self.cellsize = None
        self.NODATA_value= None
        self.BB_Xmin = None; self.BB_Xmax = None
        self.BB_Ymin = None; self.BB_Ymax = None
        self.body = None
        try:
            self.getHeader()
            self.getBody()
        except IOError:
            print "Inappropriate file format."
        self.domain = []
        self.setDomain()

    def __str__(self):
        label = "Name: "+self.name+"\trows "+str(self.nrows)+\
                "\tcols "+str(self.ncols)+"\tValue list:\t"+\
                str(self.domain)+"\n"
        label += "B-BOX\nMin:  "+str(round(self.BB_Xmin,2))+\
                 " "+str(round(self.BB_Ymin,2))+"\tMax:  "+\
                 str(round(self.BB_Xmax,2))+" "+str(round(self.BB_Ymax,2))
        return label

    def getHeader(self):
        f = open(self.file, 'r')
        head = f.readlines()[:6]
        f.close()
        data = []
        for line in head:
            line = line.strip().split()
            data.append(line)
        # populate attributes
        self.ncols = int(data.pop(0)[1])
        self.nrows = int(data.pop(0)[1])
        self.NODATA_value = int(data.pop()[1])
        self.cellsize = int(data.pop()[1])
        # retrieve bounding box coords
        self.BB_Xmin = float(data.pop(0)[1])
        self.BB_Ymin = float(data.pop(0)[1])
        self.BB_Xmax = self.BB_Xmin+self.cellsize*float(self.ncols)
        self.BB_Ymax = self.BB_Ymin+self.cellsize*float(self.nrows)


    def getBody(self):
        f = open(self.file, 'r')
        rawdata = f.readlines()[6:]
        f.close()
        array2D = []
        for line in rawdata:
            row = map(float,line.strip().split())
            array2D.append(row)
        self.body = numpy.array(array2D,self.type)

    def setDomain(self):
        """Creates an exhaustive and exclusive list of raster body values"""
        self.domain= set(self.body.flatten())

    def valueAtXY(self,xcoord,ycoord):
        """Retrieve the value of the raster at input location xcoord, ycoord """
        # to obtain value at true projected coordinates
        # we need to convert these geo-coordinates into the numpy array indices
        # so that we can read the corresponding value of the 'body' attribute
        row = int((self.BB_Ymax-ycoord)/float(self.cellsize))
        col = int((xcoord-self.BB_Xmin)/float(self.cellsize))
        if (0 <= row and row < self.nrows) and\
           (0 <= col and col < self.ncols):
            return self.body[row,col]
        else:
            print "WARNING: Out of raster bounds, returning NoData value"
            return self.NODATA_value

if __name__ == "__main__":
    f_asc = "../data/food.asc"
    # create the FOOD raster object
    food = Raster(f_asc)
    print "raster info"
    print food
    print "first 5 cols in first 4 rows"
    print food.body[:3,:4]
    valXY = food.valueAtXY(405019,3839000)
    print valXY
    
    
