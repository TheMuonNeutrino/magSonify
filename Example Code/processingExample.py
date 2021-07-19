import context
context.get()

from datetime import datetime
from magSonify.MagnetometerData import THEMISdata
import numpy as np

mag = THEMISdata()

event2007_09_04 = (datetime(2007,9,4), datetime(2007,9,5))
event2008_12_07 = (datetime(2008,12,7), datetime(2008,12,10))
event2011_09_02 = (datetime(2011, 9, 2), datetime(2011, 9, 6))

mag.importCdasAsync(
    *event2008_12_07
)
mag.magneticField.removeDuplicateTimes()
mag.peemIdentifyMagnetosheath.removeDuplicateTimes()
mag.interpolate_3s()
mag.magneticField.constrainAbsoluteValue(400)
mag.meanField = mag.magneticField.runningAverage(timeWindow=np.timedelta64(35,"m"))
mag.magneticField = mag.magneticField - mag.meanField
mag.fillLessThanRadius(4)
mag.removeMagnetosheath()
mag.convertToMeanFieldCoordinates()

mag.magneticFieldMeanFieldCoordinates.fillNaN()

com = mag.magneticFieldMeanFieldCoordinates.extractKey(0)
com.phaseVocoderStretch(16)
com.normalise()
com.genMonoAudio("Example of com x16 with phase vocoder.wav")

pol = mag.magneticFieldMeanFieldCoordinates.extractKey(1)
pol.phaseVocoderStretch(16)
pol.normalise()
pol.genMonoAudio("Example of pol x16 with phase vocoder.wav")

tor = mag.magneticFieldMeanFieldCoordinates.extractKey(2)
tor.phaseVocoderStretch(16)
tor.normalise()
tor.genMonoAudio("Example of tor x16 with phase vocoder.wav")

# Disable the wavelet stretch output if it's taking too long
# exit()

com = mag.magneticFieldMeanFieldCoordinates.extractKey(0)
com.waveletStretch(16,0.5,16)
com.normalise()
com.genMonoAudio("Example of com x16 with wavelets.wav",sampleRate=44100//2)

pol = mag.magneticFieldMeanFieldCoordinates.extractKey(1)
pol.waveletStretch(16,0.5,16)
pol.normalise()
pol.genMonoAudio("Example of pol x16 with wavelets.wav",sampleRate=44100//2)

tor = mag.magneticFieldMeanFieldCoordinates.extractKey(2)
tor.waveletStretch(16,0.5,16)
tor.normalise()
tor.genMonoAudio("Example of tor x16 with wavelets.wav",sampleRate=44100//2)