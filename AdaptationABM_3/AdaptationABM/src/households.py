"""Adaptation to CC model
   ADAPT-PMT model
   Udita Sanga and Hogeun Park"""
import numpy as np
import random


class household:
    """Cognitive model of farmers decision making when faced with adaptation choices"""

    def __init__(self, hhid, X_COORD, Y_COORD, cultivated, CC_awareness, Access_weathe_forecast, CC_CROP_IMPACT,
                 Rice_major_risk, Wheat_major_risk, maiz_major_risk, drought_type, dro_strategy_used, dro_A1_adaptcost,
                 fld_type, fld_strategy_used, fld_A1_adaptcost, event_type, crop_affected, exp_yield, act_yield,
                 price_loss, yearly_income, monthly_income, Social_Capital, SC_strength, diverse_information, dro_occ,
                 dro_event, fld_occ, fld_event, perceived_exposure):
        self.HHID = int(hhid)
        self.X_COORD = float(X_COORD)
        self.Y_COORD = float(Y_COORD)
        self.cultivated = float(cultivated)
        self.CC_awareness = float(CC_awareness)
        self.Access_weathe_forecast = float(Access_weathe_forecast)
        self.CC_CROP_IMPACT = float(CC_CROP_IMPACT)
        self.Rice_major_risk = float(Rice_major_risk)
        self.Wheat_major_risk = float(Wheat_major_risk)
        self.maiz_major_risk = float(maiz_major_risk)
        self.drought_type = float(drought_type)
        self.dro_strategy_used = float(dro_strategy_used)
        self.dro_A1_adaptcost = float(dro_A1_adaptcost)
        self.fld_type = float(fld_type)
        self.fld_strategy_used = float(fld_strategy_used)
        self.fld_A1_adaptcost = float(fld_A1_adaptcost)
        self.event_type = float(event_type)
        self.crop_affected = float(crop_affected)
        self.exp_yield = float(exp_yield)
        self.act_yield = float(act_yield)
        self.price_loss = float(price_loss)
        self.yearly_income = float(yearly_income)
        self.monthly_income = float(monthly_income)
        self.Social_Capital = float(Social_Capital)
        self.SC_strength = float(SC_strength)
        self.adaptation_score = 0
        self.perceived_exposure = float(perceived_exposure)
        self.perceived_severity = 0
        self.self_efficacy = 0
        self.adapt_efficacy = 0
        self.temp_adapt = 0
        self.adaptation_cost = 0
        self.diverse_information = float(diverse_information)
        self.dro_occ = float(dro_occ)
        self.dro_event = float(dro_event)
        self.fld_occ = float(fld_occ)
        self.fld_event = float(fld_event)
        self.yield_loss = 0
        self.households = []

    def __str__(self):
        HH_object = 'Household' + str(self.HHID) + \
                    ' located at < ' + str(self.X_COORD) + ',' \
                    + str(self.Y_COORD) + '> ' + 'has landsize ' \
                    + str(self.cultivated) + ' and a yearly income of ' \
                    + str(self.yearly_income)
        return HH_object

    def climate_risk(self):
            intensity = random.randint(1, 5)
            self.yield_loss = 0.1 * intensity * self.exp_yield
            return self.yield_loss

    def adaptation_PMT(self):  # Calculating percieved exposure
        if self.act_yield > self.exp_yield:  # if actual yield is greater than expected yield, farmer does not take any adaptation measures
            self.perceived_exposure = 0
        else:
            self.perceived_exposure = self.yield_loss

        if self.drought_type == 1:  # Calculating percieved severity of exposure
            self.perceived_severity = 0.02 * self.dro_event
        elif self.fld_type == 1:
            self.perceived_severity = 0.02 * self.fld_event

        # Calculating adaptation efficacy
        neigh_distance = 2000  # neighborhood distance buffer
        minX_buffer = self.X_COORD - neigh_distance
        minY_buffer = self.Y_COORD - neigh_distance
        maxX_buffer = self.X_COORD + neigh_distance
        maxY_buffer = self.Y_COORD + neigh_distance
        neigh_adaptation = []
        for neigh in self.households:
            if neigh != self and \
                                    minX_buffer <= neigh.X_COORD <= maxX_buffer and minY_buffer <= neigh.Y_COORD <= maxY_buffer:
                if neigh.adaptation_score > 0.5:
                    self.adaptation_efficacy = (
                        0.1 * neigh.adaptation_score)  # if neighbor has high adaptation score, their perception of  adaptation efficacy increases by 10 percent)

                neigh_adaptation.append(self.adaptation_efficacy)

        for efficacy in enumerate(neigh_adaptation):
            self.adapt_efficacy += efficacy

            if self.adapt_efficacy >= 0.2:  # adaptation efficacy can only be between range (0 to 0.2)
                self.adapt_efficacy = 0.2
            else:
                self.adapt_efficacy = self.adapt_efficacy
                # Calculating self efficacy
                # This uses memory from the last time step for adaptation strategy
        self.self_efficacy = 0.2 * self.temp_adapt
        # where 0.2 is correlation coefficient between adaptation score and self efficacy

        # Caculating adaptation cost score  adaptation_cost:
        cost_analyse = self.price_loss - self.adaptation_cost
        if cost_analyse > 0:
            self.adapt_cost_score = 0.2
        else:
            self.adapt_cost_score = 0

        # Calculating overall adaptation score
        self.adaptation_score = self.perceived_exposure + self.perceived_severity + self.adapt_efficacy + self.self_efficacy + self.adapt_cost_score
        self.temp_adapt = self.adaptation_score

        return self.adaptation_score


