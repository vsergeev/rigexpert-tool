# rigexpert-tool [![GitHub release](https://img.shields.io/github/release/vsergeev/rigexpert-tool.svg?maxAge=7200)](https://github.com/vsergeev/rigexpert-tool) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/vsergeev/rigexpert-tool/blob/master/LICENSE)

`rigexpert-tool` is a CLI tool to dump, plot, and convert impedance sweeps from
a [RigExpert](http://www.rigexpert.com/) antenna analyzer.

The sweeps are stored in CSV.

## Installation

With pip:

```
pip install rigexpert-tool
```

With direct file:

```
wget https://github.com/vsergeev/rigexpert-tool/raw/master/rigexpert_tool.py -O rigexpert-tool
chmod +x rigexpert-tool
```

## Usage

```
$ rigexpert-tool
usage: rigexpert-tool [-h] [--version] {dump,plot,imp2swr} ...

Dump, plot, or convert RigExpert Antenna Analyzer impedance sweeps.

https://github.com/vsergeev/rigexpert-tool

positional arguments:
  {dump,plot,imp2swr}  command
    dump               Dump impedance sweep CSV
    plot               Plot impedance or VSWR sweep CSV
    imp2swr            Convert sweep CSV from impedance to VSWR

optional arguments:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
$
```

### Dump Sweep

```
$ rigexpert-tool dump -h
usage: rigexpert-tool dump [-h]
                           <serial port> <start frequency> <stop frequency>
                           <number of points> <output CSV>

Dump impedance sweep CSV.

positional arguments:
  <serial port>       path to serial port, e.g. /dev/ttyUSB0
  <start frequency>   start frequency
  <stop frequency>    stop frequency
  <number of points>  number of points
  <output CSV>        output sweep CSV

optional arguments:
  -h, --help          show this help message and exit

Example, sweep 0.0 - 30.0 MHz with 500 points:
  rigexpert-tool dump /dev/ttyUSB0 0e6 30e6 500 sweep.csv

Example, sweep 7.000 - 7.300 MHz with 500 points:
  rigexpert-tool dump /dev/ttyUSB0 7.000e6 7.300e6 500 sweep.csv

Impedance CSV Format:
  <freq in MHz>,<resistance in ohms>,<reactance in ohms>
  15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms
$
```

Sweep 0.0 to 30 MHz with 3000 points:

```
$ rigexpert-tool dump /dev/ttyUSB0 0e6 30e6 3000 sweep.csv
RigExpert Analyzer version: AA-30 111

[===============================---------------------------------------------] 41% 1243/3000
...
$ cat sweep.csv
0.000000,57.35,-3.34
0.010003,50.85,-1.33
0.020006,50.43,-0.75
0.030010,50.36,-0.03
0.040014,49.95,-0.12
0.050017,50.10,-0.06
0.060020,49.90,-0.41
0.070024,49.52,-0.20
0.080027,50.32,-0.28
0.090030,50.22,0.39
...
$
```

### Plot Sweep

```
$ rigexpert-tool plot -h
usage: rigexpert-tool plot [-h] [--annotate] <sweep CSV>

Plot impedance or VSWR sweep CSV.

positional arguments:
  <sweep CSV>  impedance or VSWR sweep CSV

optional arguments:
  -h, --help   show this help message and exit
  --annotate   annotate VSWR minima

Example:
  rigexpert-tool plot sweep.imp.csv

Example, with annotated VSWR:
  rigexpert-tool plot --annotate sweep.imp.csv
$
```

Plot sweep with VSWR minima annotated:

```
$ rigexpert-tool plot --annotate sweep.csv
```

![](example-plot.png)


### Convert Sweep

```
$ rigexpert-tool imp2swr -h
usage: rigexpert-tool imp2swr [-h] [--smooth] <input CSV> <output CSV>

Convert sweep CSV from impedance to VSWR.

positional arguments:
  <input CSV>   impedance sweep CSV
  <output CSV>  VSWR sweep CSV

optional arguments:
  -h, --help    show this help message and exit
  --smooth      smooth data points

Example:
  rigexpert-tool imp2swr sweep.imp.csv sweep.swr.csv

Example (smoothed):
  rigexpert-tool imp2swr --smooth sweep.imp.csv sweep.smooth.swr.csv

Impedance CSV format:
  <freq in MHz>,<resistance in ohms>,<reactance in ohms>
  15.040000,50.56,0.08 is F=15.04 MHz,R=50.56 ohms,X=0.08 ohms

VSWR CSV format:
  <freq in MHz>,<voltage swr>
  15.040000,1.01131434816733 is F=15.04 MHz,VSWR=1.01131434816733
$
```

Convert sweep CSV from impedance to VSWR:

```
$ rigexpert-tool imp2swr sweep.imp.csv sweep.swr.csv
$ cat sweep.swr.csv
0.000000,1.162557236161653
0.010003,1.031797166033004
0.020006,1.017365430279286
0.030010,1.0072250465801453
0.040014,1.0026046865594953
0.050017,1.002332768022061
0.060020,1.0084845989693039
0.070024,1.0105050291804325
0.080027,1.008513039599767
0.090030,1.0089758215918863
...
$
```

## LICENSE

rigexpert-tool is MIT licensed. See the included [LICENSE](LICENSE) file.

