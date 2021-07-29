
import core
import context
context.get()

import magSonify
import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.axes
import numpy as np
from magSonify.sonificationMethods.audiotsmWithDebugOutput import phasevocoder
from magSonify.sonificationMethods.audiotsmWithDebugOutput.io.array import ArrayReader, ArrayWriter

### Parameters ###
stretch = 2

scan = -64 # Allows shifting the start of the interval
interval = 512//2*3 # Number of samples in the interval

xlow = 6272+scan
xhigh = 6272+scan+interval

useBreakingLines = True
useSubplotVariedLengths = True

event = (
        datetime.datetime(2008,12,7),
        datetime.datetime(2008,12,8)
    )

showFullDay_waveforms = False
showFullDay_spetrogram = False
### End Params ###

pol, polBefore = core.setup(event)

frameLength = 512
synthesisHop = frameLength//16
reader = ArrayReader(np.array((pol.x,)))
writer = ArrayWriter(reader.channels)
timeSeriesModification = phasevocoder(
    reader.channels,
    speed = 1/stretch,
    frame_length=frameLength,
    synthesis_hop=synthesisHop,
)
timeSeriesModification.run(reader, writer)
pol.x = writer.data.flatten()
pol._stretchTimeseries(stretch)
pol._correctTimeseries()

coefficients = np.abs(np.array(timeSeriesModification.STFT_DEBUG))
startPos = np.arange(
    0, len(polBefore.x), timeSeriesModification._analysis_hop
)
windowSeries = timeSeriesModification._analysis_window


ax1, ax2, ax3, ax1r, ax3r = core.setup3axesWithTwinsForWindows(useSubplotVariedLengths)

xlim1 = slice(xlow,xhigh)
xlim2 = slice(xlow*stretch,xhigh*stretch)

timesBefore = polBefore.timeSeries.asFloat()
times = pol.timeSeries.asFloat()

N = coefficients.shape[0]/len(polBefore.x)
xlimcoeffs = slice(int(xlow*N)-1,int(xhigh*N)+5)

# Disable the use of range restriction
if showFullDay_waveforms: 
    xlim1 = xlim2 = slice(None,None)
if showFullDay_spetrogram:
    xlimcoeffs = slice(None,None)


cmap = 'plasma'

preStretchX = timesBefore[xlim1] - timesBefore[xlow]

timesRelativeToIntervalStart = timesBefore - timesBefore[xlow]

# Plot the analysis windows
lastWindowLine_ax1 = core.plotWindows(
    startPos, windowSeries, ax1r, xlimcoeffs, timesRelativeToIntervalStart, numberOfWindows=10
)

magFieldPlotLine, = ax1.plot(preStretchX,polBefore.x[xlim1])

# Get the central time of each window in order to plot the coefficients
coefficientsTimes = timesRelativeToIntervalStart[startPos]
coefficientsTimes = coefficientsTimes + (timesRelativeToIntervalStart[1]-timesRelativeToIntervalStart[0])/2

coefficients = coefficients[xlimcoeffs,:]
coefficients = np.log(coefficients)

coefficientsTimes = coefficientsTimes[xlimcoeffs]

# Get frequencies
freqs = np.fft.rfftfreq(len(windowSeries),3)

# Plot coefficients
ax2.pcolormesh(
    coefficientsTimes,
    freqs,
    coefficients.T,
    shading='auto',
    cmap=cmap,
)

if useBreakingLines:
    lw = 1
    ax2.grid(True, which='minor', axis='x', linestyle='-', color='k',linewidth=lw)
    ax2.set_xticks(
        coefficientsTimes + (coefficientsTimes[1]-coefficientsTimes[0])/2,
        minor=True
    )

# Plot after time stretch
postStretchX = pol.timeSeries.asFloat()[xlim2] - pol.timeSeries.asFloat()[xlow*stretch]

lastWindowLine_ax3 = core.plotWindows(
    startPos, windowSeries, ax3r, xlimcoeffs, timesRelativeToIntervalStart, numberOfWindows=10
)

afterPlotLine, = ax3.plot(postStretchX,pol.x[xlim2])

ax2.set_yscale('log')
ax2.set_ylim([
    freqs[1],freqs[-50]
])

ax3.set_xlabel("Time since start of interval [s]")
ax1.set_ylabel("Field [nT]")
ax2.set_ylabel("Frequency [Hz]")
ax3.set_ylabel("Amplitude")
ax1r.set_ylabel("Window amplitude")
ax3r.set_ylabel("Window amplitude")

core.colorTwinAxes(ax1, ax1r, magFieldPlotLine, lastWindowLine_ax1)
core.colorTwinAxes(ax3, ax3r, afterPlotLine, lastWindowLine_ax3)

ax2.tick_params(axis='x', colors='w')

for ax in (ax1, ax2):
    plt.setp(ax.get_xticklabels(), visible=False)

core.set_xlim(showFullDay_waveforms, showFullDay_spetrogram, (ax1, ax2, ax3), preStretchX, timesRelativeToIntervalStart)

print("Window length:", len(windowSeries))
plt.tight_layout()

magSonify.Utilities.ensureFolder("Algorithm Diagrams")
plt.savefig("Algorithm Diagrams/Phase Vocoder Diagram.svg")


plt.show()