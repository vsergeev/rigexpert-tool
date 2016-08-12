import sys
import math

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Convert sweep CSV from impedance to VSWR.")
        print()
        print("Usage: {} <impedance sweep CSV>".format(sys.argv[0]))
        print()
        print("Example:")
        print("    python3 {} sweep.imp.csv > sweep.swr.csv".format(sys.argv[0]))
        print()
        print("Impedance CSV format:")
        print("    <freq in MHz>,<resistance in ohms>,<reactance in ohms>")
        print("    e.g. 15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms")
        print()
        print("VSWR CSV format:")
        print("     <freq in MHz>,<voltage swr>")
        print("    e.g. 15.040000,1.01131434816733 is F=15.04 MHz,VSWR=1.01131434816733")
        sys.exit(0)

    with open(sys.argv[1], "r") as f:
        for line in f:
            freq, r, x = line.split(",")

            r, x = float(r), float(x)
            gamma = math.sqrt((r - 50)**2 + x**2)/math.sqrt((r + 50)**2 + x**2)
            try:
                swr = (1 + gamma)/(1 - gamma)
            except ZeroDivisionError:
                swr = math.inf

            print("{},{}".format(freq, swr))
