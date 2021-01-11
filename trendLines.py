from trendLines import *

# Load Dataframe or Excel
uavDataFrame = UavDataFrame()

# Get Atoba's Data
atoba = AtobaUAV()

# Get data from Dataframe
listUav = [Uav(*row[0:17]) for index, row in uavDataFrame.df.iterrows()]

# Plot
plotUavs(listUav, "wingSpan", "mtow", atoba, save=True)
plotUavs(listUav, "wingSpan", "payload", atoba, save=True)
plotUavs(listUav, "wingSpan", "range", atoba, save=True)
plotUavs(listUav, "wingSpan", "endurance", atoba, save=True)
plotUavs(listUav, "wingSpan", "aspectRatio", atoba, save=True)