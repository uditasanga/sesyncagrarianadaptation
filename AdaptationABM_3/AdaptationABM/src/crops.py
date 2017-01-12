class crop:
	def __init__(self, season, croptype, act_yield, exp_yield):
		self.season= str(season)
		self.croptype= croptype
		self.act_yield= int(act_yield)
		self.exp_yield= int(exp_yield)
		
	def evaluate(self):
		crop_loss= self.exp_yield - self.act_yield
		if crop_loss >0:
			household.adapt_strat= True
		
if __name__ == "__main__":
	
	pass
	
