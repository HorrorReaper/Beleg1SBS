import numpy as np
import matplotlib.pyplot as plt
import random
# Zölle in der USA steigen auf ausländische Produkte -> Produktpreise steigen
# US Einwohner müssen mehr Geld für Waren aus dem Ausland ausgeben, es wird weniger gekauft, Armut steigt
# mit steigender Armut sinkt die Nachfrage nach Waren im Allgemeinen
# ebenfalls sinkt mit höheren Produktpreisen auch der internationale Absatz der USA 
# mit sinkender Nachfrage sinkt die Produktion, es werden weniger Waren hergestellt
# mit sinkender Produktion sinkt die Nachfrage nach Arbeitskräften, es werden weniger Arbeitskräfte eingestellt
# mit sinkender Nachfrage nach Arbeitskräften sinkt die Beschäftigung, es gibt mehr Arbeitslose und Armut steigt weiter

#Ich gehe davon aus, dass ein Wirtschaftscrash entstehen würde, wenn mind. 2 der 5 folgenden Kriterien erfüllt sind:
# Nachfrage	unter 70 % des Startwertes
# Produktion unter 60 % des Startwertes
# Beschäftigung	unter 80 % des Startwertes
# Einkommen	unter 75 % des Startwertes
# Absatz fällt unter 70% des Startwertes
# Diese Kriterien sind natürlich willkürlich gewählt, aber sie sollten eine realistische Annäherung an die Wirtschaftslage darstellen.
# Reale Kennzahlen:
# 2025: 
# durchschnittlicher Haushalt verliert $3800
# Verlust von 142000 Arbeitsplätzen
# Konsumentenpreise steigen um 2,3% durch Zölle alleine
# 15-16% des GDP der USA entfallen auf Auslandsimporte
# Inflationsrate ist bei 2,4%
# Arbeitslosigkeit ist bei 4%, bis Q4 2025 wird sie auf 4,3% steigen
# Nachfrage und Absatz sind jeweils um 0,9% gefallen
# Produktion ist um 0,4% gefallen 
# Durchschnittseinkommen eines Haushalts sind 77540 USD



