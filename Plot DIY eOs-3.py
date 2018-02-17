# Protótipo 40
### Programa de gravação de áudio e plotagem ao vivo do sinal

#BIBLIOTECAS MATEMÁTICAS E GRÁFICAS
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import sys
import scipy
from scipy import signal

#BIBLIOTECAS DE AUDIO
import pyaudio
import struct

#class PlotWindow É uma classe associa os dados (atributos) e operações (métodos) numa estrutura só.
class PlotWindow:
    def __init__(self):
        #DEFINIÇÕES INICIAIS

        #Self 
        self.win=pg.GraphicsWindow()
        self.win.setWindowTitle(u"Plot DYE eOs - LAFISA")
        self.plt=self.win.addPlot() #Relaconamento Visual
        self.plt.setYRange(-1,1)    #Definição dos limites inferiores e superiores do eixo Y
        self.curve=self.plt.plot()  #Onde colocar os dados

        #CONFIGURAÇÃO DA ENTRADA DO MICROFONE
        self.CHUNK=1024             #Largura de dados de áudio a ser lida de uma vez só
        self.RATE=44100             #Frequência de amostragem
        self.audio=pyaudio.PyAudio()
        self.stream=self.audio.open(format=pyaudio.paInt16,channels=1,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)

        #CONFIGURAÇÃO DO TEMPO DE ATUALIZAÇÃO AO VIVO
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)    #Atualização a cada 10ms

        #LOCAL DE ARMAZENAMENTO DE DADOS DO SOM (DADOS DO GRÁFICO)
        self.data=np.zeros(self.CHUNK)

    def update(self):
        self.data=np.append(self.data, self.AudioInput())
        if len(self.data)/1024 > 5:     # 5 * Quando 1024 pontos são excedidos, 1024 pontos são descarregados
            self.data=self.data[1024:]
        self.curve.setData(self.data)   #Armazenar dados

    def AudioInput(self):
        b, a = signal.butter(3, 0.05) #Criar um  filtro lowpass de ordem 3 butterworth:
        ret=self.stream.read(self.CHUNK)    #Leitura de audio (BINÁRIO)
        #Conversão do valor binário para númerico (int16)
        #É normal dividir por 32768.0 = 2 ^ 16 (fazer valor absoluto inferior a 1)
        ret=np.frombuffer(ret, dtype="int16")/32768.0
        scipy.signal.lfilter(b, a, x=ret, axis=-1, zi=None)
        #Aplicar o filtro no xn. Use lfilter_zi para escolher a condição inicial do filtro
        zi = signal.lfilter_zi(b, a)
        z, _ = signal.lfilter(b, a, ret, zi=zi*ret[0])
        #Aplique o filtro novamente, para que um resultado seja filtrado em uma ordem o mesmo que filtfilt:
        z2, _ = signal.lfilter(b, a, z, zi=zi*z[0])
        #Use filtfilt para aplicar o filtro:
        y = signal.filtfilt(b, a, ret)
        print(y)
        return y

if __name__=="__main__":
    plotwin=PlotWindow()
    if (sys.flags.interactive!=1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
