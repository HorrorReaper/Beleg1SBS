import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import random
#Parameter
immobilienCrashFaktor =random.uniform(0.35, 0.45)  # Zufällige Anpassung des Crash-Faktors
immobilienCrashFaktorBankgesundheit = random.uniform(0.15, 0.23)  # Zufällige Anpassung des Crash-Faktors für Banken
crashSchadensfaktor = random.uniform(0.6, 0.8)  # Zufällige Anpassung des Schadensfaktors beim Crash
crashThreshold = random.uniform(1.2, 1.5)  # Zufällige Anpassung des Schwellenwerts für den Crash
erholungThreshold = random.uniform(0.7, 0.9)  # Zufällige Anpassung des Erholungsschwellenwerts
panikThreshold = random.uniform(0.4, 0.6)  # Zufällige Anpassung des Panik-Schwellenwerts
erholungsFaktor = random.uniform(0.05, 0.1)  # Zufällige Anpassung des Erholungsfaktors
arbeitslosigkeitsFaktor = random.uniform(0.1, 0.3)  # Zufällige Anpassung des Arbeitslosigkeitsfaktors
arbeitslosigkeitsThreshold = random.uniform(0.05, 0.09)  # Zufällige Anpassung des Schwellenwerts für Arbeitslosigkeit
rettungspaketStaat = True  # Ob der Staat ein Rettungspaket geschnürt hat

