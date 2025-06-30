import simpy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Zufallsstart für Reproduzierbarkeit
random.seed(2)
np.random.seed(2)

# Parameter
beginn_dauer_durchschnitt = 5
beginn_dauer_sigma = 1.5
trainings_dauer_durchschnitt = 90
trainings_dauer_sigma = 20
verlassen_dauer_durchschnitt = 8
verlassen_dauer_sigma = 2.5

trainerzeit_dauer_durchschnitt = 10
trainerzeit_dauer_sigma = 3

besucher_ankunftszeit_durchschnitt = 3
besucher_ankunftszeit_sigma = 1.5

simulationsdauer = 840  # 1 Tag in Minuten(14 Stunden) -> 8:00 Uhr bis 22:00 Uhr
# gerät wartezeiten
geraet_wartezeit = []
geraet_nutzung_dauer_durchschnitt = 15  # Minuten
geraet_nutzung_dauer_sigma = 5

# Globale Listen zur Erfassung von Metriken
wartezeiten = []
trainer_service_dauer = []
def intervalAnkunftszeit(env_now):
    if 480 <= env_now <= 600: #16-18 Uhr kommen die meisten Besucher
        return random.uniform(0, 4) # Alle 0-4 Minuten kommt ein neuer Besucher
    elif 600 < env_now <= 720:
        return random.uniform(0, 5) # Alle 0-5 Minuten kommt ein neuer Besucher
    elif 820 <= env_now <= 840: 
        return 0 # keine neuen Besucher mehr 20 Minuten vor Schließung
    else:
        return random.uniform(4, 10) # Alle 4-10 Minuten kommt ein neuer Besucher
def Fitnessstudiobesucher(env, besucherid, trainer, typ, geraet):
    global wartezeiten, trainer_service_dauer
    print(int(env.now), 'Besucher', besucherid, ' betritt den Parkplatz %d' % int(env.now), 'Minuten nach Öffnung')
    max_beginn_dauer = simulationsdauer - env.now - 1
    beginn_dauer = min(max(0, random.gauss(beginn_dauer_durchschnitt, beginn_dauer_sigma)), max_beginn_dauer)
    yield env.timeout(beginn_dauer)
    if env.now >= simulationsdauer - 1:
        print(int(env.now), 'Besucher ', besucherid, ' verlässt das Fitnessstudio ', int(env.now), ' aufgrund von Schließung')
        return  # Besucher muss gehen
    max_trainings_dauer = simulationsdauer - env.now - 1
    trainings_dauer = max(0,min(max(0, random.gauss(trainings_dauer_durchschnitt, trainings_dauer_sigma)), max_trainings_dauer))
    for t in range(int(env.now), int(env.now + trainings_dauer)):
        besucher_pro_minute[t] = besucher_pro_minute.get(t, 0) + 1
    print('Besucher', besucherid, ' betritt das Fitnessstudio, beginnt mit dem Training %d' % int(env.now), 'Minuten nach Öffnung')
    yield env.timeout(trainings_dauer)
    if env.now >= simulationsdauer - 1:
        print(int(env.now), 'Besucher ', besucherid, ' verlässt das Fitnessstudio ', int(env.now), ' aufgrund von Schließung')
        return  # Besucher muss gehen
    if( typ == 'Beginner'):
        needs_help = random.uniform(0.3, 1) # Anfänger brauchen oft Hilfe -> 71% der Zeit
    elif( typ == 'Fortgeschritten'):
        needs_help = random.uniform(0, 0.8) # Fortgeschrittene brauchen manchmal Hilfe -> 37,5% der Zeit
    else:  # Profi
        needs_help = random.uniform(0, 0.55)# Profis brauchen selten Hilfe -> 10% der Zeit
    if needs_help > 0.5:
        print('Besucher ', besucherid, ' braucht Hilfe')
        minute = int(env.now)
        hilfe_pro_minute[minute] = hilfe_pro_minute.get(minute, 0) + 1
        t_request = env.now
        with trainer.request() as req:
            yield req
            wartezeit = env.now - t_request
            wartezeiten.append(wartezeit)
            max_trainerzeit = simulationsdauer - env.now - 1
            trainerzeit = max(0,min(max(0, random.gauss(trainerzeit_dauer_durchschnitt, trainerzeit_dauer_sigma)), max_trainerzeit))
            verfuegbar = trainer.capacity - trainer.count
            print(int(env.now), "Trainer", trainer.count, " kümmert sich um Besucher ", besucherid, " um ", int(env.now), ". Es sind noch ", verfuegbar, " Trainer verfügbar. Es werden ", int(trainerzeit), " Minuten gewartet")
            
            t_start = env.now
            yield env.timeout(trainerzeit)
            trainer_service_dauer.append(env.now - t_start)
            verfuegbar = trainer.capacity - trainer.count
            print(int(env.now), "Trainer", trainer.count, " hat die Hilfe für Besucher ", besucherid, " beendet. Es sind jetzt wieder ", verfuegbar, " Trainer verfügbar")
    if random.random() < 0.9:
        t_request = env.now
        with geraet.request() as req:
            yield req
            wartezeit = env.now - t_request
            geraet_wartezeit.append(wartezeit)
            print(f"{int(env.now)} Besucher {besucherid} wartet auf Gerät bei Minute {env.now:.1f}")
            max_geraet_nutzung_dauer = simulationsdauer - env.now - 1
            dauer = max(0,min(max(0, random.gauss(geraet_nutzung_dauer_durchschnitt, geraet_nutzung_dauer_sigma)),max_geraet_nutzung_dauer))
            yield env.timeout(dauer)
            print(f"{int(env.now)} Besucher {besucherid} verlässt das Gerät bei Minute {env.now:.1f}")

    

    max_verlassen_dauer = simulationsdauer - env.now - 1
    verlassen_duration = max(0,min(max(0, random.gauss(verlassen_dauer_durchschnitt, verlassen_dauer_sigma)), max_verlassen_dauer))
    print(int(env.now), 'Besucher ', besucherid,' verlässt das Fitnessstudio %d' % int(env.now))
    yield env.timeout(verlassen_duration)
    if env.now >= simulationsdauer - 1:
        print(int(env.now), 'Besucher ', besucherid, ' verlässt das Fitnessstudio ', int(env.now), ' aufgrund von Schließung')
        return  # Besucher muss gehen


