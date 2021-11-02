from literature_data.utils.utils import UavDataFrame, plotUavs, Uav, AtobaUAV

# Load Dataframe or Excel
uavDataFrame = UavDataFrame()

# Get Atoba's Data
atoba = AtobaUAV()
atoba = None
# Get data from Dataframe
listUav = [Uav(*row[0:17]) for index, row in uavDataFrame.df.iterrows()]

# Plot
wingSpanMin = 50
wingSpanMax = 200
plotUavs(listUav, "mtow", "wingSpan", stellaUav=atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "payload", stellaUav=atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "range", stellaUav=atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "endurance", stellaUav=atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
plotUavs(listUav, "mtow", "aspectRatio", stellaUav=atoba, lowerLimit=wingSpanMin, upperLimit=wingSpanMax, save=True)
