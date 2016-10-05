#!/usr/bin/env python

import argparse
import sys
import math
import scipy.signal

def read_csv(f):
    for line in f:
        yield tuple(line.split(","))

def write_csv(f, stream):
    for fields in stream:
        f.write(",".join(["{}".format(e) for e in fields]) + "\n")

def imp_to_vswr(stream):
    for (freq, r, x) in stream:
        r, x = float(r), float(x)

        gamma = math.sqrt((r - 50)**2 + x**2)/math.sqrt((r + 50)**2 + x**2)

        try:
            vswr = (1 + gamma)/(1 - gamma)
        except ZeroDivisionError:
            vswr = float("inf")

        yield (freq, vswr)

def smooth_vswr(stream, num_taps=64, alpha=0.06):
    freqs, vswrs = zip(*list(stream))

    # Filter VSWRs
    b, a = scipy.signal.firwin(num_taps, alpha), [1]
    filt_vswrs = scipy.signal.filtfilt(b, a, vswrs)

    # Translate nans to infs
    filt_vswrs[scipy.isnan(filt_vswrs)] = float("inf")

    return zip(freqs, filt_vswrs)

def main():
    parser = argparse.ArgumentParser(
        description="Convert sweep CSV from impedance to VSWR.",
        epilog=
        "Example:\n"
        "  {0} sweep.imp.csv sweep.swr.csv\n"
        "\n"
        "Example (smoothed):\n"
        "  {0} --smooth sweep.imp.csv sweep.smooth.swr.csv\n"
        "\n"
        "Impedance CSV format:\n"
        "  <freq in MHz>,<resistance in ohms>,<reactance in ohms>\n"
        "  e.g. 15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms\n"
        "\n"
        "VSWR CSV format:\n"
        "  <freq in MHz>,<voltage swr>\n"
        "  e.g. 15.040000,1.01131434816733 is F=15.04 MHz,VSWR=1.01131434816733\n".format(sys.argv[0]),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("in_csv", metavar="<input CSV>", help="impedance sweep CSV")
    parser.add_argument("out_csv", metavar="<output CSV>", help="VSWR sweep CSV")
    parser.add_argument('--smooth', help='smooth data points', action='store_true')
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit(1)
    args = parser.parse_args()

    with open(args.in_csv, "r") as f_in:
        with open(args.out_csv, "w") as f_out:
            if args.smooth:
                write_csv(f_out, smooth_vswr(imp_to_vswr(read_csv(f_in))))
            else:
                write_csv(f_out, imp_to_vswr(read_csv(f_in)))

if __name__ == "__main__":
    main()
