import sys
import argparse

import serial

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dump a RigExpert antenna analyzer impedance sweep in CSV to stdout.",
        epilog=
        "Example: Sweep 0.0 - 30.0 MHz with 500 points\n"
        "  {0} /dev/ttyUSB0 0e6 30e6 500 sweep.csv\n"
        "\n"
        "Example: Sweep 7.000 - 7.300 MHz with 500 points\n"
        "  {0} /dev/ttyUSB0 7.000e6 7.300e6 500 sweep.csv\n"
        "\n"
        "Impedance CSV Format:\n"
        "  <freq in MHz>,<resistance in ohms>,<reactance in ohms>\n"
        "  e.g. 15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms\n".format(sys.argv[0]),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("serial_path", metavar="<serial port>", type=str)
    parser.add_argument("start_frequency", metavar="<start frequency>", type=float)
    parser.add_argument("stop_frequency", metavar="<stop frequency>", type=float)
    parser.add_argument("num_points", metavar="<number of points>", type=int)
    parser.add_argument("csv_path", metavar="<output CSV>", type=str)
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit(1)
    args = parser.parse_args()

    # Check start and stop frequency
    if args.stop_frequency < args.start_frequency:
        sys.stderr.write("Error: stop frequency less than start frequency.\n")
        sys.exit(1)

    # Open serial port
    ser = serial.Serial(args.serial_path, 38400)

    # Read analyzer version
    analyzer_version = list(transact(ser, b"VER"))[0].decode()
    sys.stderr.write("Analyzer version: " + analyzer_version + "\n")

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
