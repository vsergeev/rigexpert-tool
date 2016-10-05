#!/usr/bin/env python

# rigexpert-tool
# https://github.com/vsergeev/rigexpert-tool
#
# Copyright (c) 2016 Ivan (Vanya) A. Sergeev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import argparse
import math
import sys

__version__ = "1.0.0"

################################################################################
# Command registration infrastructure
################################################################################

Commands = []

def register_command(name, help, run_func, setup_func):
    Commands.append({'name': name, 'help': help, 'run_func': run_func, 'setup_func': setup_func})

################################################################################
# dump command
################################################################################

def transact(ser, cmd):
    ser.write(cmd + b"\n")

    while True:
        data = ser.readline().strip()

        if data == b"OK":
            break
        elif data == b"ERROR":
            raise IOError("Error: Unsupported command.")
        elif data == b"":
            continue

        yield data

def transact_cmd(ser, cmd):
    list(transact(ser, cmd))

def dump(args):
    # Import dependencies
    try:
        import serial
    except ImportError:
        sys.stderr.write("Error: dump command requires pyserial.\n")
        sys.exit(1)

    # Check start and stop frequency
    if args.stop_frequency < args.start_frequency:
        sys.stderr.write("Error: stop frequency less than start frequency.\n")
        sys.exit(1)

    # Open serial port
    ser = serial.Serial(args.serial_path, 38400)

    # Read analyzer version
    analyzer_version = list(transact(ser, b"VER"))[0].decode()
    sys.stderr.write("RigExpert Analyzer version: " + analyzer_version + "\n\n")

    # Enable RF
    transact_cmd(ser, b"ON")
    # Set center frequency
    transact_cmd(ser, "FQ{}".format(int((args.start_frequency + args.stop_frequency)/2)).encode())
    # Set sweep range
    transact_cmd(ser, "SW{}".format(int(args.stop_frequency - args.start_frequency)).encode())

    # Perform sweep
    with open(args.csv_path, "w") as f_csv:
        count = 0
        for line in transact(ser, "FRX{}".format(args.num_points-1).encode()):
            f_csv.write(line.decode() + "\n")
            count += 1

            # Print progress bar
            progress = float(count)/args.num_points
            sys.stderr.write("\r[" + "="*int(progress*76) + "-"*(76-int(progress*76)) + "] {}% {}/{}".format(int(progress*100), count, args.num_points))
    sys.stderr.write("\n")

    # Disable RF
    transact_cmd(ser, b"OFF")

    # Close serial port
    ser.close()

def dump_setup_args(parser):
    parser.description = "Dump impedance sweep CSV."
    parser.epilog = "Example, sweep 0.0 - 30.0 MHz with 500 points:\n" \
                    "  %(prog)s /dev/ttyUSB0 0e6 30e6 500 sweep.csv\n" \
                    "\n" \
                    "Example, sweep 7.000 - 7.300 MHz with 500 points:\n" \
                    "  %(prog)s /dev/ttyUSB0 7.000e6 7.300e6 500 sweep.csv\n" \
                    "\n" \
                    "Impedance CSV Format:\n" \
                    "  <freq in MHz>,<resistance in ohms>,<reactance in ohms>\n" \
                    "  15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms\n"
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.add_argument("serial_path", metavar="<serial port>", type=str, help="path to serial port, e.g. /dev/ttyUSB0")
    parser.add_argument("start_frequency", metavar="<start frequency>", type=float, help="start frequency")
    parser.add_argument("stop_frequency", metavar="<stop frequency>", type=float, help="stop frequency")
    parser.add_argument("num_points", metavar="<number of points>", type=int, help="number of points")
    parser.add_argument("csv_path", metavar="<output CSV>", type=str, help="output sweep CSV")

register_command("dump", "Dump impedance sweep CSV", dump, dump_setup_args)

################################################################################
# plot command
################################################################################

def imp_to_vswr(r, x):
    gamma = math.sqrt((r - 50)**2 + x**2)/math.sqrt((r + 50)**2 + x**2)

    try:
        swr = (1 + gamma)/(1 - gamma)
    except ZeroDivisionError:
        swr = float("inf")

    return swr

def plot(args):
    # Import dependencies
    try:
        import matplotlib.pyplot as plt
        import scipy.signal
    except ImportError:
        sys.stderr.write("Error: plot command requires matplotlib and scipy.\n")
        sys.exit(1)

    freqs = []
    vswrs = []

    # Read CSV file
    with open(args.csv, "r") as f:
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
    b, a = scipy.signal.firwin(min(64, int(len(vswrs)/3.0)-1), 0.06), [1]
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

    if args.annotate:
        # Find minima in smoothed VSWRs curve
        arg_minima = scipy.signal.argrelextrema(filt_vswrs, lambda a,b: a < b)[0]
        # Filter minima with SWR less than 3
        arg_minima = [e for e in arg_minima if vswrs[e] < 3]
        # Annotate points if there's 15 or less
        if len(arg_minima) <= 15:
            for i in arg_minima:
                plt.annotate('{:.2f} MHz\n{:.2f} VSWR'.format(freqs[i], vswrs[i]), xy=(freqs[i], vswrs[i]))

    plt.show()

