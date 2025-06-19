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

#Ich gehe davon aus, dass ein Wirtschaftscrash entstehen würde, wenn mind. 2 der 6 folgenden Kriterien erfüllt sind:
# Nachfrage	unter 70 % des Startwertes
# Produktion	unter 60–70 % des Startwertes
# Beschäftigung	unter 80 % des Startwertes
# Einkommen	unter 75 % des Startwertes
# Inflationsrate	über 8–10 %
# Absatz fällt unter 70% des Startwertes
# Diese Kriterien sind natürlich willkürlich gewählt, aber sie sollten eine realistische Annäherung an die Wirtschaftslage darstellen.
# Reale Kennzahlen:
# 2025: 
# durchschnittlicher Haushalt verliert $3800
# Verlust von 142000 Arbeitsplätzen
# Konsumentenpreise steigen um 2,3% durch Zölle alleine
# Inflationsrate ist bei 2,4%
# Arbeitslosigkeit ist bei 4%, bis Q4 2025 wird sie auf 4,3% steigen
# Einkommen ist seit Anfang 2025 um 2,5% gestiegen
# Nachfrage und Absatz sind jeweils um 0,9% gefallen
# Produktion ist um 0,4% gefallen seit 2024



class Finanzkrise:
    def __init__(self):
        #Parameter
        self.zollsatz = 0.225  # initiale Tariff Rate -> 25%
        self.zollsatz_steigung = 0.05  # Tariffs steigen um 5% pro Jahr
        self.zollsatz_max = 0.50  # maximale Tariff Rate -> 50%
        self.einwohneranzahl = 330000000  # USA Einwohneranzahl
        self.initialesEinkommen = 50000  # Durchschnittseinkommen USA in USD
        self.einkommen = self.initialesEinkommen
        self.inflationsrate = 0.024  # initiale Inflationsrate -> 2,4%
        self.produktpreis_index = 100  # initialer Produktpreisindex -> 100
        self.initialeNachfrage = 1000  # initiale Nachfrage nach Waren
        self.nachfrageThreshold = 0.01  # Mindestnachfrage, um einen totalen Marktkollaps zu vermeiden (1% der initialen Nachfrage)
        self.nachfrage = self.initialeNachfrage
        self.initialeProduktion = 1000  # initiale Produktion von Waren
        self.produktion = self.initialeProduktion
        self.initialeArbeiter = 150000000  # initiale Arbeiteranzahl in den USA
        self.initialerAbsatz = 100
        self.absatz = self.initialerAbsatz #Absatz mit initialwert 100
        
        self.arbeiter = self.initialeArbeiter
        
        #Koeffizienten
        self.einkommensPreisSensitivitaet = 0.005  # Sensitivität von Einkommen gegenüber Preisänderungen des allgemeinen Produktpreisindex
        self.einkommensBeschaeftigungsSensitivitaet = 0.001  # Sensitivität von Einkommen gegenüber Beschäftigungsänderungen
        
        self.produktionsPreisSensitivitaet = 0.01  # sensitivity of production to price changes
        self.produktionsEinkommensSensitivitaet = 0.005  # sensitivity of production to income changes
        self.produktionsNachfrageSensitivitaet = 0.05  # sensitivity of production to demand changes
        self.arbeiterProduktionsSensitivitaet = 0.005  # sensitivity of employment to production changes
        self.absatzPreisSensitivitaet = 0.01  # sensitivity of sales to price changes



    def update(self):
        # Simulate the effects of the crisis
        self.zollsatz = min(self.zollsatz + self.zollsatz_steigung, self.zollsatz_max) # Tariffs werden jährlich erhöht, es gibt allerdings eine Obergrenze von 50%
        import_anteil = 0.5 # 50% 
        price_increase_from_tariffs = self.zollsatz * (1.0 / self.produktpreis_index) # Zölle erhöhen die Preise der importierten Waren, was sich auf den Produktpreisindex auswirkt
        price_increase_from_inflation = self.inflationsrate 
        self.produktpreis_index *= (1 + price_increase_from_tariffs + price_increase_from_inflation) # Produktpreise steigen durch Zölle und Inflation
        self.einkommen *= (1 - self.einkommensPreisSensitivitaet * (self.produktpreis_index / 100 - 1) - self.einkommensBeschaeftigungsSensitivitaet * (1 - self.arbeiter / self.initialeArbeiter)) # Einkommen sinkt durch steigende Preise und sinkende Beschäftigung
        self.nachfrage *= max(self.nachfrageThreshold, 1.0 - (self.produktionsPreisSensitivitaet * (self.produktpreis_index / 100)) - (self.produktionsEinkommensSensitivitaet * (1 - self.einkommen / self.initialesEinkommen))) # self.nachfrage kann nicht unter 1% der initialen Nachfrage fallen, um eine totale Marktkollaps zu vermeiden
        self.produktion *= (1 - self.produktionsNachfrageSensitivitaet * (1 - self.nachfrage / self.initialeNachfrage)) # wenn die Nachfrage sinkt, sinkt auch die Produktion
        self.arbeiter *= (1 - self.arbeiterProduktionsSensitivitaet * (1 - self.produktion / self.initialeProduktion)) # wenn die Produktion sinkt, sinkt auch die Nachfrage nach Arbeitskräften
        self.inflationsrate += 1
        self.inflationsrate *= random.uniform(1.01, 1.06)  # Inflation liegt zufällig zwischen 1% und 6%
        self.absatz *= (1 - self.absatzPreisSensitivitaet * (self.produktpreis_index / 100 - 1))  # Absatz sinkt durch steigende Preise
        self.inflationsrate -= 1
        

    def simulate(self, years=10):
        self.produktpreis_index *= (1 + self.zollsatz)
        history = []
        crash_jahr = None  # Wann tritt der Crash ein?
        i = 0
        for year in range(years):
            self.update()
            if (self.nachfrage < 0.7 * self.initialeNachfrage and self.produktion < 0.7 * self.initialeProduktion and self.einkommen < 0.75 * self.initialesEinkommen and self.arbeiter < 0.85 * self.initialeArbeiter):
                if crash_jahr is None:
                    crash_jahr = year
            if (self.nachfrage < 0.7 * self.initialeNachfrage):
                i += 1
            if (self.produktion < 0.7 * self.initialeProduktion):
                i += 1
            if (self.arbeiter < 0.85 * self.initialeArbeiter):
                i += 1
            if (self.einkommen < 0.75 * self.initialesEinkommen):
                i += 1
            if(self.absatz < 0.7 * self.initialerAbsatz):
                i += 1
            print(f"Jahr {2025 + year}: Nachfrage={self.nachfrage:.2f}, Produktion={self.produktion:.2f}, Arbeiter={self.arbeiter:.2f}, Zollsatz={self.zollsatz * 100:.2f}%, Einkommen={self.einkommen:.2f}, Inflationsrate={self.inflationsrate:.2f}%, Produktpreis Index={self.produktpreis_index:.2f}, Absatz={self.absatz:.2f}")
            print(f"Vergleich: Nachfrage: {self.nachfrage / self.initialeNachfrage * 100:.2f}%, Produktion: {self.produktion / self.initialeProduktion * 100:.2f}%, Beschäftigung: {self.arbeiter / self.initialeArbeiter * 100:.2f}%, Einkommen: {self.einkommen / self.initialesEinkommen * 100:.2f}%, Inflationsrate: {self.inflationsrate:.2f}%")
            if i >= 2:  # Wenn mindestens 2 der 6 Kriterien erfüllt sind, wird ein Crash angenommen
                if crash_jahr is None:
                    crash_jahr = year
            history.append(( self.nachfrage, self.produktion, self.arbeiter, self.zollsatz, self.einkommen, self.inflationsrate, self.produktpreis_index, self.absatz))
        return history, crash_jahr
    def plot_results(self, history):
        startjahr = 2025
        years = list(range(startjahr, startjahr + len(history)))
        demand, production, employment, zollsatz, einkommen, inflationsrate, produktpreis_index, absatz = zip(*history)

        plt.figure(figsize=(12, 16))
        plt.subplot(2, 2, 1)
        plt.plot(years, absatz, label='Absatz')
        plt.title('Absatz über Zeitraum')
        plt.xlabel('Jahre')
        plt.ylabel('Absatz')
        plt.grid()

        plt.subplot(2, 2, 2)
        plt.plot(years, demand, label='Nachfrage', color='orange')
        plt.title('Nachfrage über Zeitraum')
        plt.xlabel('Jahre')
        plt.ylabel('Nachfrage')
        plt.grid()

        plt.subplot(2, 2, 3)
        plt.plot(years, production, label='Produktion', color='green')
        plt.title('Produktion über Zeitraum')
        plt.xlabel('Jahre')
        plt.ylabel('Produktion (Basis 1000)')
        plt.grid()

        plt.subplot(2, 2, 4)
        plt.plot(years, employment, label='Beschäftigung', color='red')
        plt.title('Beschäftigung über Zeitraum')
        plt.xlabel('Jahre')
        plt.ylabel('Beschäftigung')
        plt.grid()
        plt.suptitle('Wirtschaftskrise')
        plt.legend()
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        # Additional plots for tariff rate, product price index, income, and inflation rate
        plt.figure(figsize=(12, 8))


        plt.subplot(2, 2, 1)
        plt.plot(years, zollsatz, label='Zoll Rate', color='purple')
        plt.title('Zollrate über Zeitraum')
        plt.xlabel('Jahre')
        plt.ylabel('Zollrate (%)')
        plt.grid()
        plt.subplot(2, 2, 2)
        plt.plot(years, produktpreis_index, label='Produkt Preis Index', color='brown')
        plt.title('Produkt Preis Index über Zeitraum')
        plt.xlabel('Jahre')
        plt.ylabel('Produkt Preis Index(Basis 100)')
        plt.grid()
        plt.subplot(2, 2, 3)
        plt.plot(years, einkommen, label='Einkommen', color='cyan')
        plt.title('Einkommen über Zeitraum')
        plt.xlabel('Jahre')
        plt.ylabel('Einkommen')
        plt.grid()
        plt.subplot(2, 2, 4)
        plt.plot(years, inflationsrate, label='Inflationsrate', color='magenta')
        plt.title('Inflationsrate über Zeitraum kumuliert')
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
        