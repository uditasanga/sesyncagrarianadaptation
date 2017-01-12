import household from src 

#  CLASSes ---------------------------------
class Neighbor:
	def __init__(self,   ):
		
	def set_neighbors(self,distance,allblocks):
		neighs_ids=lookup[self.hhid]
		#neighbors=[nblock for nid in neighs_ids for nblock in allblocks if nblock.pid == nid]
		self.neighbors=neighbors 
		##pass

class ShapeMap:
	def __init__(self,BB_Xmin,BB_Ymin,BB_Xmax,BB_Ymax):
		"""the boundig box object"""
		self.BB_Xmin = BB_Xmin
		self.BB_Xmax = BB_Xmax
		self.BB_Ymin = BB_Ymin
		self.BB_Ymax = BB_Ymax

	def __str__(self):
		label = "Bounding Box\n"
		label += "Min:  "+str(round(self.BB_Xmin,2))+"\t"+str(round(self.BB_Ymin,2))
		label += "\tMax:  "+str(round(self.BB_Xmax,2))+"\t"+str(round(self.BB_Ymax,2))
		return label

#  FUNCTIONs ---------------------------------
#def setup(shp="../data/blocks",gal="../data/neighbors.gal"):
	#""" loads data and creates objects
		#returns the objects packed into a tuple in the following order
		#(shapemap, blocks)
	#"""
	#shapebase = reader.readShpPolyData(shp)
	#database = reader.readDbfData(shp)
	##load the gal file
	#with open(gal,'r')as f:
		#galdata=f.readlines()[1:]
	#lookup={}
	#for idx,line in enumerate(galdata):
		#if idx%2 == 0:
			#line1 = line.strip().split()
			#blockid=int(line1[0])
			#line2 = galdata[idx+1].strip().split()
			#neighs_ids=map(int,line2)
			#lookup[blockid] = neighs_ids
	#blocks = []
	#for geom,data in zip(shapebase,database):
		#pid,area, landprice = data
		#ablock = Block(pid,area,landprice,geom)
		#blocks.append(ablock)
	##getting neighbors	
	#for ablock in blocks:
		#ablock.set_neighborhood(lookup,blocks)
	##shape map
	#shpheader = reader.readShpHeader(shp)
	#shapemap = ShapeMap(shpheader['BBOX Xmin'], shpheader['BBOX Ymin'],shpheader['BBOX Xmax'], shpheader['BBOX Ymax'])
	#return (shapemap,blocks)
	
#if __name__ == "__main__":
	#shpmap, blocks = setup()
	#for j,block in enumerate(blocks):
		##print block
		##print "No. of neighbors",len(block.neighbors)
		#for nb in block.neighbors:
			#print nb
			