class ShapeMap:
    def __init__(self, BB_Xmin, BB_Ymin, BB_Xmax, BB_Ymax):
        self.BB_Xmin = BB_Xmin
        self.BB_Ymin = BB_Ymin
        self.BB_Xmax = BB_Xmax
        self.BB_Ymax = BB_Ymax

    def __str__(self):
        messageMap = "The lower bound of this space is {} in x {} in y, and the upper bound of this space is {} in x and {} in y".format(
            self.BB_Xmin, self.BB_Ymin, self.BB_Xmax, self.BB_Ymax)
        return messageMap


# ---------------------------------
if __name__ == "__main__":
    import pshapes

    # loading the data
    hh = "../data/bihar7"
    shapebase = pshapes.readShpPointData(hh)
    database = pshapes.readDbfData(hh)
    households = []
    for points, hhdata in zip(shapebase, database):
        HH_ID, cultivated, CC_awareness, Access_weathe_forecast, CC_CROP_IMPACT, Rice_major_risk, Wheat_major_risk, maiz_major_risk, drought_type, dro_strategy_used, dro_A1_adaptcost, fld_type, fld_strategy_used, fld_A1_adaptcost, event_type, crop_affected, exp_yield, act_yield, price_loss, yearly_income, monthly_income, Social_Capital, SC_strength, diverse_information, dro_occ, dro_event, fld_occ, fld_event, perceived_exposure = hhdata
        x, y = points
        house = household(HH_ID, x, y, cultivated, CC_awareness, Access_weathe_forecast, CC_CROP_IMPACT,
                          Rice_major_risk, Wheat_major_risk, maiz_major_risk, drought_type, dro_strategy_used,
                          dro_A1_adaptcost, fld_type, fld_strategy_used, fld_A1_adaptcost, event_type, crop_affected,
                          exp_yield, act_yield, price_loss, yearly_income, monthly_income, Social_Capital, SC_strength,
                          diverse_information, dro_occ, dro_event, fld_occ, fld_event, perceived_exposure)
        households.append(house)

    # display chouseholds
    for house in households:
        print house
    # shape map

    shpheader = pshapes.readShpHeader(hh)
    shapemap = ShapeMap(shpheader["BBOX Xmin"], shpheader["BBOX Ymin"], shpheader["BBOX Xmax"], shpheader["BBOX Ymax"])
    print shapemap