class Finanzkrise:
    def __init__(self):
        #Parameterinitialisierung
        self.zollsatz = 0.225  # initiale Zollrate -> 22,5%
        self.zollsatz_steigung = 0.05  # Zölle steigen um 5% pro Jahr
        self.zollsatz_max = 0.50  # maximale Zollrate -> 50%
        self.initialesEinkommen = 77540  # Durchschnittseinkommen USA in USD eines Haushalts
        self.einkommen = self.initialesEinkommen
        self.inflationsrate = 0.024  # initiale Inflationsrate -> 2,4%
        self.initialerProduktPreisIndex = 100  # initialer Produktpreisindex -> 100
        self.produktpreis_index = self.initialerProduktPreisIndex + self.zollsatz  # Produktpreisindex (im ersten Jahr bereits um den Zollsatz erhöht)
        self.initialeNachfrage = 100  # initiale Nachfrage nach Waren
        self.nachfrageThreshold = 0.01  # Mindestnachfrage, um einen totalen Marktkollaps zu vermeiden (1% der initialen Nachfrage)
        self.nachfrage = self.initialeNachfrage
        self.initialeProduktion = 100  # initiale Produktion von Waren
        self.produktion = self.initialeProduktion
        self.initialeArbeiter = 150000000  # initiale Arbeiteranzahl in den USA
        self.initialerAbsatz = 100
        self.absatz = self.initialerAbsatz #Absatz mit initialwert 100
        self.importanteil = 0.155  # Anteil der Importe am BIP der USA (15,5%)
        self.arbeiter = self.initialeArbeiter
        
        #Koeffizienten(Sensitivitäten)
        self.einkommensPreisSensitivitaet = 0.18  # Sensitivität von Einkommen gegenüber Preisänderungen des allgemeinen Produktpreisindex
        self.einkommensBeschaeftigungsSensitivitaet = 0.018  # Sensitivität von Einkommen gegenüber Beschäftigungsänderungen
        
        self.nachfragePreisSensitivitaet = 0.007  # Sensitivität der Nachfrage gegenüber Preisänderungen des Produktpreisindex
        self.nachfrageEinkommensSensitivitaet = 0.001  # Sensitivität der Nachfrage gegenüber Einkommensänderungen des durchschnittlichen US-Haushalts
        self.produktionsNachfrageSensitivitaet = 0.65  # Sensitivität der Produktion gegenüber Nachfrageänderungen
        self.arbeiterProduktionsSensitivitaet = 0.17  # Sensitivität der Anzahl der Arbeiter gegenüber Produktionsänderungen
        self.absatzPreisSensitivitaet = 0.032  # Sensitivität des Absatzes gegenüber Preisänderungen des Produktpreisindex

        # Crashkennzahlen
        self.crash_nachfrage_threshold = 0.7 * self.initialeNachfrage  # Nachfrage unter 70% des Startwertes
        self.crash_produktions_threshold = 0.6 * self.initialeProduktion  # Produktion unter 60% des Startwertes
        self.crash_beschaeftigung_threshold = 0.8 * self.initialeArbeiter  # Beschäftigung unter 80% des Startwertes
        self.crash_einkommen_threshold = 0.75 * self.initialesEinkommen  # Einkommen unter 75% des Startwertes
        self.crash_absatz_threshold = 0.7 * self.initialerAbsatz  # Absatz unter 70% des Startwertes 



    def update(self,year):
        if year > 0:
            self.einkommensPreisSensitivitaet = 0.05  
            self.einkommensBeschaeftigungsSensitivitaet = 0.008  

            self.nachfragePreisSensitivitaet = 0.02  
            self.nachfrageEinkommensSensitivitaet = 0.005 

            self.produktionsNachfrageSensitivitaet = 0.4  
            self.arbeiterProduktionsSensitivitaet = 0.08  

            self.absatzPreisSensitivitaet = 0.02  

        # Kriseneffekt simulieren
        self.zollsatz = min(self.zollsatz + self.zollsatz_steigung, self.zollsatz_max) # Zölle werden jährlich erhöht, es gibt allerdings eine Obergrenze von 50%
        if self.zollsatz < self.zollsatz_max:  # Wenn der Zollsatz unter dem Maximum liegt, wird der Produktpreisindex erhöht
            preissteigerung_durch_zoelle = self.zollsatz_steigung * ( self.produktpreis_index / self.initialerProduktPreisIndex) # Zölle erhöhen die Preise der importierten Waren, was sich auf den Produktpreisindex auswirkt
        else:
            preissteigerung_durch_zoelle = 0
        self.produktpreis_index *= (1 + (self.importanteil * preissteigerung_durch_zoelle) + self.inflationsrate) # Produktpreise steigen durch Zölle und Inflation
        self.einkommen *= (1 - self.einkommensPreisSensitivitaet * (self.produktpreis_index / self.initialerProduktPreisIndex - 1) - self.einkommensBeschaeftigungsSensitivitaet * (1 - self.arbeiter / self.initialeArbeiter)) # Einkommen sinkt durch steigende Preise und sinkende Beschäftigung
        self.nachfrage *= max(self.nachfrageThreshold, 1.0 - (self.nachfragePreisSensitivitaet * (self.produktpreis_index / self.initialerProduktPreisIndex)) - (self.nachfrageEinkommensSensitivitaet * (1 - self.einkommen / self.initialesEinkommen))) # self.nachfrage kann nicht unter 1% der initialen Nachfrage fallen, um eine totale Marktkollaps zu vermeiden
        self.produktion *= (1 - self.produktionsNachfrageSensitivitaet * (1 - self.nachfrage / self.initialeNachfrage)) # wenn die Nachfrage sinkt, sinkt auch die Produktion
        self.arbeiter = round(self.arbeiter * (1 - self.arbeiterProduktionsSensitivitaet * (1 - self.produktion / self.initialeProduktion))) # wenn die Produktion sinkt, sinkt auch die Nachfrage nach Arbeitskräften
        self.inflationsrate = random.uniform(0.01, 0.06)  # Inflation liegt zufällig zwischen 1% und 6%
        self.absatz *= (1 - self.absatzPreisSensitivitaet * (self.produktpreis_index / 100 - 1))  # Absatz sinkt durch steigende Preise
        

    def simulate(self, years=10):
        self.produktpreis_index *= (1 + self.zollsatz)
        history = []
        crash_jahr = None  # Wann tritt der Crash ein?
        i = 0
        boolean_array = [False] * 5  # Array, um die Erfüllung der Kriterien zu verfolgen
        history.append(( self.nachfrage, self.produktion, self.arbeiter, self.zollsatz, self.einkommen, self.inflationsrate, self.produktpreis_index, self.absatz, boolean_array))

        for year in range(years):
            self.update(year)
            if (self.nachfrage < self.crash_nachfrage_threshold):
                i += 1
                boolean_array[0] = True
            if (self.produktion < self.crash_produktions_threshold):
                i += 1
                boolean_array[1] = True
            if (self.arbeiter < self.crash_beschaeftigung_threshold):
                i += 1
                boolean_array[2] = True
            if (self.einkommen < self.crash_einkommen_threshold):
                i += 1
                boolean_array[3] = True
            if(self.absatz < self.crash_absatz_threshold):
                i += 1
                boolean_array[4] = True
            print(f"Jahr {2025 + year}: Nachfrage={self.nachfrage:.2f}, Produktion={self.produktion:.2f}, Arbeiter={self.arbeiter:.2f}, Zollsatz={self.zollsatz * 100:.2f}%, Einkommen={self.einkommen:.2f}, Inflationsrate={self.inflationsrate:.2f}%, Produktpreis Index={self.produktpreis_index:.2f}, Absatz={self.absatz:.2f}")
            if i >= 2:  # Wenn mindestens 2 der 5 Kriterien erfüllt sind, wird ein Crash angenommen
                if crash_jahr is None:
                    crash_jahr = year + 1
            history.append(( self.nachfrage, self.produktion, self.arbeiter, self.zollsatz, self.einkommen, self.inflationsrate, self.produktpreis_index, self.absatz, boolean_array))
        return history, crash_jahr
    def plot_results(self, history):
        startjahr = 2025
        years = list(range(startjahr, startjahr + len(history)))
        nachfrage, produktion, beschaeftigte, zollsatz, einkommen, inflationsrate, produktpreis_index, absatz, boolean_array = zip(*history)

        plt.figure(figsize=(12, 16))
        plt.subplot(2, 2, 1)
        plt.plot(years, absatz, label='Absatz')
        plt.title('Absatz über Zeitraum')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')
        if boolean_array[4]:
            plt.axhline(y=self.crash_absatz_threshold, color='red', linestyle='--', alpha=0.5, label='Absatzschwelle (70% des Startwertes)')
        plt.xlabel('Jahre')
        plt.ylabel('Absatz (Basis 100)')
        plt.legend()
        plt.grid()

        plt.subplot(2, 2, 2)
        plt.plot(years, nachfrage, label='Nachfrage', color='orange')
        plt.title('Nachfrage über Zeitraum')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')
        if boolean_array[0]:
            plt.axhline(y=self.crash_nachfrage_threshold, color='red', linestyle='--', alpha=0.5, label='Nachfragesschwelle (70% des Startwertes)')
        plt.xlabel('Jahre')
        plt.ylabel('Nachfrage (Basis 100)')
        plt.legend()
        plt.grid()

        plt.subplot(2, 2, 3)
        plt.plot(years, produktion, label='Produktion', color='green')
        plt.title('Produktion über Zeitraum')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')
        if boolean_array[1]:
            plt.axhline(y=self.crash_produktions_threshold, color='red', linestyle='--', alpha=0.5, label='Produktionsschwelle (60% des Startwertes)')
        plt.xlabel('Jahre')
        plt.ylabel('Produktion (Basis 100)')
        plt.legend()
        plt.grid()

        plt.subplot(2, 2, 4)
        plt.plot(years, beschaeftigte, label='Beschäftigung', color='red')
        plt.title('Beschäftigung über Zeitraum')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')
        if boolean_array[2]:
            plt.axhline(y=self.crash_beschaeftigung_threshold, color='red', linestyle='--', alpha=0.5, label='Beschäftigungsschwelle (80% des Startwertes)')
        plt.xlabel('Jahre')
        plt.ylabel('Beschäftigung')
        plt.grid()
        plt.suptitle('Wirtschaftskrise')
        plt.legend()
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.figure(figsize=(12, 8))


        plt.subplot(2, 2, 1)
        plt.plot(years, zollsatz, label='Zollrate', color='purple')
        plt.title('Zollrate über Zeitraum')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')

        plt.xlabel('Jahre')
        plt.ylabel('Zollrate (%)')
        plt.legend()
        plt.grid()
        plt.subplot(2, 2, 2)
        plt.plot(years, produktpreis_index, label='Produkt Preis Index', color='brown')
        plt.title('Produkt Preis Index über Zeitraum')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')

        plt.xlabel('Jahre')
        plt.ylabel('Produkt Preis Index(Basis 100)')
        plt.legend()
        plt.grid()
        plt.subplot(2, 2, 3)
        plt.plot(years, einkommen, label='durchschnittliches Haushaltseinkommen', color='cyan')
        plt.title('durchschnittliches Haushaltseinkommen über Zeitraum')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')
        if boolean_array[3]:
            plt.axhline(y=self.crash_einkommen_threshold, color='red', linestyle='--', alpha=0.5, label='Einkommensschwelle (75% des Startwertes)')
        plt.xlabel('Jahre')
        plt.ylabel('Einkommen')
        plt.legend()
        plt.grid()
        plt.subplot(2, 2, 4)
        plt.plot(years, inflationsrate, label='Inflationsrate', color='magenta')
        plt.title('Inflationsrate')
        if crash_jahr is not None:
            plt.axvline(x=startjahr + crash_jahr, color='black', linestyle='--', alpha=0.7, label='Crash-Jahr')
        
        plt.xlabel('Jahre')
        plt.ylabel('Inflationsrate(%)')
        plt.grid()
        plt.suptitle('Wirtschaftsindikatoren über Zeitraum')
        plt.legend()
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])


        plt.tight_layout()
        plt.show()
# Example usage
if __name__ == "__main__":
    crisis = Finanzkrise()
    history, crash_jahr = crisis.simulate(years=10)
    crisis.plot_results(history)     
    if crash_jahr is not None:
        print(f"Wirtschaftscrash erkannt im Jahr {2025 + crash_jahr}!")
    else:
        print("Kein wirtschaftlicher Crash in den nächsten 10 Jahren.") 
        