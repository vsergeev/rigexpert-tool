import sys
import math
import scipy.signal

def read_csv(f):
    for line in f:
        yield tuple(line.split(","))

def imp_to_vswr(stream):
    for (freq, r, x) in stream:
        r, x = float(r), float(x)

        gamma = math.sqrt((r - 50)**2 + x**2)/math.sqrt((r + 50)**2 + x**2)

        try:
            vswr = (1 + gamma)/(1 - gamma)
        except ZeroDivisionError:
            vswr = math.inf

        yield (freq, vswr)

def smooth_vswr(stream, num_taps=64, alpha=0.06):
    freqs, vswrs = zip(*list(stream))

    # Determine first non-inf sample index
    start_index = 0 if math.inf not in vswrs else (len(vswrs) - vswrs[::-1].index(math.inf))

    # Filter VSWRs, starting at first non-inf sample
    b, a = scipy.signal.firwin(num_taps, alpha), [1]
    filt_vswrs = scipy.signal.filtfilt(b, a, vswrs[start_index:])

    # Concatenate leading inf samples
    filt_vswrs = list(vswrs[:start_index]) + list(filt_vswrs)

    return zip(freqs, filt_vswrs)

def dump_vswr(stream):
    for (freq, vswr) in stream:
        print("{},{}".format(freq, vswr))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Convert sweep CSV from impedance to VSWR.")
        print()
        print("Usage: {} [--smooth] <impedance sweep CSV>".format(sys.argv[0]))
        print()
        print("Example:")
        print("    python3 {} sweep.imp.csv > sweep.swr.csv".format(sys.argv[0]))
        print()
        print("Example (smoothed version):")
        print("    python3 rigexpert-csv-imp2swr.py --smooth sweep.imp.csv > sweep.smooth.swr.csv")
        print()
        print("Impedance CSV format:")
        print("    <freq in MHz>,<resistance in ohms>,<reactance in ohms>")
        print("    e.g. 15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms")
        print()
        print("VSWR CSV format:")
        print("     <freq in MHz>,<voltage swr>")
        print("    e.g. 15.040000,1.01131434816733 is F=15.04 MHz,VSWR=1.01131434816733")
        sys.exit(0)

    smooth = len(sys.argv) == 3 and sys.argv[1] == "--smooth"
    filepath = sys.argv[2] if len(sys.argv) == 3 else sys.argv[1]

    with open(filepath, "r") as f:
        if smooth:
            dump_vswr(smooth_vswr(imp_to_vswr(read_csv(f))))
        else:
            dump_vswr(imp_to_vswr(read_csv(f)))
