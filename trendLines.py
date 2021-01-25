from trendLines import *

# Load Dataframe or Excel
uavDataFrame = UavDataFrame()

# Get Atoba's Data
atoba = AtobaUAV()

# Get data from Dataframe
listUav = [Uav(*row[0:17]) for index, row in uavDataFrame.df.iterrows()]

# Plot
wingSpanMin = 0
wingSpanMax = 20
plotUavs(listUav, "wingSpan", "mtow", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "wingSpan", "payload", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "wingSpan", "range", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "wingSpan", "endurance", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "wingSpan", "aspectRatio", atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
