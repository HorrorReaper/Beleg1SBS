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
trainerzeit_dauer_sigma = 2

besucher_ankunftszeit_durchschnitt = 3
besucher_ankunftszeit_sigma = 1.5
besucher_ankunftszeit_min = 0
besucher_ankunftszeit_max = 10

simulationsdauer = 840  # 1 Tag in Minuten -> 8:00 Uhr bis 22:00 Uhr
# gerät wartezeiten
geraet_wartezeit = []
geraet_nutzung_dauer_durchschnitt = 15  # Minuten
geraet_nutzung_dauer_sigma = 5

# Globale Listen zur Erfassung von Metriken
wait_times = []
service_times = []
def intervalAnkunftszeit(env_now):
    if 480 <= env_now <= 600: #16-18 Uhr kommen die meisten Besucher
        return random.uniform(1, 4)
    elif 600 < env_now <= 720:
        return random.uniform(1, 5)
    elif 820 <= env_now <= 840: 
        return 0 # keine neuen Besucher mehr 20 Minuten vor Schließung
    else:
        return random.uniform(4, 10)
def Fitnessstudiobesucher(env, besucherid, trainer, typ, geraet):
    global wait_times, service_times
    max_beginn_dauer = simulationsdauer - env.now - 1
    beginn_dauer = min(max(0, random.gauss(beginn_dauer_durchschnitt, beginn_dauer_sigma)), max_beginn_dauer)
    print(int(env.now), 'Besucher', besucherid, ' betritt den Parkplatz %d' % int(env.now), 'Minuten nach Öffnung')
    yield env.timeout(beginn_dauer)
    if env.now >= simulationsdauer - 1:
        print(int(env.now), 'Besucher ', besucherid, ' verlässt das Fitnessstudio ', int(env.now), ' aufgrund von Schließung')
        return  # Besucher muss gehen

    if( typ == 'Beginner'):
        needs_help = random.uniform(0.3, 1)
    elif( typ == 'Fortgeschritten'):
        needs_help = random.uniform(0, 0.8)
    else:  # Profi
        needs_help = random.uniform(0, 0.55)
    if needs_help > 0.5:
        print('Besucher ', besucherid, ' braucht Hilfe')
        minute = int(env.now)
        hilfe_pro_minute[minute] = hilfe_pro_minute.get(minute, 0) + 1
        t_request = env.now
        with trainer.request() as req:
            yield req
            wait = env.now - t_request
            wait_times.append(wait)
            max_trainerzeit = simulationsdauer - env.now - 1
            trainerzeit = max(0,min(max(0, random.gauss(trainerzeit_dauer_durchschnitt, trainerzeit_dauer_sigma)), max_trainerzeit))
            verfuegbar = trainer.capacity - trainer.count
            print(int(env.now), "Trainer", trainer.count, " kümmert sich um Besucher ", besucherid, " um ", int(env.now), ". Es sind noch ", verfuegbar, " Trainer verfügbar. Es werden ", int(trainerzeit), " Minuten gewartet")
            
            t_start = env.now
            yield env.timeout(trainerzeit)
            service_times.append(env.now - t_start)
            verfuegbar = trainer.capacity - trainer.count
            print(int(env.now), "Trainer", trainer.count, " hat die Hilfe für Besucher ", besucherid, " beendet. Es sind jetzt wieder ", verfuegbar, " Trainer verfügbar")
    if random.random() < 0.4:
        t_request = env.now
        with geraet.request() as req:
            yield req
            wait = env.now - t_request
            geraet_wartezeit.append(wait)
            print(f"{int(env.now)} Besucher {besucherid} wartet auf Gerät bei Minute {env.now:.1f}")
            max_geraet_nutzung_dauer = simulationsdauer - env.now - 1
            dauer = max(0,min(max(0, random.gauss(geraet_nutzung_dauer_durchschnitt, geraet_nutzung_dauer_sigma)),max_geraet_nutzung_dauer))
            yield env.timeout(dauer)
            print(f"{int(env.now)} Besucher {besucherid} verlässt das Gerät bei Minute {env.now:.1f}")

    max_trainings_dauer = simulationsdauer - env.now - 1
    trainings_dauer = max(0,min(max(0, random.gauss(trainings_dauer_durchschnitt, trainings_dauer_sigma)), max_trainings_dauer))
    for t in range(int(env.now), int(env.now + trainings_dauer)):
        besucher_pro_minute[t] = besucher_pro_minute.get(t, 0) + 1
    print('Besucher', besucherid, ' betritt das Fitnessstudio, beginnt mit dem Training %d' % int(env.now), 'Minuten nach Öffnung')
    yield env.timeout(trainings_dauer)
    if env.now >= simulationsdauer - 1:
        print(int(env.now), 'Besucher ', besucherid, ' verlässt das Fitnessstudio ', int(env.now), ' aufgrund von Schließung')
        return  # Besucher muss gehen

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
        print(int(env.now), "Besucher kommt an ", besucherid, " zur Zeit: ", int(env.now))
        typ = random.choice(['Beginner', 'Fortgeschritten', 'Profi'])
        env.process(Fitnessstudiobesucher(env, besucherid, trainer, typ, geraet))
        '''intervalAnkunftszeit = np.clip(
            np.random.normal(besucher_ankunftszeit_durchschnitt, besucher_ankunftszeit_sigma),
            besucher_ankunftszeit_min,
            besucher_ankunftszeit_max
        )'''
        yield env.timeout(intervalAnkunftszeit(env.now))

