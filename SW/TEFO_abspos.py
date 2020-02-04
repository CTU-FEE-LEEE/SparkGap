#!/usr/bin/python

#import logging
#logging.basicConfig(level=logging.DEBUG)

import sys
import time
import axis
from pymlab import config
import json


class focuser():

    def __init__(self):

        config_file = 'sparkgap.json'
        if len(sys.argv) == 3:
            config_file = sys.argv[1]
            self.pos = eval(sys.argv[2])

        print "Using config file:", config_file

        with open(config_file) as data_file:
            self.tefo_conf = json.load(data_file)
        tefo_conf = self.tefo_conf

        cfg = config.Config(i2c = tefo_conf['pymlab']['i2c'],  bus = tefo_conf['pymlab']['bus'])

        cfg.initialize()
        spi = cfg.get_device("spi")

        spi.SPI_config(spi.I2CSPI_MSB_FIRST| spi.I2CSPI_MODE_CLK_IDLE_HIGH_DATA_EDGE_TRAILING| spi.I2CSPI_CLK_461kHz)

        self.motor = axis.axis(SPI = spi, SPI_CS = spi.I2CSPI_SS0, StepsPerUnit=tefo_conf['tefo']['StepsPermm'])

        # Transition to newer axis class
        kvals = tefo_conf['tefo']['kval']
        self.motor.Setup(MAX_SPEED = tefo_conf['tefo']['speed'],
                       KVAL_ACC=kvals,
                       KVAL_RUN=kvals,
                       KVAL_DEC=kvals,
                       ACC = 100,
                       DEC = 100,
                       FS_SPD=3000,
                       STEP_MODE = axis.axis.STEP_MODE_1_16)


        self.motor.MaxSpeed(tefo_conf['tefo']['speed'])
        self.motor.Float()

        self.calib(pos = self.pos)

        self.motor.Float()

    def calib(self, pos = None):
        #pokud je software nove zapnuty (nebo neni definovany 'pos'), tak se chci vycentrovat. Jinak se navratit na 'pos' argument
        self.motor.MaxSpeed(self.tefo_conf['tefo']['speed'])
        print self.motor.getStatus()
        print "Zacatek kalibrace"
        self.motor.GoUntil( direction = 1, speed = self.tefo_conf['tefo']['home_speed'], ACT = True)
        self.motor.Wait()
        self.motor.ReleaseSW(direction = 0)

        self.motor.getStatus()
        
        print('Move na koncak dokoncen')

        self.motor.GoTo(pos, wait=True)
        self.motor.Wait()
        self.motor.Float()



def main():
    f = focuser()

if __name__ == '__main__':
    main()
