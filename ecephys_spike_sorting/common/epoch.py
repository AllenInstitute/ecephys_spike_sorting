import h5py as h5
import numpy as np


class Epoch():

    """
    Represents a data epoch with a start time (in seconds), an end time (in seconds), and a name

    Optionally includes a start_index and an end_index

    """

    def __init__(self, name, start_time, end_time):

        """
        name : str
            Name of epoch
        start_time : float
            Start time in seconds
        end_time : float
            End time in seconds (can be Inf to use the full file)
        """

        self.start_time = start_time
        self.end_time = end_time
        self.name = name
        self.start_index = None
        self.end_index = None

    def convert_to_index(timestamps):

        """ Converts start/end times to start/end indices

        Input:
        ------
        timestamps : numpy.ndarray (float)
            Array of timestamps for each sample

        """

        self.start_index = np.argmin(np.abs(timestamps - self.start_time))

        if self.end_time != np.Inf:
            self.end_index = np.argmin(np.abs(timestamps - self.end_time))
        else:
            self.end_index = timestamps.size



def get_epochs_from_nwb_file(filename):

    nwb = h5.File(filename)

    epochs = []

    stimuli = nwb['stimulus']['presentation'].keys()

    for stim_idx, stimulus in enumerate(stimuli):

        if stimulus != 'optotagging' and stimulus != 'spontaneous':
            
            trial_times = np.squeeze(nwb['stimulus']['presentation'][stimulus]['timestamps'][:,0])
            trial_data = nwb['stimulus']['presentation'][stimulus]['data']
            stimulus_features = [i.decode('utf-8') for i in nwb['stimulus']['presentation'][stimulus]['features']]
            
            if stimulus.find('natural_movie') > -1:
                movie_start_inds = np.where(trial_data == 0)[0]
                trial_times = trial_times[movie_start_inds]

            if stimulus.find('flash_250') > -1:
                epoch1_end = np.max(trial_times)
            elif stimulus.find('drifting_gratings_more_repeats') > -1:
                gap = np.where(np.diff(trial_times) > 5)[0][0]
                epoch3_start = np.mean(trial_times[gap:gap+2])
            elif stimulus.find('static_gratings') > -1:
                epoch3_start = np.min(trial_times)

    epochs = [Epoch('RF_mapping_and_flashes', 0, epoch1_end),
              Epoch('epoch2', epoch1_end, epoch3_start),
              Epoch('epoch3', epoch3_start, np.Inf),
              Epoch('complete_session', 0, np.Inf)]

    return epochs