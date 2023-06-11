"""Swing-By Manöver"""

import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation

#Importiere die notwendigen Elemente für die GUI.
from PyQt5 import QtWidgets
from PyQt5.uic import loadUiType

#Lade das mit dem Qt Designer erstellte Benutzerinterface.
MainWindow = loadUiType('MainWindow.ui')[0]

#Expliziter Euler
def euler(G, mP, mS, r0P, r0S, v0P, v0S, t, dt):
    
     #Array für die Position und die Geschwindigkeit der Sonde und des Planeten
     vP = np.zeros((2, len(t)))
     rP = np.zeros((2, len(t)))
     
     vS = np.zeros((2, len(t)))
     rS = np.zeros((2, len(t)))
     
     
     #Übergabe der Anfangsbedingungen des Planeten und der Sonde
     vP[0,0] = v0P[0] 
     vP[1,0] = v0P[1]
     rP[0,0] = r0P[0]
     rP[1,0] = r0P[1]  
     
     vS[0,0] = v0S[0]
     vS[1,0] = v0S[1]
     rS[0,0] = r0S[0]
     rS[1,0] = r0S[1] 
     
     #Berechnung der numerischen Lösung
     for n in range(len(t)-1):          

         #Hier wird die Geschwindigkeit für die x-und y-Komponente zum Zeitpunkt t+1 berechnet
         vS[0,n+1] = vS[0,n] + dt * (G * mP / (np.linalg.norm(rS[:,n] - rP[:,n]))**3 * (rP[0,n] - rS[0,n]))
         vS[1,n+1] = vS[1,n] + dt * (G * mP / (np.linalg.norm(rS[:,n] - rP[:,n]))**3 * (rP[1,n] - rS[1,n]))
         
         #Position der Sonde und des Planeten zum Zeitpunkt t+1
         rP[0,n+1] = rP[0,n] + dt * vP[0,0]
         rP[1,n+1] = rP[1,n] + dt * vP[1,0]
         
         rS[0,n+1] = rS[0,n] + dt * vS[0,n]
         rS[1,n+1] = rS[1,n] + dt * vS[1,n]                
            
         d =  np.linalg.norm(rS[:,n]-rP[:,n])               #Distanz zwischen den Körpern 
         
         if d < 69.911e6:
             print("Abgestürzt")
             break
         
     return np.concatenate([vP, vS, rP, rS])                #Rückgabewert als Array der Lösungen

#Swing-By-Algorithmus und Plot
def swingby(m, r0, v0):
    
    #Konstanten -----------------
    G = 6.674e-11                                           #Gravitationskonstante [m^2/kg*s^2]
    
    stunde = 60 * 60
    tag = 24 * stunde
    
    mP = 1.898e27                                           #Masse des Jupiters [kg]
    mS = m                                                  #Masse der Sonde [kg]

    T = 36 * tag
    dt = 0.5 * stunde

    s_Jupiter = 20.18e9                                     #Anfangsentfernung vom Saturn [m]
    
    #Anfangsposition
    r0P = np.array([s_Jupiter, 0.0])
    r0S = r0                    

    #Anfangsgeschwdigkeit
    v0P = np.array([-13e3, 0.0])
    v0S = v0
        
    #Zeitintervall
    t = np.arange(0, T, dt)  
    
    #Ergebnis des "Eulers" und Verteilung auf 4 Arrays
    result = euler(G, mP, mS, r0P, r0S, v0P, v0S, t, dt)
    vP, vS, rP, rS = np.split(result, 4)
    
    #Betrag für die Geschwindigkeit der Raumsonde.
    geschwindigkeit = np.linalg.norm(vS, axis=0)

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_tight_layout(True)

    #Figur erzeugen mit Achsenbeschriftung
    ax1.set_xlabel('$x$ [m]')
    ax1.set_ylabel('$y$ [m]')
    ax1.set_xlabel('$x$ [m]')
    ax1.grid()   

    #Bahnkurve der Körper Plotten
    ax1.plot(rP[0, :], rP[1, :], '-b')
    ax1.plot(rS[0, :], rS[1, :], '-r')

    #Plot für das v-t-Diagramm
    ax2.set_xlabel("$t$ [Tage]")
    ax2.set_ylabel("Geschwindigkeit [km/s]")
    ax2.grid()
    ax2.plot(t / tag, geschwindigkeit / 1e3)

    #Punktplot für die Körper
    koerper1, = ax1.plot([0], [1], 'o', color='blue')
    koerper2, = ax1.plot([0], [1], 'o', color='red')

    def update(n):
        #Position der Körper wird aktualisiert
        koerper1.set_data(rP[:, n])
        koerper2.set_data(rS[:, n])

        return koerper1, koerper2


    #Animationsobject
    ani = mpl.animation.FuncAnimation(fig, update, interval=40,
                                      frames=t.size, )
    #ani.save("swingby.mp4")
    plt.show()       
    return ani

#Hauptfenster mit der Abfrage
class MainWindow(QtWidgets.QMainWindow, MainWindow):

    def __init__(self):
        # Initialisiere das QMainWindow.
        super().__init__()
        self.setupUi(self)  
        
        self.button_berechne.clicked.connect(self.berechne)
    
    def closeEvent(self, event):
        #Hier werden auch gleich die Plots mitgeschlossen
        plt.close('all')
        QtWidgets.QApplication.quit()
    
    def eingabe_float(self, field):
        #Gleitkommazahl wird eingelesen       
        value = float(field.text())
        return value
    
    def berechne(self):        
        #Anfangswerte der Raumsonde
        mS = self.eingabe_float(self.edit_m1)
        r0Sx = self.eingabe_float(self.edit_r01x)*1e9
        r0Sy = self.eingabe_float(self.edit_r01y)*1e9
        v0 = self.eingabe_float(self.edit_v01)*1e3
        alpha = self.eingabe_float(self.edit_alpha)
        alpha = np.deg2rad(alpha)                           #Grad wird in Radiant umgerechnet
        
        #x und y Werte in einem Array
        r0S = np.array([r0Sx, r0Sy]) 
        
        #v01x und vo1y Werte in Array        
        v0S = np.array([v0 *np.cos(alpha), v0*np.sin(alpha)])
        print(v0S )
        
        #Swing-By Funktion wird aufgerufen
        ani = swingby(mS, r0S, v0S)
        
        #Zeichnet die Grafikelemente neu
        self.fig.canvas.draw()
        
        #ani wird "geplottet"
        plt.show()


#Erzeuge eine QApplication und das Hauptfenster.
app = QtWidgets.QApplication([])
window = MainWindow()

#Zeige das Fenster und starte die QApplication.
window.show()
app.exec_()  
