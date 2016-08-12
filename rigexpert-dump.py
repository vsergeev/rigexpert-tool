import sys
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
    if len(sys.argv) < 5:
        print("Dump a RigExpert antenna analyzer impedance sweep in CSV to stdout.")
        print()
        print("Usage: {} <serial port> <center frequency> <sweep range> <number of points>".format(sys.argv[0]))
        print()
        print("Example: Sweep 0.0 - 30.0 MHz with 5000 points")
        print("    python3 {} /dev/ttyUSB0 15e6 30e6 5000 > sweep.csv".format(sys.argv[0]))
        print()
        print("Example: Sweep 7.000 - 7.300 MHz with 300 points")
        print("    python3 {} /dev/ttyUSB0 7.150e6 0.300e6 300 > sweep.csv".format(sys.argv[0]))
        print()
        print("CSV Format:")
        print("    <freq in MHz>,<resistance in ohms>,<reactance in ohms>")
        print("    e.g. 15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms")
        sys.exit(0)

    path = sys.argv[1]
    frequency = int(float(sys.argv[2]))
    sweep_range = int(float(sys.argv[3]))
    num_points = int(float(sys.argv[4]))

    # Open serial port
    ser = serial.Serial(path, 38400)

    # Read analyzer version
    analyzer_version = list(transact(ser, b"VER"))[0].decode()
    sys.stderr.write("Analyzer version: " + analyzer_version + "\n")

    # Enable RF
    transact_cmd(ser, b"ON")
    # Set center frequency
    transact_cmd(ser, "FQ{}".format(frequency).encode())
    # Set sweep range
    transact_cmd(ser, "SW{}".format(sweep_range).encode())

    # Perform sweep
    count = 0
    for line in transact(ser, "FRX{}".format(num_points-1).encode()):
        print(line.decode())
        count += 1

        # Print progress bar
        progress = count/num_points
        sys.stderr.write("\r[" + "="*int(progress*76) + "-"*(76-int(progress*76)) + "] {}% {}/{}".format(int(progress*100), count, num_points))

    sys.stderr.write("\n")

    # Disable RF
    transact_cmd(ser, b"OFF")

    # Close serial port
    ser.close()
