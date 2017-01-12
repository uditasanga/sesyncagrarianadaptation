import pshapes
import households
import ASCII

def setup(pts="../data/bihar7", raster="../data/field2.asc"):
    shapebase = pshapes.readShpPointData(pts)
    database = pshapes.readDbfData(pts)
    houses = []

    for point, pointdata in zip(shapebase, database):
        HH_ID, cultivated, CC_awareness, Access_weathe_forecast, CC_CROP_IMPACT, Rice_major_risk, Wheat_major_risk, maiz_major_risk, drought_type, dro_strategy_used, dro_A1_adaptcost, fld_type, fld_strategy_used, fld_A1_adaptcost, event_type, crop_affected, exp_yield, act_yield, price_loss, yearly_income, monthly_income, Social_Capital, SC_strength, diverse_information, dro_occ, dro_event, fld_occ, fld_event, perceived_exposure = pointdata
        x, y = point
        home = households.household(HH_ID, x, y, cultivated, CC_awareness, Access_weathe_forecast, CC_CROP_IMPACT,
                                    Rice_major_risk, Wheat_major_risk, maiz_major_risk, drought_type, dro_strategy_used,
                                    dro_A1_adaptcost, fld_type, fld_strategy_used, fld_A1_adaptcost, event_type,
                                    crop_affected, exp_yield, act_yield, price_loss, yearly_income, monthly_income,
                                    Social_Capital, SC_strength, diverse_information, dro_occ, dro_event, fld_occ,
                                    fld_event, perceived_exposure)
        houses.append(home)

    # create the background raster object
    back = ASCII.Raster(raster)

    shpheader = pshapes.readShpHeader(pts)
    shapemap = households.ShapeMap(shpheader["BBOX Xmin"], shpheader["BBOX Ymin"], shpheader["BBOX Xmax"],
                                   shpheader["BBOX Ymax"])
    return (shapemap, houses, back)


# APPLICATION ----------------------------------------------------------------
if __name__ == '__main__':
    db = setup()
    for data in db:
        print data
