import sys
import math
import operator

import matplotlib.pyplot as plt
import scipy.signal

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Plot an impedance or VSWR sweep CSV.")
        print()
        print("Usage: {} <CSV>".format(sys.argv[0]))
        sys.exit(0)

    freqs = []
    swrs = []

    # Read CSV file
    with open(sys.argv[1]) as f:
        for line in f:
            fields = line.split(",")

            freq = float(fields[0])

            # Ignore DC
            if freq < 0.10:
                continue

            if len(fields) == 2:
                # SWR CSV
                swr = float(fields[1])
            elif len(fields) == 3:
                # Impedance CSV

                # Compute SWR
                r, x = float(fields[1]), float(fields[2])
                gamma = math.sqrt((r - 50)**2 + x**2)/math.sqrt((r + 50)**2 + x**2)
                try:
                    swr = (1 + gamma)/(1 - gamma)
                except ZeroDivisionError:
                    swr = math.inf

            freqs.append(freq)
            swrs.append(swr)

    # Create smoothed SWRs
    b, a = scipy.signal.firwin(64, 0.06), [1]
    filt_swrs = scipy.signal.filtfilt(b, a, swrs)

    # Plot raw SWRs
    plt.plot(freqs, swrs)
    # Plot smoothed SWRs
    plt.plot(freqs, filt_swrs, color='red')
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

    # Find minima in smoothed SWRs curve
    arg_minima = scipy.signal.argrelextrema(filt_swrs, operator.lt)[0]
    print(len(arg_minima))
    # Filter minima with SWR less than 3
    arg_minima = [e for e in arg_minima if swrs[e] < 3]
    # Annotate points if there's 15 or less
    if len(arg_minima) <= 15:
        for i in arg_minima:
            plt.annotate('{:.2f} MHz\n{:.2f} VSWR'.format(freqs[i], swrs[i]), xy=(freqs[i], swrs[i]))

    plt.show()
