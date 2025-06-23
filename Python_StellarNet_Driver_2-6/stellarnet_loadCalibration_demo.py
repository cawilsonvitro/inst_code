#################################################################################
# This demo program demonstrates how to capture raw dark reference and 
# raw sample/light reference spectra, then use that spectral data to compute 
# scope and watts values using the StellarNet-provided .CAL calibration file.
#
# Be sure to use the .CAL file provided specifically for your spectrometer, 
# as calibration files are unique to each device.
#
# This is a demo only. You will need to modify or extend the code to suit 
# your specific needs or application requirements.
#
# Date: 6/5/2025
#################################################################################


from stellarnet_driverLibs import stellarnet_driver3 as sn
import time, numpy as np

def getScopeAndWattsData(spectrometerWavelength, rawSampleDataY, rawDarkDataY, rawSampleDataCapturedIntegrationTimeInMS, calibrationFilePath, aperturePercentage=100):
    """
    Calculate the Watts/m^2 spectral data using the provided raw sample data, dark data, and calibration file.

    Args:
        spectrometerWavelength (array or list): Wavelength values for the spectrometer.
        rawSampleDataY (array or list): Raw sample spectral data directly obtained from the spectrometer, without dark subtraction.
        rawDarkDataY (array or list): Raw dark spectral data (to subtract from the sample data). The spectrometer should be covered to ensure no light enters.
        rawSampleDataCapturedIntegrationTimeInMS (float): The integration time in milliseconds at which the sample data was captured.
        calibrationFilePath (str): The path to the StellarNet .CAL calibration file. It should be a valid StellarNet calibration file.
        aperturePercentage (float, optional): Percentage of the aperture value (the amount of light entering the spectrometer). Default is 100%.

    Returns:
        spectrometerWavelength (numpy.ndarray): Provided wavelengths nm.
        scopeY (numpy.ndarray): A numpy array representing the scope intensity spectrum corresponding to the provided wavelengths.
        wattsY (numpy.ndarray): A numpy array representing the Watts/m^2 spectrum corresponding to the provided wavelengths.

    Notes:
        - `spectrometerWavelength`, `rawSampleDataY`, and `rawDarkDataY` must have the same length. The `spectrometerWavelength` array should correspond to the provided `rawSampleDataY` and `rawDarkDataY`.
    """
    
    # Step 1: Load the calibration data and interpolate it to match the spectrometerWavelength
    calibrationData = np.genfromtxt(calibrationFilePath, skip_header=31, skip_footer=1)  # Read the calibration data from the file
    interpolatedCalibrationDataY = np.interp(spectrometerWavelength, calibrationData[:, 0], calibrationData[:, 1], left=0, right=0)  # Interpolate calibration data

    # Step 2: Extract the calibration integration time from the .CAL file
    calibrationIntegrationTime = int(
        next(line.strip().split('=')[1]
            for line in open(calibrationFilePath, 'r') if 'Csf1' in line))  # Extract integration time from the calibration file

    # Step 3: Subtract dark data from the sample data to obtain the corrected scope data
    scopeY = np.subtract(rawSampleDataY, rawDarkDataY)  # Subtract dark data from sample data to correct for dark noise
    scopeY[scopeY < 0] = 0  # Ensure no negative values after subtraction

    # Step 4: Normalize the raw scope data based on the integration times (calibration and sample)
    normRatio = float(calibrationIntegrationTime) / float(rawSampleDataCapturedIntegrationTimeInMS)  # Calculate the normalization ratio

    # Step 5: Convert the spectral data to Watts, applying the aperture scaling
    wattsY = np.asarray(scopeY * interpolatedCalibrationDataY[:len(spectrometerWavelength)] * normRatio * (100.0 / aperturePercentage))  # Convert to Watts

    wattsY[wattsY < 0] = 0  # Ensure no negative values in the Watts data
    
    return {'wavelength':spectrometerWavelength, 'scopeY':scopeY, 'wattsY':wattsY}  # Return the calculated Watts values


# Device parameters to set. Replace it with your desired settings
inttime = 100  
scansavg = 1 
smooth = 1    
xtiming = 3   

#init Spectrometer - Get BOTH spectrometer and wavelength
spectrometer, wav = sn.array_get_spec(0) # 0 for first channel and 1 for second channel , up to 127 spectrometers

# Get device ID
deviceID = sn.getDeviceId(spectrometer)
print('\nMy device ID: ', deviceID)

# Call to Enable or Disable External Trigger to by default is Disbale=False -> with timeout
# Enable or Disable Ext Trigger by Passing True or False, If pass True than Timeout function will be disable, so user can also use this function as timeout enable/disbale 
sn.ext_trig(spectrometer,True)

# Only call this function on first call to get spectrum or when you want to change device setting.
# -- Set last parameter to 'True' throw away the first spectrum data because the data may not be true for its inttime after the update.
# -- Set to 'False' if you don't want to throw away the first data, however your next spectrum data might not be valid.
sn.setParam(spectrometer, inttime, scansavg, smooth, xtiming, True) 

# Get current device parameter
currentParam = sn.getDeviceParam(spectrometer)
print(currentParam)

# Get device coefficients
myCoefficients = sn.getCoeffs(spectrometer)
print(myCoefficients)

# User parameters for configuration. Adjust the parameters as needed.
userParams = {
    'calFile': 'demo.CAL', # Replace this your StellarNet Provided .CAL Calibration file
    'co1': myCoefficients[0], # 1st coefficient
    'co2': myCoefficients[1], # 2nd coefficient
    'co3': myCoefficients[2], # 3rd coefficient
    'co4': myCoefficients[3], # 4th coefficient
    'dsf': currentParam['int_time'], # Current integration time in seconds
    'tc': currentParam['temp_comp'], # Temperature compensation flag
    'aper': 100, # Aperture percentage
    'pixels': len(wav) # Pixel length
}

# Taking the dark spectrum. Make sure the spectrometer is covered and no light goes into the spectrometer
print('\n\n*** Cover the spectrometer to take the dark. Dark capture will start in 3 seconds...')
time.sleep(3) # Increase the sleep timer if you need more time to cover the spectrometer.
raw_dark_dataY = sn.getSpectrum_Y(spectrometer)   # Capture dark spectrometer
print('Dark Captured')

# Start capturing the light data now...
print('\n\n*** Remove the cover from the spectrometer and place the light source or samples. Data capture will start in 3 seconds...')
time.sleep(3)  # Increase the sleep timer if you need more time to place the sample or light source

# Perform data capture 30 times, adjust this value as needed.
for run in range(30):

    print('Capture counter: ', run+1)

# Get raw light data from spectrometer
    raw_sample_dataY = sn.getSpectrum_Y(spectrometer)  

# Call the function to calculate the scope and watts spectra
    spectralData = getScopeAndWattsData(wav[:, 0], raw_sample_dataY, raw_dark_dataY, userParams['dsf'], userParams['calFile'], userParams['aper'])
    
    wavelength = spectralData['wavelength']
    scopeY = spectralData['scopeY']  #spectrum with dark subtracted
    wattsY = spectralData['wattsY']  #Watts spectrum with calibration applied: Watts/m^2

# Uncomment the section below to graph the spectrum using the matplotlib library.
# Make sure matplotlib is installed by running: pip install matplotlib
    # import matplotlib.pyplot as plt
    # plt.plot(wavelength, scopeY)  #Change scopeY to wattsY if you like to plot the watts graph
    # plt.xlabel('Wavelength')
    # plt.ylabel('')
    # plt.show()

# wait 1 second before start of next scan, adjust this timer as needed
    time.sleep(1) 