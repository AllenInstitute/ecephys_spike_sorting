
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
            End time in seconds
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
