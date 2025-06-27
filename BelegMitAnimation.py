import simpy
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Initialisierung
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
simulationsdauer = 840

besucher_pro_minute = {}

def intervalAnkunftszeit(env_now):
    if 480 <= env_now <= 600:
        return random.uniform(1, 4)
    elif 660 <= env_now <= 720:
        return random.uniform(1, 5)
    else:
        return random.uniform(4, 10)

def Fitnessstudiobesucher(env, besucherid, trainer, typ):
    beginn_dauer = max(0, random.gauss(beginn_dauer_durchschnitt, beginn_dauer_sigma))
    yield env.timeout(beginn_dauer)

    needs_help = {
        'Beginner': random.uniform(0.3, 1),
        'Fortgeschritten': random.uniform(0, 0.8),
        'Profi': random.uniform(0, 0.55)
    }[typ]

    if needs_help > 0.5:
        with trainer.request() as req:
            yield req
            trainerzeit = max(0, random.gauss(trainerzeit_dauer_durchschnitt, trainerzeit_dauer_sigma))
            yield env.timeout(trainerzeit)

    trainings_dauer = max(0, random.gauss(trainings_dauer_durchschnitt, trainings_dauer_sigma))
    for t in range(int(env.now), int(env.now + trainings_dauer)):
        besucher_pro_minute[t] = besucher_pro_minute.get(t, 0) + 1
    yield env.timeout(trainings_dauer)

    verlassen_duration = max(0, random.gauss(verlassen_dauer_durchschnitt, verlassen_dauer_sigma))
    yield env.timeout(verlassen_duration)

def generiereFitnessstudiobesucher(env, trainer):
    besucherid = 0
    while True:
        besucherid += 1
        typ = random.choice(['Beginner', 'Fortgeschritten', 'Profi'])
        env.process(Fitnessstudiobesucher(env, besucherid, trainer, typ))
        yield env.timeout(intervalAnkunftszeit(env.now))

def simulate(num_trainers=5):
    global besucher_pro_minute
    besucher_pro_minute = {}
    env = simpy.Environment()
    trainer = simpy.Resource(env, capacity=num_trainers)
    env.process(generiereFitnessstudiobesucher(env, trainer))
    env.run(until=simulationsdauer)

simulate()

# Animation erstellen
minutes = sorted(besucher_pro_minute.keys())
visitor_counts = [besucher_pro_minute[m] for m in minutes]

fig, ax = plt.subplots(figsize=(10, 5))
line, = ax.plot([], [], lw=2, color='teal')
ax.set_xlim(0, 840)
ax.set_ylim(0, max(visitor_counts) + 5)
ax.set_title("Live-Auslastung des Fitnessstudios")
ax.set_xlabel("Minute seit Öffnung (8:00 Uhr)")
ax.set_ylabel("Anzahl Besucher")
ax.grid(True)

x_data, y_data = [], []
def update(frame):
    x_data.append(minutes[frame])
    y_data.append(visitor_counts[frame])
    line.set_data(x_data, y_data)
    return line,

ani = FuncAnimation(fig, update, frames=len(minutes), blit=True, interval=30)
ani.save("fitnessstudio_animation.mp4", writer="ffmpeg", fps=30)
plt.show()
