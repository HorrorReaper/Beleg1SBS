import simpy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # NEU: Seaborn für bessere Heatmaps importieren

# Zufallsstart für Reproduzierbarkeit
random.seed(2)
np.random.seed(2)

# === Parameter (unverändert) ===
beginn_dauer_durchschnitt = 5
beginn_dauer_sigma = 1.5
trainings_dauer_durchschnitt = 90
trainings_dauer_sigma = 20
verlassen_dauer_durchschnitt = 8
verlassen_dauer_sigma = 2.5

trainerzeit_dauer_durchschnitt = 10
trainerzeit_dauer_sigma = 2

besucher_ankunftszeit_durchschnitt = 3
besucher_ankunftszeit_sigma = 1.5
besucher_ankunftszeit_min = 0
besucher_ankunftszeit_max = 10

simulationsdauer = 840  # 1 Tag in Minuten -> 8:00 Uhr bis 22:00 Uhr
# gerät wartezeiten
geraet_nutzung_dauer_durchschnitt = 15  # Minuten
geraet_nutzung_dauer_sigma = 5

# === Simulationsfunktionen (unverändert) ===
def intervalAnkunftszeit(env_now):
    if 480 <= env_now <= 600: #16-18 Uhr kommen die meisten Besucher
        return random.uniform(1, 4)
    elif 600 < env_now <= 720:
        return random.uniform(1, 5)
    elif 820 <= env_now <= 840:
        return 0 # keine neuen Besucher mehr 20 Minuten vor Schließung
    else:
        return random.uniform(4, 10)

# WICHTIG: Die Funktion Fitnessstudiobesucher benötigt jetzt die Dictionaries als Argument,
# um sie zu befüllen, anstatt globale Variablen zu nutzen.
def Fitnessstudiobesucher(env, besucherid, trainer, typ, geraet, service_times, wait_times, geraet_wartezeit, besucher_pro_minute, hilfe_pro_minute):
    max_beginn_dauer = simulationsdauer - env.now - 1
    beginn_dauer = min(max(0, random.gauss(beginn_dauer_durchschnitt, beginn_dauer_sigma)), max_beginn_dauer)
    # print(int(env.now), 'Besucher', besucherid, ' betritt den Parkplatz %d' % int(env.now), 'Minuten nach Öffnung')
    yield env.timeout(beginn_dauer)
    if env.now >= simulationsdauer - 1:
        # print(int(env.now), 'Besucher ', besucherid, ' verlässt das Fitnessstudio ', int(env.now), ' aufgrund von Schließung')
        return

    if( typ == 'Beginner'):
        needs_help = random.uniform(0.3, 1)
    elif( typ == 'Fortgeschritten'):
        needs_help = random.uniform(0, 0.8)
    else:  # Profi
        needs_help = random.uniform(0, 0.55)

    if needs_help > 0.5:
        # print('Besucher ', besucherid, ' braucht Hilfe')
        minute = int(env.now)
        hilfe_pro_minute[minute] = hilfe_pro_minute.get(minute, 0) + 1
        t_request = env.now
        with trainer.request() as req:
            yield req
            wait = env.now - t_request
            wait_times.append(wait)
            max_trainerzeit = simulationsdauer - env.now - 1
            trainerzeit = max(0,min(max(0, random.gauss(trainerzeit_dauer_durchschnitt, trainerzeit_dauer_sigma)), max_trainerzeit))
            # ... print-Anweisungen können für schnellere Läufe auskommentiert werden
            t_start = env.now
            yield env.timeout(trainerzeit)
            service_times.append(env.now - t_start)

    if random.random() < 0.4:
        t_request = env.now
        with geraet.request() as req:
            yield req
            wait = env.now - t_request
            geraet_wartezeit.append(wait)
            max_geraet_nutzung_dauer = simulationsdauer - env.now - 1
            dauer = max(0,min(max(0, random.gauss(geraet_nutzung_dauer_durchschnitt, geraet_nutzung_dauer_sigma)),max_geraet_nutzung_dauer))
            yield env.timeout(dauer)

    max_trainings_dauer = simulationsdauer - env.now - 1
    trainings_dauer = max(0,min(max(0, random.gauss(trainings_dauer_durchschnitt, trainings_dauer_sigma)), max_trainings_dauer))
    
    # Anstatt zu printen, befüllen wir das Dictionary für die Auslastung
    start_training_minute = int(env.now)
    end_training_minute = int(env.now + trainings_dauer)
    for t in range(start_training_minute, min(end_training_minute, simulationsdauer)):
        besucher_pro_minute[t] = besucher_pro_minute.get(t, 0) + 1

    yield env.timeout(trainings_dauer)
    if env.now >= simulationsdauer - 1:
        return

    max_verlassen_dauer = simulationsdauer - env.now - 1
    verlassen_duration = max(0,min(max(0, random.gauss(verlassen_dauer_durchschnitt, verlassen_dauer_sigma)), max_verlassen_dauer))
    yield env.timeout(verlassen_duration)


def generiereFitnessstudiobesucher(env, trainer, geraet, service_times, wait_times, geraet_wartezeit, besucher_pro_minute, hilfe_pro_minute):
    besucherid = 0
    while env.now < simulationsdauer - 20:
        besucherid += 1
        typ = random.choice(['Beginner', 'Fortgeschritten', 'Profi'])
        # Die Dictionaries werden nun an den Prozess übergeben
        env.process(Fitnessstudiobesucher(env, besucherid, trainer, typ, geraet, service_times, wait_times, geraet_wartezeit, besucher_pro_minute, hilfe_pro_minute))
        yield env.timeout(intervalAnkunftszeit(env.now))

