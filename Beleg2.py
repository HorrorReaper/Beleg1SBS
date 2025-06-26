import simpy
import random
import numpy as np
random.seed(2)
env = simpy.Environment()
# Simulation
#Öffnungszeiten: 8-22Uhr
beginn_dauer_min = 1 #Leute brauchen mindestens 1 Minute, um anzufangen (direkt vom Auto ohne umziehen)
beginn_dauer_max = 20 #Leute brauchen maximal 20 Minuten, um anzufangen (umziehen, quatschen,...)
beginn_dauer_durchschnitt = 5
beginn_dauer_sigma = 1.5
trainings_dauer_min = 20
trainings_dauer_max = 180
trainings_dauer_durchschnitt = 90
trainings_dauer_sigma = 20
wait_times = [] # Liste für Wartezeiten der Trainer
service_times = [] # Liste für Servicezeiten der Trainer

verlassen_dauer_durchschnitt = 8
verlassen_dauer_sigma = 2.5
gesamtanzahl_besucher = 0
needs_help = 0

#Zeit, die Trainer für Besucher braucht
trainerzeit_dauer_durchschnitt = 10
trainerzeit_dauer_sigma = 2
besucherid = 0
# Besucher ankunftszeit
besucher_ankunftszeit_min = 0 #es kommen mehrere hintereinander
besucher_ankunftszeit_max = 10 #10min nach dem vorherigen besucher kommt ein neuer Fitnessstudiobesucher
besucher_ankunftszeit_durchschnitt = 3
def Fitnessstudiobesucher(env,besucherid):
    while True:

        beginn_dauer = random.gauss(beginn_dauer_durchschnitt, beginn_dauer_sigma)
        while beginn_dauer < 0:
            beginn_dauer = random.gauss(beginn_dauer_durchschnitt, beginn_dauer_sigma)
        print('Besucher', besucherid, ' betritt den Parkplatz %d' % env.now, 'Minuten nach Öffnung')
        yield env.timeout(beginn_dauer)
        needs_help = random.uniform(0, 0.8)
        if needs_help > 0.5:
            # wenn der Kunde Hilfe benötigt:
            t_request = env.now
            with trainer.request() as req:
                yield req
                wait = env.now - t_request
                wait_times.append(wait)
                t_start = env.now
                yield env.timeout(trainerzeit)
                service_times.append(env.now - t_start)
 #           print('Besucher ', besucherid, ' braucht Hilfe')
 #           trainerreq = trainer.request()
 #           yield trainerreq
            print("Trainer", trainer.count, " kümmert sich um Besucher ", besucherid, " um ", env.now, ". Es sind noch ", trainer.capacity, " Trainer verfügbar")
            trainerzeit = random.gauss(trainerzeit_dauer_durchschnitt, trainerzeit_dauer_sigma)
 #           yield env.timeout(trainerzeit)
 #           trainer.release(trainerreq)
        trainings_dauer = random.gauss(trainings_dauer_durchschnitt, trainings_dauer_sigma)
        while trainings_dauer < 0:
            trainings_dauer = random.gauss(trainings_dauer_durchschnitt, trainings_dauer_sigma)
        print('Besucher', besucherid, ' betritt das Fitnessstudio, beginnt mit dem Training %d' % env.now, 'Minuten nach Öffnung')
        yield env.timeout(trainings_dauer)
        verlassen_duration = random.gauss(verlassen_dauer_durchschnitt, verlassen_dauer_sigma)
        while verlassen_duration < 0:
            verlassen_duration = random.gauss(verlassen_dauer_durchschnitt, verlassen_dauer_sigma)
        print('Besucher ', besucherid,' verlässt das Fitnessstudio %d' % env.now)
        yield env.timeout(verlassen_duration)
def generiereFitnessstudiobesucher(env, anzahl, intervalankunftszeit):
    global gesamtanzahl_besucher
    besucherid = 0
    while True:
        besucherid += 1
        print("Besucher kommt an ", besucherid, " zur Zeit: ", env.now)
        env.process(Fitnessstudiobesucher(env, besucherid))
        gesamtanzahl_besucher += 1
        yield env.timeout(intervalankunftszeit)
def generiereFitnessstudiobesucher(env):
    global gesamtanzahl_besucher
    global besucherid
    while True:
        besucherid += 1
        print("Besucher kommt an ", besucherid, " zur Zeit: ", env.now)
        env.process(Fitnessstudiobesucher(env, besucherid))
        intervalAnkunftszeit = np.clip(np.random.normal(besucher_ankunftszeit_durchschnitt, 1.5), besucher_ankunftszeit_min, besucher_ankunftszeit_max)
        yield env.timeout(intervalAnkunftszeit)
        gesamtanzahl_besucher += 1
        print("Hallo",gesamtanzahl_besucher)
#env.process( generiereFitnessstudiobesucher(env, 10, 5))
env.process(generiereFitnessstudiobesucher(env))
trainer = simpy.Resource(env, capacity = 5) # 5 trainer sind verfügbar
env.run(until=840)
print("Gesamtanzahl Besucher:", gesamtanzahl_besucher)
# 1. Vorlesung 1. Juli(Dienstag) Online 9.00-10.30
# Abnahme 8. Juli 8.30-9.45