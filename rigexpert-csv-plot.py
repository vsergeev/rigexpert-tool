import sys
import math
import operator

import matplotlib.pyplot as plt
import scipy.signal

def imp_to_vswr(r, x):
    gamma = math.sqrt((r - 50)**2 + x**2)/math.sqrt((r + 50)**2 + x**2)

    try:
        swr = (1 + gamma)/(1 - gamma)
    except ZeroDivisionError:
        swr = float("inf")

    return swr

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Plot an impedance or VSWR sweep CSV.")
        print()
        print("Usage: {} <CSV>".format(sys.argv[0]))
        sys.exit(0)

    freqs = []
    vswrs = []

    # Read CSV file
    with open(sys.argv[1], "r") as f:
        for line in f:
            fields = line.split(",")

            freq = float(fields[0])

            # Ignore DC
            if freq < 0.10:
                continue

            if len(fields) == 2:
                # SWR CSV
                vswr = float(fields[1])
            elif len(fields) == 3:
                # Impedance CSV
                vswr = imp_to_vswr(float(fields[1]), float(fields[2]))

            freqs.append(freq)
            vswrs.append(vswr)

    # Create smoothed VSWRs
    b, a = scipy.signal.firwin(64, 0.06), [1]
    filt_vswrs = scipy.signal.filtfilt(b, a, vswrs)

    # Plot raw VSWRs
    plt.plot(freqs, vswrs)
    # Plot smoothed VSWRs
    plt.plot(freqs, filt_vswrs, color='red')
    # Plot 1.0 reference line
    plt.axhline(1.0, color='r', ls='dashed')

    # Add labels
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('VSWR')
    plt.title('VSWR from {:.2f} MHz to {:.2f} MHz'.format(freqs[0], freqs[-1]))

    # Set y limits to max 10.0
    yl, yh = plt.gca().get_ylim()
    plt.ylim((yl, min(yh, 10)))
    # Include 1.0 SWR in y ticks
    plt.yticks(list(plt.yticks()[0]) + [1.0])

    # Find minima in smoothed VSWRs curve
    arg_minima = scipy.signal.argrelextrema(filt_vswrs, operator.lt)[0]
    # Filter minima with SWR less than 3
    arg_minima = [e for e in arg_minima if vswrs[e] < 3]
    # Annotate points if there's 15 or less
    if len(arg_minima) <= 15:
        for i in arg_minima:
            plt.annotate('{:.2f} MHz\n{:.2f} VSWR'.format(freqs[i], vswrs[i]), xy=(freqs[i], vswrs[i]))

    plt.show()