# --- MODIFIZIERTE run_scenario Funktion ---
def run_scenario(num_trainers):
    # Die Listen und Dictionaries sind jetzt lokal in der Funktion, nicht mehr global
    wait_times = []
    service_times = []
    besucher_pro_minute = {}
    hilfe_pro_minute = {}
    geraet_wartezeit = []

    env = simpy.Environment()
    trainer = simpy.Resource(env, capacity=num_trainers)
    geraet = simpy.Resource(env, capacity=3)

    # Die lokalen Container werden an den Generator übergeben
    env.process(generiereFitnessstudiobesucher(env, trainer, geraet, service_times, wait_times, geraet_wartezeit, besucher_pro_minute, hilfe_pro_minute))
    env.run(until=simulationsdauer)
    
    avg_wait_geraet = np.mean(geraet_wartezeit) if geraet_wartezeit else 0.0
    avg_wait = np.mean(wait_times) if wait_times else 0.0
    max_wait = np.max(wait_times) if wait_times else 0.0
    utilization = sum(service_times) / (num_trainers * simulationsdauer) if num_trainers > 0 else 0

    # NEU: Die Funktion gibt jetzt auch die Verlaufsdaten zurück
    return {
        'trainers': num_trainers,
        'avg_wait_geraet': avg_wait_geraet,
        'avg_wait': avg_wait,
        'max_wait': max_wait,
        'utilization': utilization,
        'besucher_pro_minute': besucher_pro_minute, # <-- Hinzugefügt
        'hilfe_pro_minute': hilfe_pro_minute      # <-- Hinzugefügt
    }

# === Haupt-Ausführung und Analyse ===
# Szenarien testen für 1 bis 10 Trainer
# Die 'results' Liste enthält jetzt für jedes Szenario die detaillierten Verlaufsdaten
results = [run_scenario(n) for n in range(1, 11)]
df = pd.DataFrame(results)

# Die 'print' Anweisung zeigt jetzt Spalten, die Dictionaries enthalten
print("Ergebnis-DataFrame mit aggregierten Daten und Verlaufsdaten:")
print(df[['trainers', 'avg_wait', 'max_wait', 'utilization']].round(2))


# --- NEU: Aufbereitung der Verlaufsdaten für die Heatmap ---

# 1. Heatmap für die Anzahl der Besucher (Studioauslastung)
verlaufsdaten_besucher_list = []
for res in results:
    # Wandle das Dictionary in eine Pandas Series um und gib ihr als Namen die Traineranzahl
    s = pd.Series(res['besucher_pro_minute'], name=res['trainers'])
    verlaufsdaten_besucher_list.append(s)

# Füge alle Series zu einem DataFrame zusammen. Fehlende Werte (Minuten ohne Besucher) werden zu NaN
heatmap_df_besucher = pd.concat(verlaufsdaten_besucher_list, axis=1)
# Fülle die NaNs mit 0 und stelle sicher, dass alle Minuten von 0 bis zur Simulationsdauer als Index existieren
heatmap_df_besucher = heatmap_df_besucher.reindex(range(simulationsdauer)).fillna(0).astype(int)


# 2. Heatmap für die Anzahl der benötigten Hilfen
verlaufsdaten_hilfe_list = []
for res in results:
    s = pd.Series(res['hilfe_pro_minute'], name=res['trainers'])
    verlaufsdaten_hilfe_list.append(s)
    
heatmap_df_hilfe = pd.concat(verlaufsdaten_hilfe_list, axis=1)
heatmap_df_hilfe = heatmap_df_hilfe.reindex(range(simulationsdauer)).fillna(0).astype(int)


# --- NEU: Überarbeitete Visualisierung ---

# Plot 1 & 2: Aggregierte Metriken (Wartezeit und Auslastung)
plt.figure(figsize=(14, 12))
plt.suptitle('Simulationsergebnisse für Fitnessstudio-Besucher', fontsize=18)

plt.subplot(2, 2, 1)
plt.plot(df['trainers'], df['utilization'], marker='s', label='Auslastung der Trainer')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Auslastung')
plt.title('Auslastung in Abhängigkeit der Traineranzahl')
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot(df['trainers'], df['avg_wait'], marker='x', label='Durchschnittliche Wartezeit')
plt.plot(df['trainers'], df['max_wait'], marker='o', label='Maximale Wartezeit')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Wartezeit (Minuten)')
plt.title('Wartezeiten für Trainerhilfe')
plt.legend()
plt.grid(True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


# Plot 3: Heatmap der Studioauslastung
plt.figure(figsize=(15, 6))
# Wir transponieren (.T) den DataFrame, damit die Szenarien auf der y-Achse und die Zeit auf der x-Achse liegt
sns.heatmap(heatmap_df_besucher.T, cmap='viridis')
plt.title('Heatmap der Studioauslastung (Anzahl Besucher) nach Szenario', fontsize=16)
plt.xlabel('Minute der Simulation (0 = 8:00 Uhr)')
plt.ylabel('Anzahl Trainer (Szenario)')
plt.show()

# Plot 4: Heatmap der benötigten Hilfe
plt.figure(figsize=(15, 6))
sns.heatmap(heatmap_df_hilfe.T, cmap='rocket')
plt.title('Heatmap der benötigten Trainerhilfe nach Szenario', fontsize=16)
plt.xlabel('Minute der Simulation (0 = 8:00 Uhr)')
plt.ylabel('Anzahl Trainer (Szenario)')
plt.show()