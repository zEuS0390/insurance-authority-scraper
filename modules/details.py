# Definition of a class named 'Details'
class Details:
    
    # Constructor method to initialize instances of the class
    def __init__(self):
        # Initializing private attributes for different sections with 'None'
        self._POLII = None
        self._AWCAP = None
        self._PL = None
        self._PDAL5 = None
        self._N = None
        self._R = None

    # Property getter and setter methods for 'POLII' attribute
    @property
    def POLII(self):
        return self._POLII

    @POLII.setter
    def POLII(self, value):
        self._POLII = value

    # Property getter and setter methods for 'AWCAP' attribute
    @property
    def AWCAP(self):
        return self._AWCAP

    @AWCAP.setter
    def AWCAP(self, value):
        self._AWCAP = value

    # Property getter and setter methods for 'PL' attribute
    @property
    def PL(self):
        return self._PL

    @PL.setter
    def PL(self, value):
        self._PL = value

    # Property getter and setter methods for 'PDAL5' attribute
    @property
    def PDAL5(self):
        return self._PDAL5

    @PDAL5.setter
    def PDAL5(self, value):
        self._PDAL5 = value

    # Property getter and setter methods for 'N' attribute
    @property
    def N(self):
        return self._N

    @N.setter
    def N(self, value):
        self._N = value

    # Property getter and setter methods for 'R' attribute
    @property
    def R(self):
        return self._R

    @R.setter
    def R(self, value):
        self._R = value
