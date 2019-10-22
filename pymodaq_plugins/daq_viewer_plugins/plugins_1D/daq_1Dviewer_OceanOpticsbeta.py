# Ocean Optics using seabreeze

# mandatory imports
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo
from pymodaq.daq_utils import custom_parameter_tree
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base
from pymodaq.daq_viewer.utility_classes import comon_parameters
import numpy as np
from collections import OrderedDict
from PyQt5 import QtWidgets, QtCore
from easydict import EasyDict as edict
import time
import sys

import usb.core
import seabreeze
seabreeze.use("pyseabreeze")
import seabreeze.spectrometers as sb
time.sleep(5)
device = sb.list_devices()
time.sleep(5)
spec = sb.Spectrometer(device[0])
print(spec.model)
spec.integration_time_micros(3000)
spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
spec.close()

class DAQ_1DViewer_OceanOpticsbeta(DAQ_Viewer_base):
    """
     Template to be used in order to write your own viewer modules
    """

    params = comon_parameters+[
        {'title':'Spectrometer','name':'Spectrometer','type':'str','value':spec.model},
        {'title':'Spectrometer Settings','name':'SpecSett','type':'group','children':[
            {'title':'Exposure time (ms)','name':'exposure','type':'int','value':3,'default':3},
            {'title':'Wave Min','name':'Wave_min','type':'float','value':400,'default':400},
            {'title':'Wave Max','name':'Wave_max','type':'float','value':1000,'default':1000}
         ]}]
    hardware_averaging=False

    def __init__(self, parent=None, params_state=None):
        super(DAQ_1DViewer_OceanOpticsbeta, self).__init__(parent,params_state)  # initialize base class with commom attributes and methods

        self.controller = None

    def commit_settings(self, param):
        if param.name() == 'exposure':
            self.controller.integration_time_micros(param.value()*1000)  # in ms in the interface and in micro second in the lib

    def ini_detector(self, controller=None):
         """
         init hardware

         """
         self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
         import usb.core
         import seabreeze
         seabreeze.use("pyseabreeze")
         import seabreeze.spectrometers as sb
         time.sleep(5)
         device = sb.list_devices()
         time.sleep(5)
         self.controller = sb.Spectrometer(device[0])
         self.controller.integration_time_micros(3000)
         # %%%%%%% init axes from hardware: do xaxis if 1D viewer do both if 2D viewer
         self.x_axis = self.get_xaxis()
         self.status.initialized = True
         self.statubs.controller = self.controller
         self.emit_status(ThreadCommand('close_splash'))
         return self.status


    def close(self):
        """
        """
        self.controller.close()  # put here any specific close method of your hardware/controller if any

    def get_xaxis(self):
          """
              Obtain the horizontal axis of the detector (wavelengths)
              Returns
              -------
              1D numpy array
         """
          wave = self.controller.wavelengths()
          return wave

    def grab_data(self, Naverage=1, **kwargs):
          """
          """
          try:
              datas=[]
              data=self.controller.intensities(correct_dark_counts=True, correct_nonlinearity=True)
              QtWidgets.QApplication.processEvents()
              datas.append(OrderedDict(name=self.controller.model, data=[data], type='Data1D'))
              self.data_grabed_signal.emit(datas)

          except Exception as e:
             self.emit_status(ThreadCommand('Update_Status', [str(e), "log"]))

    def stop(self):
         """
             not implemented.
         """

         return ""
