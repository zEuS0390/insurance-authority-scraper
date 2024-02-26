class FirmDetails:
    
    def __init__(self):
        self._POLII = None
        self._AWCAP = None
        self._PL = None
        self._PDAL5 = None
        self._N = None
        self._R = None

    @property
    def POLII(self): return self._POLII

    @POLII.setter
    def POLII(self, value): self._POLII = value

    @property
    def AWCAP(self): return self._AWCAP

    @AWCAP.setter
    def AWCAP(self, value): self._AWCAP = value

    @property
    def PL(self): return self._PL

    @PL.setter
    def PL(self, value): self._PL = value

    @property
    def PDAL5(self): return self._PDAL5

    @PDAL5.setter
    def PDAL5(self, value): self._PDAL5 = value

    @property
    def N(self): return self._N

    @N.setter
    def N(self, value): self._N = value

    @property
    def R(self): return self._R

    @R.setter
    def R(self, value): self._R = value

