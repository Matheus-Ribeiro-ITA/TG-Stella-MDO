from trendLines import *

# Load Dataframe or Excel
uavDataFrame = UavDataFrame()

# Get Atoba's Data
atoba = AtobaUAV()

# Get data from Dataframe
listUav = [Uav(*row[0:17]) for index, row in uavDataFrame.df.iterrows()]

# Plot
wingSpanMin = 50
wingSpanMax = 800
plotUavs(listUav, "mtow", "wingSpan", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "payload", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "range", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "endurance", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "aspectRatio", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
