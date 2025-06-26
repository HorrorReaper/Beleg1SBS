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

simulationsdauer = 840  # 1 Tag in Minuten

# Globale Listen zur Erfassung von Metriken
wait_times = []
service_times = []
def intervalAnkunftszeit(env_now):
    if 480 <= env_now <= 600:
        return random.uniform(1, 4)
    elif 660 <= env_now <= 720:
        return random.uniform(1, 5)
    else:
        return random.uniform(4, 10)
def Fitnessstudiobesucher(env, besucherid, trainer, typ):
    global wait_times, service_times
    beginn_dauer = max(0, random.gauss(beginn_dauer_durchschnitt, beginn_dauer_sigma))
    print('Besucher', besucherid, ' betritt den Parkplatz %d' % env.now, 'Minuten nach Öffnung')
    yield env.timeout(beginn_dauer)
    if( typ == 'Beginner'):
        needs_help = random.uniform(0.3, 1)
    elif( typ == 'Fortgeschritten'):
        needs_help = random.uniform(0, 0.8)
    else:  # Profi
        needs_help = random.uniform(0, 0.55)
    if needs_help > 0.5:
        print('Besucher ', besucherid, ' braucht Hilfe')
        t_request = env.now
        with trainer.request() as req:
            yield req
            wait = env.now - t_request
            wait_times.append(wait)
            print("Trainer", trainer.count, " kümmert sich um Besucher ", besucherid, " um ", env.now, ". Es sind noch ", trainer.capacity, " Trainer verfügbar")
            trainerzeit = max(0, random.gauss(trainerzeit_dauer_durchschnitt, trainerzeit_dauer_sigma))
            t_start = env.now
            yield env.timeout(trainerzeit)
            service_times.append(env.now - t_start)

    trainings_dauer = max(0, random.gauss(trainings_dauer_durchschnitt, trainings_dauer_sigma))
    print('Besucher', besucherid, ' betritt das Fitnessstudio, beginnt mit dem Training %d' % env.now, 'Minuten nach Öffnung')
    yield env.timeout(trainings_dauer)

    verlassen_duration = max(0, random.gauss(verlassen_dauer_durchschnitt, verlassen_dauer_sigma))
    print('Besucher ', besucherid,' verlässt das Fitnessstudio %d' % env.now)
    yield env.timeout(verlassen_duration)

def generiereFitnessstudiobesucher(env, trainer):
    besucherid = 0
    while True:
        besucherid += 1
        print("Besucher kommt an ", besucherid, " zur Zeit: ", env.now)
        typ = random.choice(['Beginner', 'Fortgeschritten', 'Profi'])
        env.process(Fitnessstudiobesucher(env, besucherid, trainer, typ))
        '''intervalAnkunftszeit = np.clip(
            np.random.normal(besucher_ankunftszeit_durchschnitt, besucher_ankunftszeit_sigma),
            besucher_ankunftszeit_min,
            besucher_ankunftszeit_max
        )'''
        yield env.timeout(intervalAnkunftszeit(env.now))

def run_scenario(num_trainers):
    global wait_times, service_times
    wait_times = []
    service_times = []

    env = simpy.Environment()
    trainer = simpy.Resource(env, capacity=num_trainers)
    env.process(generiereFitnessstudiobesucher(env, trainer))
    env.run(until=simulationsdauer)

    avg_wait = np.mean(wait_times) if wait_times else 0.0
    max_wait = np.max(wait_times) if wait_times else 0.0
    utilization = sum(service_times) / (num_trainers * simulationsdauer) if num_trainers > 0 else 0

    return {
        'trainers': num_trainers,
        'avg_wait': avg_wait,
        'max_wait': max_wait,
        'utilization': utilization
    }

# Szenarien testen für 1 bis 10 Trainer
results = [run_scenario(n) for n in range(1, 11)]
df = pd.DataFrame(results)
print(df)

# Plotten
plt.figure(figsize=(10, 5))
plt.plot(df['trainers'], df['avg_wait'], marker='o', label='Durchschnittliche Wartezeit')
plt.plot(df['trainers'], df['utilization'], marker='s', label='Auslastung der Trainer')
plt.xlabel('Anzahl Trainer')
plt.ylabel('Werte')
plt.title('Wartezeit und Auslastung in Abhängigkeit der Traineranzahl')
plt.legend()
plt.grid(True)
plt.show()