def plot_setup_args(parser):
    parser.description = "Plot impedance or VSWR sweep CSV."
    parser.epilog = "Example:\n" \
                    "  %(prog)s sweep.imp.csv\n" \
                    "\n" \
                    "Example, with annotated VSWR:\n" \
                    "  %(prog)s --annotate sweep.imp.csv\n" \
                    "\n"
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.add_argument("csv", metavar="<sweep CSV>", help="impedance or VSWR sweep CSV")
    parser.add_argument('--annotate', help='annotate VSWR minima', action='store_true')

register_command("plot", "Plot impedance or VSWR sweep CSV", plot, plot_setup_args)

################################################################################
# imp2swr command
################################################################################

def stream_read_csv(f):
    for line in f:
        yield tuple(line.split(","))

def stream_write_csv(f, stream):
    for fields in stream:
        f.write(",".join(["{}".format(e) for e in fields]) + "\n")

def stream_imp_to_vswr(stream):
    for (freq, r, x) in stream:
        r, x = float(r), float(x)

        gamma = math.sqrt((r - 50)**2 + x**2)/math.sqrt((r + 50)**2 + x**2)

        try:
            vswr = (1 + gamma)/(1 - gamma)
        except ZeroDivisionError:
            vswr = float("inf")

        yield (freq, vswr)

def stream_smooth_vswr(stream, num_taps=64, alpha=0.06):
    freqs, vswrs = zip(*list(stream))

    # Filter VSWRs
    b, a = scipy.signal.firwin(min(num_taps, int(len(vswrs)/3.0)-1), alpha), [1]
    filt_vswrs = scipy.signal.filtfilt(b, a, vswrs)

    # Translate nans to infs
    filt_vswrs[scipy.isnan(filt_vswrs)] = float("inf")

    return zip(freqs, filt_vswrs)

def imp2swr(args):
    # Import dependencies
    try:
        global scipy
        import scipy.signal
    except ImportError:
        sys.stderr.write("Error: imp2swr command requires scipy.\n")
        sys.exit(1)

    with open(args.in_csv, "r") as f_in:
        with open(args.out_csv, "w") as f_out:
            if args.smooth:
                stream_write_csv(f_out, stream_smooth_vswr(stream_imp_to_vswr(stream_read_csv(f_in))))
            else:
                stream_write_csv(f_out, stream_imp_to_vswr(stream_read_csv(f_in)))

def imp2swr_setup_args(parser):
    parser.description = "Convert sweep CSV from impedance to VSWR."
    parser.epilog = "Example:\n" \
                    "  %(prog)s sweep.imp.csv sweep.swr.csv\n" \
                    "\n" \
                    "Example (smoothed):\n" \
                    "  %(prog)s --smooth sweep.imp.csv sweep.smooth.swr.csv\n" \
                    "\n" \
                    "Impedance CSV format:\n" \
                    "  <freq in MHz>,<resistance in ohms>,<reactance in ohms>\n" \
                    "  15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms\n" \
                    "\n" \
                    "VSWR CSV format:\n" \
                    "  <freq in MHz>,<voltage swr>\n" \
                    "  15.040000,1.01131434816733 is F=15.04 MHz,VSWR=1.01131434816733\n"
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.add_argument("in_csv", metavar="<input CSV>", help="impedance sweep CSV")
    parser.add_argument("out_csv", metavar="<output CSV>", help="VSWR sweep CSV")
    parser.add_argument('--smooth', help='smooth data points', action='store_true')

register_command("imp2swr", "Convert sweep CSV from impedance to VSWR", imp2swr, imp2swr_setup_args)

################################################################################
# program entry point
################################################################################

def main():
    parser = argparse.ArgumentParser(
        prog = 'rigexpert-tool',
        description = "Dump, plot, or convert RigExpert Antenna Analyzer impedance sweeps.\n\n" \
                      "https://github.com/vsergeev/rigexpert-tool",
        formatter_class = argparse.RawTextHelpFormatter
    )
    parser.add_argument('--version', action='version', version="%(prog)s v{}".format(__version__))

    # Add command parsers
    subparsers = parser.add_subparsers(help='command')
    for command in Commands:
        subparser = subparsers.add_parser(command['name'], help=command['help'])
        subparser.set_defaults(run_func=command['run_func'])
        command['setup_func'](subparser)

    # Print help and exit for no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit(0)

    args = parser.parse_args()

    args.run_func(args)

if __name__ == "__main__":
    main()