def run_scenario(num_trainers):
    global wait_times, service_times, besucher_pro_minute, hilfe_pro_minute, geraet_wartezeit
    wait_times = []
    service_times = []
    besucher_pro_minute = {}
    hilfe_pro_minute = {}
    geraet_wartezeit = []

    env = simpy.Environment()
    trainer = simpy.Resource(env, capacity=num_trainers)
    geraet = simpy.Resource(env, capacity=3)  # z. B. 3 Beinpressen

    env.process(generiereFitnessstudiobesucher(env, trainer, geraet))
    env.run(until=simulationsdauer)
    avg_wait_geraet = np.mean(geraet_wartezeit) if geraet_wartezeit else 0.0
    avg_wait = np.mean(wait_times) if wait_times else 0.0
    max_wait = np.max(wait_times) if wait_times else 0.0
    utilization = sum(service_times) / (num_trainers * simulationsdauer) if num_trainers > 0 else 0

    return {
        'trainers': num_trainers,
        'avg_wait_geraet': avg_wait_geraet,
        'avg_wait': avg_wait,
        'max_wait': max_wait,
        'utilization': utilization
    }

# Szenarien testen für 1 bis 10 Trainer
results = [run_scenario(n) for n in range(1, 11)]
df = pd.DataFrame(results)
print(df)

# Plotten
plt.figure(figsize=(12, 16))
plt.subplot(4, 2, 1)
plt.plot(df['trainers'], df['utilization'], marker='s', label='Auslastung der Trainer')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Werte')
plt.title('Auslastung in Abhängigkeit der Traineranzahl')
plt.legend()
plt.subplot(4, 2, 2)
plt.plot(df['trainers'], df['avg_wait'], marker='x', label='Durchschnittliche Wartezeit')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Durchschnittliche Wartezeit (Minuten)')
plt.title('Durchschnittliche Wartezeit in Abhängigkeit der Traineranzahl')
plt.legend()

plt.suptitle('Simulationsergebnisse für Fitnessstudio-Besucher', fontsize=16)
plt.subplot(4, 2, 3)
plt.plot(df['trainers'], df['max_wait'], marker='x', label='Maximale Wartezeit')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Maximale Wartezeit (Minuten)')
plt.title('Maximale Wartezeit in Abhängigkeit der Traineranzahl')
times = sorted(besucher_pro_minute.keys())
hilfe = sorted(hilfe_pro_minute.keys())
hilfe_anzahl = [hilfe_pro_minute[k] for k in hilfe]
anzahl = [besucher_pro_minute[t] for t in times]
auslastung_df = pd.DataFrame({'Minute': times, 'Anzahl Besucher': anzahl})
hilfe_df = pd.DataFrame({'Minute': hilfe, 'Anzahl Hilfe': hilfe_anzahl})
plt.subplot(4, 2, 4)
plt.plot(auslastung_df['Minute'], auslastung_df['Anzahl Besucher'], color='teal')
plt.title("Auslastung des Fitnessstudios im Tagesverlauf")
plt.xlabel("Minute seit Öffnung (8:00 Uhr)")
plt.ylabel("Anzahl gleichzeitiger Besucher")
plt.subplot(4, 2, 5)
plt.plot(hilfe_df['Minute'], hilfe_df['Anzahl Hilfe'], color='teal')
plt.title("Anzahl Hilfe im Tagesverlauf")
plt.xlabel("Minute seit Öffnung (8:00 Uhr)")
plt.ylabel("Anzahl gleichzeitiger benötigter Hilfen")
plt.subplot(4, 2, 6)
plt.plot(df['trainers'], df['avg_wait_geraet'], color='teal')
plt.title("Durchschnittliche Wartezeit am Gerät")
plt.xlabel("Anzahl Trainer(zusammenhangslos)")
plt.ylabel("Werte")
plt.grid(True)
plt.show()
