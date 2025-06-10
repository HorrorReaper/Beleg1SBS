import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import random
# Zölle in der USA steigen auf ausländische Produkte -> Produktpreise steigen
# US Einwohner müssen mehr Geld für Waren aus dem Ausland ausgeben, es wird weniger gekauft, Armut steigt
# mit steigender Armut sinkt die Nachfrage nach Waren im Allgemeinen
# mit sinkender Nachfrage sinkt die Produktion, es werden weniger Waren hergestellt
# mit sinkender Produktion sinkt die Nachfrage nach Arbeitskräften, es werden weniger Arbeitskräfte eingestellt
# mit sinkender Nachfrage nach Arbeitskräften sinkt die Beschäftigung, es gibt mehr Arbeitslose und Armut steigt weiter




class Finanzkrise:
    def __init__(self):
        #Parameter
        self.zollsatz = 0.25  # initial tariff rate -> 25%
        self.zollsatz_steigung = 0.05  # tariff rate increase per year -> 5%
        self.zollsatz_max = 0.50  # maximum tariff rate -> 50%
        self.einwohneranzahl = 330000000  # US population
        self.initialesEinkommen = 50000  # average income in USD
        self.arbeitslosenrate = 0.05  # initial unemployment rate -> 5%
        self.inflationsrate = 0.02  # initial inflation rate -> 2%
        self.produktpreis_index = 100  # initial product price index
        self.initialeNachfrage = 1000  # initial demand for goods
        self.initialeProduktion = 1000  # initial production of goods
        self.initialeArbeiter = 150_000_000  # initial employment in millions
        self.einkommen = self.initialesEinkommen
        self.nachfrage = self.initialeNachfrage
        self.arbeiter = self.initialeArbeiter
        self.produktion = self.initialeProduktion
        #Koeffizienten
        self.einkommensPreisSensitivitaet = 0.005  # sensitivity of income to price changes
        self.einkommensBeschaeftigungsSensitivitaet = 0.001  # sensitivity of income to employment changes
        self.nachfrageThreshold = 0.01  # sensitivity of demand to price changes
        self.produktionsPreisSensitivitaet = 0.01  # sensitivity of production to price changes
        self.produktionsEinkommensSensitivitaet = 0.005  # sensitivity of production to income changes
        self.produktionsNachfrageSensitivitaet = 0.05  # sensitivity of production to demand changes
        self.arbeiterProduktionsSensitivitaet = 0.005  # sensitivity of employment to production changes



    def update(self):
        # Simulate the effects of the crisis
        self.zollsatz = min(self.zollsatz + self.zollsatz_steigung, self.zollsatz_max) # Tariffs werden jährlich erhöht, es gibt allerdings eine Obergrenze von 50%
        price_increase_from_tariffs = self.zollsatz * (1.0 / self.produktpreis_index) # hier wird angenommen, dass der Zollsatz direkt den Produktpreisindex beeinflusst
        price_increase_from_inflation = self.inflationsrate # Inflation beeinflusst den Produktpreisindex direkt
        self.produktpreis_index *= (1 + price_increase_from_tariffs + price_increase_from_inflation)

        self.einkommen *= (1 - self.einkommensPreisSensitivitaet * (self.produktpreis_index / 100 - 1) - self.einkommensBeschaeftigungsSensitivitaet * (1 - self.arbeiter / self.initialeArbeiter))
        nachfrage_reduktionsfaktor = 1.0 - (self.produktionsPreisSensitivitaet * (self.produktpreis_index / 100)) - (self.produktionsEinkommensSensitivitaet * (1 - self.einkommen / self.initialesEinkommen))
        self.nachfrage *= max(self.nachfrageThreshold, nachfrage_reduktionsfaktor) 
        #self.nachfrage *= 0.95  # Demand decreases by 5%
        self.produktion *= (1 - self.produktionsNachfrageSensitivitaet * (1 - self.nachfrage / self.initialeNachfrage))
        self.arbeiter *= (1 - self.arbeiterProduktionsSensitivitaet * (1 - self.produktion / self.initialeProduktion)) # wenn die Produktion sinkt, sinkt auch die Nachfrage nach Arbeitskräften
        self.inflationsrate *= random.uniform(1.01, 1.06)  

    def simulate(self, years=10):
        self.produktpreis_index *= (1 + self.zollsatz)
        history = []
        for year in range(years):
            self.update()
            history.append((self.einwohneranzahl, self.nachfrage, self.produktion, self.arbeiter, self.zollsatz, self.einkommen, self.inflationsrate, self.produktpreis_index))
        return history
    def plot_results(self, history):
        years = list(range(len(history)))
        population, demand, production, employment, zollsatz, einkommen, inflationsrate, produktpreis_index = zip(*history)

        plt.figure(figsize=(12, 16))
        plt.subplot(2, 2, 1)
        plt.plot(years, population, label='Population')
        plt.title('Population Over Time')
        plt.xlabel('Years')
        plt.ylabel('Population')
        plt.grid()

        plt.subplot(2, 2, 2)
        plt.plot(years, demand, label='Demand', color='orange')
        plt.title('Demand Over Time')
        plt.xlabel('Years')
        plt.ylabel('Demand')
        plt.grid()

        plt.subplot(2, 2, 3)
        plt.plot(years, production, label='Production', color='green')
        plt.title('Production Over Time')
        plt.xlabel('Years')
        plt.ylabel('Production')
        plt.grid()

        plt.subplot(2, 2, 4)
        plt.plot(years, employment, label='Employment', color='red')
        plt.title('Employment Over Time')
        plt.xlabel('Years')
        plt.ylabel('Employment')
        plt.grid()
        plt.suptitle('Economic Crisis Simulation Results')
        plt.legend()
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        # Additional plots for tariff rate, product price index, income, and inflation rate
        plt.figure(figsize=(12, 8))


        plt.subplot(2, 2, 1)
        plt.plot(years, zollsatz, label='Tariff Rate', color='purple')
        plt.title('Tariff Rate Over Time')
        plt.xlabel('Years')
        plt.ylabel('Tariff Rate')
        plt.grid()
        plt.subplot(2, 2, 2)
        plt.plot(years, produktpreis_index, label='Product Price Index', color='brown')
        plt.title('Product Price Index Over Time')
        plt.xlabel('Years')
        plt.ylabel('Product Price Index')
        plt.grid()
        plt.subplot(2, 2, 3)
        plt.plot(years, einkommen, label='Income', color='cyan')
        plt.title('Income Over Time')
        plt.xlabel('Years')
        plt.ylabel('Income')
        plt.grid()
        plt.subplot(2, 2, 4)
        plt.plot(years, inflationsrate, label='Inflation Rate', color='magenta')
        plt.title('Inflation Rate Over Time')
        plt.xlabel('Years')
        plt.ylabel('Inflation Rate')
        plt.grid()
        plt.suptitle('Economic Indicators Over Time')
        plt.legend()
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])


        plt.tight_layout()
        plt.show()
# Example usage
if __name__ == "__main__":
    crisis = Finanzkrise()
    history = crisis.simulate(years=10)
    crisis.plot_results(history)      
        