from stellarnet_driverLibs import stellarnet_driver3 as sn
from threading import Thread
import time

def runSingleSpectrometerInLoop(channel, device_id, spectrometer, wav):
    count = 0
    while LOOP_RUNNING:
        count +=1
        st = time.time()
        spectrum = sn.array_spectrum(spectrometer, wav)
        print('Count: '+str(count)+' -> Spectrum from Channel '+str(channel)+' (ID: '+device_id+') : ', spectrum, '\n=====================\n\n')
        print(time.time() - st)
        
version = sn.version()
print(version)	

# predefind spectrometer parameters based on the parameters
spectrometer_params = {
    '22072013':{'inttime': 50, 'scansavg':1, 'smooth':1, 'xtiming':3 }, 
    '19041129':{'inttime': 10, 'scansavg':1, 'smooth':1, 'xtiming':3 }, 
    'Default' :{'inttime': 10, 'scansavg':2, 'smooth':2, 'xtiming':3 }
}

# Soectrometer objects
spectrometers = {} 
spectrometer_wavs = {} 
spectrometer_threads = {}
LOOP_RUNNING = True

# get all connected spectrometer
totalCount = sn.total_device_count()

# Create the spectrometer objects for each spectrometer
for channel in range(totalCount):
    # Get the spectrometer for current channel
    spectrometer, wav = sn.array_get_spec(channel)


for channel in range(totalCount):
    # Turn off the timeout
    spectrometer['device'].extrig(True)
    
    # Get the device id for current channel
    device_id = sn.getDeviceId(spectrometer)

    # Store the spectrometer and the wavelength toa dictionary
    spectrometers[device_id] = spectrometer
    spectrometer_wavs[device_id] = wav

    # configure the device parameters. If device parameter is not pre-defined, use the default parameters.
    if device_id in spectrometer_params.keys():
        sn.setParam(spectrometer, 
                    spectrometer_params[device_id]['inttime'], 
                    spectrometer_params[device_id]['scansavg'] , 
                    spectrometer_params[device_id]['smooth'], 
                    spectrometer_params[device_id]['xtiming'], clear = False) 
    else:
        sn.setParam(spectrometer, 
            spectrometer_params['Default']['inttime'], 
            spectrometer_params['Default']['scansavg'] , 
            spectrometer_params['Default']['smooth'], 
            spectrometer_params['Default']['xtiming'], clear = False) 
    
    # double check the device parameters
    deviceSetting = sn.getDeviceParam(spectrometer)
    print(device_id+': ', deviceSetting)

    # Create a thread for each spectrometer and store it to a dictionary
    spectrometer_thread = Thread(target =runSingleSpectrometerInLoop ,  args=(channel, device_id, spectrometer, wav, ), daemon=True)
    spectrometer_threads[device_id] = spectrometer_thread

# start running the threads
for deviceID, thread in spectrometer_threads.items():
    thread.start()


# Stop the spectrometer capture after 5 second
time.sleep(5)
LOOP_RUNNING = False

# Terminate all the threads
for deviceID, thread in spectrometer_threads.items():
    thread.join()