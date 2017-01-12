#Forecast infomation for households 

import pshapes, household 


class forecast:
	def __init__(self,HH_ID, weathe_forecast_access):
		self.HH_ID = HH_ID
		self. access= weathe_forecast_access
	def __str__(self):
		info_object = 'Household'+ str(self.HH_ID)+\
		'access '+ str(self.access)
		return info_object
		
		
if __name__=="__main__":

	# loading the data
	hh = "../data/bihar5"
	#shapebase = pshapes.readShpPointData(hh)
	database = pshapes.readDbfData(hh)
	forecast_info =[]
	for infodata in database:
		HH_ID, weathe_forecast_access = infodata
		#x,y = points
		fore_info= forecast(infodata)
		forecast_info.append(fore_info)

	#display forecast information
	for forecast in forecast_info:
		print forecast

	
	
	
	