def generiereFitnessstudiobesucher(env, trainer, geraet):
    besucherid = 0
    while env.now < simulationsdauer - 20:

        besucherid += 1
        besuchertyp = random.choice(['Beginner', 'Fortgeschritten', 'Profi'])
        env.process(Fitnessstudiobesucher(env, besucherid, trainer, besuchertyp, geraet))
        yield env.timeout(intervalAnkunftszeit(env.now))

def run_scenario(anz_trainer, anz_geraete):
    global wartezeiten, trainer_service_dauer, besucher_pro_minute, hilfe_pro_minute, geraet_wartezeit
    wartezeiten = []
    trainer_service_dauer = []
    besucher_pro_minute = {}
    hilfe_pro_minute = {}
    geraet_wartezeit = []

    env = simpy.Environment()
    trainer = simpy.Resource(env, capacity=anz_trainer)
    geraet = simpy.Resource(env, capacity=anz_geraete)  

    env.process(generiereFitnessstudiobesucher(env, trainer, geraet))
    env.run(until=simulationsdauer)
    durchschnittliche_wartezeit_geraet = np.mean(geraet_wartezeit) if geraet_wartezeit else 0.0
    durchschnittliche_wartezeit_trainer = np.mean(wartezeiten) if wartezeiten else 0.0
    maximale_wartezeit_trainer = np.max(wartezeiten) if wartezeiten else 0.0
    auslastung_trainer = sum(trainer_service_dauer) / (anz_trainer * simulationsdauer) if anz_trainer > 0 else 0

    return {
        'trainers': anz_trainer,
        'geraete': anz_geraete,
        'avg_wait_geraet': durchschnittliche_wartezeit_geraet,
        'avg_wait': durchschnittliche_wartezeit_trainer,
        'max_wait': maximale_wartezeit_trainer,
        'utilization': auslastung_trainer, 
        'besucher_pro_minute': besucher_pro_minute
    }

# Szenarien testen für 1 bis 10 Trainer
results = [run_scenario(n, n+2) for n in range(1, 11)]
df = pd.DataFrame(results)
print(df)

# Plotten
plt.figure(figsize=(12, 16))
plt.subplot(2, 2, 1)
plt.plot(df['trainers'], df['utilization'], marker='s', label='Auslastung der Trainer')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Werte')
plt.title('Auslastung in Abhängigkeit der Traineranzahl')
plt.grid(True)
plt.legend()
plt.subplot(2, 2, 2)
plt.plot(df['trainers'], df['avg_wait'], marker='s', label='Durchschnittliche Wartezeit')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Durchschnittliche Wartezeit (Minuten)')
plt.title('Durchschnittliche Wartezeit in Abhängigkeit der Traineranzahl')
plt.grid(True)
plt.legend()

plt.suptitle('Simulationsergebnisse für Fitnessstudio-Besucher', fontsize=16)
plt.subplot(2, 2, 3)
plt.plot(df['trainers'], df['max_wait'], marker='s', label='Maximale Wartezeit')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Maximale Wartezeit (Minuten)')
plt.title('Maximale Wartezeit in Abhängigkeit der Traineranzahl')
plt.legend()
plt.grid(True)
plt.subplot(2, 2, 4)
plt.plot(df['geraete'], df['avg_wait_geraet'], marker='s', color='teal')
plt.title("Durchschnittliche Wartezeit am Gerät")
plt.xlabel("Anzahl Geräte")
plt.ylabel("Durchschnittliche Wartezeit (Minuten)")
plt.grid(True)
plt.legend()
plt.show()
verlaufsdaten_besucher_list = [pd.Series(res['besucher_pro_minute'], name=res['trainers']) for res in results]
heatmap_df_besucher = pd.concat(verlaufsdaten_besucher_list, axis=1).reindex(range(simulationsdauer)).fillna(0).astype(int)

durchschnitt_besucher = heatmap_df_besucher.mean(axis=1) # Durchschnitt der Besucheranzahl über alle Szenarien berechnen

# Plot 3: Durchschnittliche Studioauslastung
fig, ax = plt.subplots(figsize=(15, 7))
durchschnitt_besucher.plot(kind='line', ax=ax, color='teal')
ax.set_title('Durchschnittliche Studioauslastung im Tagesverlauf', fontsize=16)
ax.set_xlabel('Minute der Simulation (0 = 8:00 Uhr)')
ax.set_ylabel('Durchschnittl. Anzahl gleichzeitiger Besucher')
ax.grid(True, linestyle='--', alpha=0.6)
plt.show()