class FinanzKrise:
    """
    Einfache kontinuierliche Simulation der Finanzkrise 2008
    
    Kernidee: Modellierung der wichtigsten Zusammenhänge:
    1. Immobilienblase wächst
    2. Banken werden instabil
    3. Vertrauen bricht ein
    4. Wirtschaft leidet
    """
    
    def __init__(self):
        # Einfache Parameter
        self.blasenwachstum = np.random.normal(0.2, 0.05)      # Wie schnell wächst die Immobilienblase
        self.bank_risiko = np.random.normal(0.5, 0.05)          # Wie riskant sind die Banken
        self.vertrauensVerlust = np.random.normal(0.3, 0.05)     # Wie schnell verliert man Vertrauen
        self.erholungWirtschaft = np.random.normal(0.2, 0.05)            # Wie schnell erholt sich das System
    
    def konti_system(self, state, Jahre):
        """
        Das Herzstück: Die Differentialgleichungen
        
        Wir haben 3 Hauptvariablen:
        - house_prices: Immobilienpreise (1.0 = normal, >1.0 = Blase)
        - bank_health: Gesundheit der Banken (1.0 = gesund, 0.0 = pleite)
        - confidence: Vertrauen der Menschen (1.0 = volles Vertrauen, 0.0 = Panik)
        """
        haeuser_preise, bank_gesundheit, vertrauen, dArbeitslosigkeit_dt = state
        
        # 1. IMMOBILIENPREISE
        # Steigen durch Vertrauen, fallen wenn Banken schlecht sind
        crash_start = 3.0  # Wann platzt die Blase? (3 Jahre)
        if rettungspaketStaat:
            crash_end = 6.0
        if Jahre < crash_start :  # Ersten 3 Jahre: Blase wächst
            dImmobilienmarkt_dt = self.blasenwachstum * vertrauen * haeuser_preise # Bsp: 0,2*0,8 = 16% pro Jahr wachstum
        elif Jahre > crash_start and Jahre < crash_end:  # In den 3 Jahren nach der Blase
            dImmobilienmarkt_dt = -immobilienCrashFaktor * haeuser_preise + immobilienCrashFaktorBankgesundheit * bank_gesundheit
        else:  # Dann: Blase platzt
            dImmobilienmarkt_dt = self.erholungWirtschaft * (1.0 - haeuser_preise) + 0.05 * vertrauen
            

        # 2. BANKEN-GESUNDHEIT  
        # Leiden unter fallenden Immobilienpreisen (haben viele Kredite vergeben)
        # Erholen sich langsam
        erholung = 0
        if Jahre < crash_end:
            risiko_von_haeusern = -self.bank_risiko * max(0, haeuser_preise - 1.0)  # Risiko bei Blase
            crash_schaden = -crashSchadensfaktor * max(0, crashThreshold - haeuser_preise)  # Schaden beim Crash
        else:  # Nach der Blase: Banken erholen sich langsam
            risiko_von_haeusern = 0  # Kein Risiko mehr, da Blase geplatzt
            crash_schaden = 0
            erholung = self.erholungWirtschaft * (erholungThreshold - bank_gesundheit)  # Langsame Erholung

        
        dbank_dt = risiko_von_haeusern + crash_schaden + erholung
        
        # 3. VERTRAUEN
        # Sinkt wenn Banken schlecht sind, erholt sich langsam
        if Jahre < crash_start or Jahre > crash_end: # In den ersten 3 Jahren: Vertrauen wächst
            dVertrauen_dt = self.blasenwachstum * vertrauen
        else:  # Nach der Blase: Vertrauen bricht ein
            panik = -self.vertrauensVerlust * max(0, panikThreshold - bank_gesundheit)  # Panik bei Bank-Problemen
            natuerliche_erholung = erholungsFaktor * (erholungThreshold - vertrauen)  # Natürliche Erholung
        
            dVertrauen_dt = panik + natuerliche_erholung
        # 4. ARBEITSLOSIGKEIT (optional, aber realistisch)
        # Arbeitslosigkeit steigt bei Bankenproblemen, sinkt bei Erholung
        dArbeitslosigkeit_dt = 0 # Initialwert
        if Jahre > crash_start and Jahre < crash_end:  # In den ersten 3 Jahren nach der Blase
            dArbeitslosigkeit_dt = arbeitslosigkeitsThreshold*(arbeitslosigkeitsFaktor * max(0, 1- bank_gesundheit))
        elif Jahre >= crash_end:  # Nach der Blase: Arbeitslosigkeit sinkt langsam
            dArbeitslosigkeit_dt = -arbeitslosigkeitsFaktor * max(0, arbeitslosigkeitsThreshold - dArbeitslosigkeit_dt)


        
        return [dImmobilienmarkt_dt, dbank_dt, dVertrauen_dt, dArbeitslosigkeit_dt]
    
    def simulation(self, jahre=10):
        """Führt die Simulation durch"""
        
        # Startwerte (2005)
        initial_state = [
            1.0,  # house_prices: Normal
            0.9,  # bank_health: Ziemlich gesund
            0.8,   # confidence: Gutes Vertrauen
            0.05   # arbeitslosigkeit: 5% 
        ]
        
        # Zeit von 2005 bis 2005+years
        zeit = np.linspace(0, jahre, jahre * 50)  # 50 Punkte pro Jahr
        
        # Simulation durchführen
        resultat = odeint(self.konti_system, initial_state, zeit)
        
        return zeit, resultat
    
    def plots_erstellen(self, zeit, resultat):
        """Erstellt die Plots"""
        
        # Daten extrahieren
        haeuser_preise = resultat[:, 0]
        bank_gesundheit = resultat[:, 1] 
        vertrauen = resultat[:, 2]
        arbeitslosigkeit = resultat[:, 3]  
        
        # Plot erstellen
        plt.figure(figsize=(12, 8))
        
        # Oberer Plot: Die drei Hauptvariablen
        plt.subplot(2, 1, 1)
        plt.plot(zeit + 2005, haeuser_preise, 'b-', linewidth=2, label='Immobilienpreise')
        plt.plot(zeit + 2005, bank_gesundheit, 'r-', linewidth=2, label='Banken-Gesundheit')
        plt.plot(zeit + 2005, vertrauen, 'g-', linewidth=2, label='Marktvertrauen')
        plt.plot(zeit + 2005, arbeitslosigkeit, 'k-', linewidth=2, label='Arbeitslosigkeit')
        
        plt.axvline(x=2008, color='red', linestyle='--', alpha=0.7, label='Krise 2008')
        if rettungspaketStaat:plt.axvline(x=2011, color='blue', linestyle='--', alpha=0.7, label='Rettungspaket Staat')
        plt.title('Finanzkrise 2008 - Kontinuierliche Simulation', fontsize=14, fontweight='bold')
        plt.xlabel('Jahr')
        plt.ylabel('Relative Werte (1.0 = Normal)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Unterer Plot: Phasen der Krise
        plt.subplot(2, 1, 2)
        
        # Farbkodierte Bereiche für verschiedene Phasen
        farben = []
        for i in range(len(zeit)):
            if haeuser_preise[i] > 1.2:  # Blase
                farben.append('orange')
            elif bank_gesundheit[i] < 0.5:  # Krise
                farben.append('red') 
            elif vertrauen[i] < 0.4:  # Panik
                farben.append('darkred')
            else:  # Normal/Erholung
                farben.append('lightblue')
        
        plt.scatter(zeit + 2005, haeuser_preise, c=farben, s=10, alpha=0.6)
        plt.title('Krisenphasen (Orange=Blase, Rot=Bankkrise, Dunkelrot=Panik, Blau=Normal)')
        plt.xlabel('Jahr')
        plt.ylabel('Immobilienpreise')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return haeuser_preise, bank_gesundheit, vertrauen, arbeitslosigkeit
    
    def krisenanalyse(self, zeit, resultat):
        """Einfache Analyse der Krisenergebnisse"""
        
        haeuser_preise = resultat[:, 0]
        bank_gesundheit = resultat[:, 1]
        vertrauen = resultat[:, 2]
        arbeitslosigkeit = resultat[:, 3]  # Optional, falls benötigt
        jahre = zeit + 2005
        
        print("=== EINFACHE KRISENANALYSE ===")
        print()
        
        # Wann war die Blase am größten?
        max_bubble_idx = np.argmax(haeuser_preise)
        print(f"Höchste Immobilienpreise: {jahre[max_bubble_idx]:.1f} (Faktor {haeuser_preise[max_bubble_idx]:.2f})")
        
        # Wann waren die Banken am schlechtesten?
        min_bank_idx = np.argmin(bank_gesundheit)
        print(f"Schlechteste Banken-Situation: {jahre[min_bank_idx]:.1f} (Gesundheit: {bank_gesundheit[min_bank_idx]:.2f})")
        
        # Wann war das Vertrauen am niedrigsten?
        min_confidence_idx = np.argmin(vertrauen)
        print(f"Niedrigstes Vertrauen: {jahre[min_confidence_idx]:.1f} (Niveau: {vertrauen[min_confidence_idx]:.2f})")
        
        # Wie lange dauerte die Krise?
        krisenstart = None
        krisenende = None
        
        for i, gesundheit in enumerate(bank_gesundheit):
            if gesundheit < 0.7 and krisenstart is None:
                krisenstart = jahre[i]
            if gesundheit > 0.7 and krisenstart is not None and krisenende is None:
                krisenende = jahre[i]
                break
        
        if krisenstart and krisenende:
            print(f"Krisendauer: {krisenstart:.1f} bis {krisenende:.1f} ({krisenende-krisenstart:.1f} Jahre)")
        
        print()
        print("Interpretation:")
        if haeuser_preise[max_bubble_idx] > 1.5:
            print("- Deutliche Immobilienblase erkennbar")
        if bank_gesundheit[min_bank_idx] < 0.3:
            print("- Schwere Bankenkrise")
        if vertrauen[min_confidence_idx] < 0.3:
            print("- Vertrauenskrise/Panik")


# === HAUPTPROGRAMM ===
def main():
    print("Starte einfache Finanzkrise-Simulation...")
    print("Modelliert: Immobilienblase → Bankenkrise → Vertrauensverlust")
    print()
    
    # Simulation erstellen und durchführen
    krise = FinanzKrise()
    zeit, resultat = krise.simulation(jahre=10)
    
    # Ergebnisse plotten
    house_prices, bank_health, confidence, arbeitslosigkeit = krise.plots_erstellen(zeit, resultat)
    
    # Analyse durchführen
    krise.krisenanalyse(zeit, resultat)
    
    print("\n=== NÄCHSTE SCHRITTE ===")
    print("Diese einfache Simulation zeigt die Grunddynamik.")
    print("Mögliche Erweiterungen:")
    print("- Arbeitslosigkeit hinzufügen")
    print("- Staatsverschuldung modellieren") 
    print("- Verschiedene Szenarien (mit/ohne Rettungspakete)")
    print("- Realistische Parameter aus echten Daten")
    
    return krise, zeit, resultat

# Simulation starten
if __name__ == "__main__":
    model, time_data, results = main()