"""
Adpatation Model - main GUI
----------------------
Hogeun Park & Udita Sanga

Display rural households as points as the underlying image
Apr 24, 2016
"""
# IMPORTs --------------------------------------------------------------------------
import wx, os
import numpy as np

import matplotlib as mpl

mpl.use('WXAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg, NavigationToolbar2Wx, FigureManager
from matplotlib.ticker import NullLocator

from src import load
from src import households
import numpy as np 

# CLASS DEFINITIONs ------------------------------------------------------------------

class Map(wx.Frame):
    """Basic frame for ABM display """

    # subclasses the generic wx.Frame

    def __init__(self, pts, raster, update_time=0):
        """ path to the points shapefile, path to ASCII grid """
        # __init__() sets up the frame, but does not display anything
        wx.Frame.__init__(self, None, title="Agent-Based Model Viewer",
                          pos=(100, 0), size=(1000, 1000))  # the frame has a fixed location and size
        # load the data
        shapemap, houses, grid = load.setup(pts, raster)
        # set extent of your map to the largest bounding box
        self.xmin = min(shapemap.BB_Xmin, grid.BB_Xmin)
        self.xmax = max(shapemap.BB_Xmax, grid.BB_Xmax)
        self.ymin = min(shapemap.BB_Ymin, grid.BB_Ymin)
        self.ymax = max(shapemap.BB_Ymax, grid.BB_Ymax)

        x_size = self.xmax - self.xmin
        y_size = self.ymax - self.ymin
        # create the main figure & toolbar
        self.figure = plt.figure(figsize=(x_size, y_size))
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        # Put all into a sizer that will handle the ogranization of the frame in a neat way
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        # ------------------------------------------------------
        # CUSTOM GIS-related attributes (model components)
        self.points = houses
        self.grid = grid  # background raster (static object!)
        self.ticks = 0  # tick count
        self.moved = 0
        self.runs = 0
        self.intensitytimer=0

        # -------------------------------------------------------
        # To execute the model and trigger the display we will use the Timer object from wxPython:
        self.timer = wx.Timer(self)
        self.timer.Start(update_time)  # update step (milliseconds)
        # event binders:
        self.Bind(wx.EVT_TIMER, self.onTimer)  # model iterator
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def reset(self):
        self.ticks = 0
        self.moved = 0
        self.intensitytimer=0
        for house in self.points:
			house.yield_loss= 0
			house.adaptation_score=0
        self.redraw()
        hh_shp = "data/bihar7"
        asciigrid = "data/field2.asc"
        shapemap, houses, grid = load.setup(hh_shp, asciigrid)
        self.points = houses
    def draw(self):
        colormap = "summer_r"
        alpha = 0.6
        plt = self.figure.add_subplot(111)
        self.map_raster = plt.imshow(self.grid.body,
                                     extent=[self.xmin, self.xmax, self.ymin, self.ymax],
                                     cmap=colormap, alpha=alpha,
                                     interpolation='nearest')
        plt.xaxis.set_major_locator(NullLocator())
        plt.yaxis.set_major_locator(NullLocator())

        nonadapt_xcoord = []
        nonadapt_ycoord = []
        lowadapt_xcoord = []
        lowadapt_ycoord = []
        medadapt_xcoord = []
        medadapt_ycoord = []
        highadapt_xcoord = []
        highadapt_ycoord = []
        for point in self.points:
            if point.adaptation_score <= 0:  # no adaptation
                nonadapt_xcoord.append(point.X_COORD)
                nonadapt_ycoord.append(point.Y_COORD)
            elif point.adaptation_score < 0.1: #and point.adaptation_score <= 0.3:  # low adaptation
                lowadapt_xcoord.append(point.X_COORD)
                lowadapt_ycoord.append(point.Y_COORD)
            elif point.adaptation_score < 0.3:  # Medium adaptation
                medadapt_xcoord.append(point.X_COORD)
                medadapt_ycoord.append(point.Y_COORD)
            else:
                highadapt_xcoord.append(point.X_COORD)
                highadapt_ycoord.append(point.Y_COORD)
        self.drawn_points = plt.plot(nonadapt_xcoord, nonadapt_ycoord, marker='o', color='r', markersize=6,markeredgewidth=0.5, linewidth=0)
        self.drawn_points = plt.plot(lowadapt_xcoord, lowadapt_ycoord, marker='o', color='b', markersize=6,markeredgewidth=0.5, linewidth=0)
        self.drawn_points = plt.plot(medadapt_xcoord, medadapt_ycoord, marker='o', color='g', markersize=6,markeredgewidth=0.5, linewidth=0)
        self.drawn_points = plt.plot(highadapt_xcoord, highadapt_ycoord, marker='o', color='y', markersize=6,markeredgewidth=0.5, linewidth=0)

    def redraw(self):
        """ redraw points after a tick"""
        # retrieve the new coords for points
        nonadapt_xcoord = []
        nonadapt_ycoord = []
        lowadapt_xcoord = []
        lowadapt_ycoord = []
        medadapt_xcoord = []
        medadapt_ycoord = []
        highadapt_xcoord = []
        highadapt_ycoord = []
        # x_coords = []; y_coords = []

        for point in self.points:
            if point.adaptation_score <= 0:  # no adaptation
                nonadapt_xcoord.append(point.X_COORD)
                nonadapt_ycoord.append(point.Y_COORD)
            elif point.adaptation_score < 0.1:# and point.adaptation_score <= 0.3:  # low adaptation
                lowadapt_xcoord.append(point.X_COORD)
                lowadapt_ycoord.append(point.Y_COORD)
            elif point.adaptation_score < 0.3:# and point.adaptation_score <= 0.7:  # Medium adaptation
               medadapt_xcoord.append(point.X_COORD)
               medadapt_ycoord.append(point.Y_COORD)
            else:
				highadapt_xcoord.append(point.X_COORD)
				highadapt_ycoord.append(point.Y_COORD)
        # redraw
        self.drawn_points[0].set_data(nonadapt_xcoord, nonadapt_ycoord)
        self.drawn_points[0].set_data(lowadapt_xcoord, lowadapt_ycoord)
        self.drawn_points[0].set_data(medadapt_xcoord, medadapt_ycoord)
        self.drawn_points[0].set_data(highadapt_xcoord, highadapt_ycoord)
        self.canvas.draw()
#initalize resident agents"""
    def onTimer(self, evt):
        self.ticks += 1
        self.intensitytimer += 3
        average_adapt = []
        yield_l = []
        for house in self.points:
            house.climate_risk()
            loss = house.yield_loss*self.intensitytimer
            house.adaptation_PMT()
            average_adapt.append(house.adaptation_score)
            yield_l.append(loss)
#print "t =", self.ticks,"average_adaptation_score =",
        print sum(average_adapt)/615
        time.append(self.ticks)
        average_score.append(float(sum(average_adapt)/615))

        if self.ticks == 50:
            self.runs += 1
            #print "Run N =", self.runs, "finished"
            if self.runs == 200:
                print "Simulation finished."
                self.timer.Stop()
            else:
                self.reset()

        self.redraw()

    def onClose(self, evt):
        self.timer.Stop()
        evt.Skip()


# APPLICATION ----------------------------------------------------------------
if __name__ == '__main__':
    # INPUT
    hh_shp = "data/bihar7"
    asciigrid = "data/field2.asc"
    time = []
    average_score = []

    # Cows
    # INITIALIZE display
    app = wx.PySimpleApp()
    frame = Map(hh_shp, asciigrid)
    frame.draw()
    frame.Show()
    

    # EXECUTE
    app.MainLoop()
