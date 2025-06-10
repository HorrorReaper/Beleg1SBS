import random
toleranzLaenge = 0.2 # in cm pro 10cm
toleranzDicke = 0.02 #in cm pro 8mm
Dichte = 5.0 # in g/cm^3
idealeMasse =10*10*0.8*Dichte
res = 0
for i in range(0, 10):
    laengeL1 = 10 +(random.uniform(-1, 1) * toleranzLaenge)
    laengeL2 = 10 +(random.uniform(-1, 1) * toleranzLaenge)
    dicke = 0.0008 +(random.uniform(-1, 1) * toleranzDicke)
    volumen = laengeL1 * laengeL2 * dicke
    masse = volumen * Dichte
    res += masse
print ("Die Masse beträgt: ", res, "g")
print ("Die ideale Masse beträgt: ", idealeMasse, "g")
if abs(res/ (idealeMasse * 10) - 1) > 0.02:
    print("Die Abweichung ist zu groß")