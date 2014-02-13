import h5py

NUM_MICS = 1 # Number of microphones to be used. Can be 0, 1, or 2
BUFFER_SIZE = 1000
SAMPLE_RATE = 100000.0
TIMESTEP = 1 / SAMPLE_RATE
WINDOW_NAME = 'Feed' # window name for the live stream output
TOLERANCE = 30 # Determines the tolerance to be used in thresholding the roi image in defs.py. Larger tolerance values lead to more white pixels
RECORDING_TIME = 300
NUMBER_OF_AUDIO_SAMPLES = SAMPLE_RATE * RECORDING_TIME
WRITE_SIZE = BUFFER_SIZE*1000

AUDIO_OUTPUT_PATH = "C:\Users\ken\Desktop\noStimNewWriter\audio_output.hdf5"
