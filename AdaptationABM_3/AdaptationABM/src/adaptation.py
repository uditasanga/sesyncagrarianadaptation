"""Adaptation to CC model
   ADAPT-PMT model
   Udita Sanga and Hogeun Park"""
   

    
class crop:
	def __init__(self,HHID, cc_crop_impact,climate_event_type,crop_affected, exp_yield, act_yield, price_loss,rice_major_risk,wheat_major_risk, maize_major_risk):
		self.HHID= HHID
		self.cc_crop_impact= cc_crop_impact
		self.climate_event_type= climate_event_type
		self.crop_affected= crop_affected
		self.exp_yield=exp_yield
		self.act_yield= act_yield
		self.price_loss= price_loss 
		self._rice_major_risk= rice_major_risk 
		self.wheat_major_risk= wheat_major_risk 
		self.maize_major_risk= maize_major_risk 
		self.adapt_score= 0 
		
	def PMT_decision:
		if self.act_yield > exp_yield: # if actual yield is greater than expected yield, farmer does not take any adaptation measures  
			perceived_exposure = 0
		else:
			perceived_exposure = (self.exp_yield- self.act_yield)  # Weighted to 0.2 
	
	def percieved_severity:
		if 
		
	def adaptation_efficacy:
		
	def self_efficacy:
		
	def adaptation_cost:
		
if __name__ == '__main__':
	import csv
    crop = "../data/crop.csv"
    with open(crop,'rb') as csvfile:
		cropdata= csv.reader(csvfile, delimiter=' ', quotechar='|')
		for row in cropdata:
			print ','.join(row)
    
    dbf = open(dbfile,'rb')
    data_iter = dbfloader.dbfreader(dbf)
    data_iter.next(); data_iter.next() # skip the first two lines
    database = []
    for data in data_iter:
        data = [str(item).strip() for item in data]
        database.append(data)
    dbf.close()
    return database
    
    
    
    
    
    

    # cows
    shapebase = pshapes.readShpPointData(pts)
    database = pshapes.readDbfData(pts)
    cattle = []

    for point, pointdata in zip(shapebase, database):
        pid, mites ###dat# = pointdata
        x, y = point
        cow = Cow(pid, mites, x, y)
        if cow.MITE_COUNT == 1:
            parasite = Mite()
            cow.mites.append(parasite)
        cattle.append(cow)

    for cow in cattle:
        print cow

    shpheader = pshapes.readShpHeader(pts)
    shapemap = ShapeMap(shpheader["BBOX Xmin"], shpheader["BBOX Ymin"], shpheader["BBOX Xmax"], shpheader["BBOX Ymax"])
    print shapemap

		
	
		
if __name__ == "__main__":
	
	pass
	
