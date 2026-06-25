# PersLQY Calculator

A desktop application for calculating the **persistent luminescence quantum yield (PersLQY)** and the **total luminescence quantum yield (TotalQY)** from spectroscopic and time-dependent measurements.

The calculation follows the method described in:

> V. Castaing, M. Romero, D. Rytz, G. Lozano, and H. Míguez,  
> *Quantification of Emission Efficiency in Persistent Luminescent Materials*,  
> **Advanced Optical Materials** 12 (2024), 2401638.  
> https://doi.org/10.1002/adom.202401638

## Features

- Graphical desktop interface
- Selection of all required measurement files
- Configurable background interval
- Default background calculated from the first 30 seconds of the emission measurement
- Calculation of TotalQY and PersLQY
- Four embedded measurement plots
- Zoom and pan controls for the plots
- Export of plots as PNG, PDF, or SVG

## Installation

There are two ways to run PersLQY Calculator.

### Option 1: Windows application

This is the recommended option for users who do not normally work with Python.

When a Windows release is available:

1. Open the repository's **Releases** page on GitHub.
2. Download the Windows package for the latest release.
3. Extract the downloaded ZIP file.
4. Open the extracted folder.
5. Double-click `PersLQY.exe`.

Python is not required when using the Windows application.

> The Windows executable is distributed through GitHub Releases and is not stored directly in the source-code folders of the repository.

### Option 2: Run from Python

This option is intended for users who want to inspect, modify, or contribute to the source code.

#### Requirements

- Python 3
- NumPy
- pandas
- Matplotlib
- Tkinter

Tkinter is included with most standard Python installations on Windows.

#### Install the Python dependencies

Open a terminal in the repository folder and run:

```bash
python -m pip install numpy pandas matplotlib
```

#### Run from Visual Studio Code

1. Open the repository folder in Visual Studio Code.
2. Open:

   ```text
   src/perslqy/app.py
   ```

3. Make sure Visual Studio Code is using the desired Python interpreter.
4. Click **Run Python File** in the upper-right corner.

#### Run from a terminal

Open a terminal in the repository folder and run:

```bash
python src/perslqy/app.py
```

The PersLQY Calculator window should open.

## Using the interface

1. Select the six required measurement files using the **Browse...** buttons.

   You can also use **Select all files in sequence** to select them one after another.

2. Check the background interval.

   By default, the application uses the first 30 seconds of the emission measurement. The start and stop times can be changed manually.

3. Click **Calculate**.

4. The application displays:

   - TotalQY
   - PersLQY
   - Luminescence and persistent luminescence spectra
   - Source and source + sample spectra
   - Reference and sample absorption kinetics
   - Raw and background-corrected emission kinetics

5. To export the plots, click **Save plots...** and choose PNG, PDF, or SVG.

## Required data files

The application requires six files for each PersLQY measurement.

Additional files, such as the absorption reference and neutral-density-filter spectrum, are loaded automatically from the filenames stored in the selected measurement files. These additional files should therefore be located in the same directory as the selected measurement files.

All files are tab-separated text files with column headers.

### 1. Luminescence spectrum

This file contains the spectrum measured during illumination.

Required columns:

| Column | Meaning |
|---|---|
| `wl` | Wavelength in nanometres |
| `counts` | Measured intensity |

Example:

```text
wl	counts
420	0.00899413512876429
420.5	0.00987102886128422
421	0.0096912224891284
421.5	0.0102467026352578
422	0.0108732897365367
```

### 2. Persistent luminescence spectrum

This file contains the spectrum measured after the excitation has stopped.

Required columns:

| Column | Meaning |
|---|---|
| `wl` | Wavelength in nanometres |
| `counts` | Measured intensity |

Example:

```text
wl	counts
420	0.003013006393295
440	0.010150615158934
450	0.0221624961338828
460	0.0573174014402506
470	0.140815487509773
```

### 3. Source spectrum

This file contains the excitation-source spectrum measured without the sample.

Required columns:

| Column | Meaning |
|---|---|
| `wl` | Wavelength in nanometres |
| `counts` | Measured intensity |

Example:

```text
wl	counts
390	1157.52478
391	10705.6113
392	19559.9336
393	43986.3203
394	93591.3359
```

### 4. Source + sample spectrum

This file contains the excitation spectrum measured in the presence of the sample. It represents the portion of the excitation signal that is not absorbed by the sample.

Required columns:

| Column | Meaning |
|---|---|
| `wl` | Wavelength in nanometres |
| `counts` | Measured intensity |

Example:

```text
wl	counts
390	1159.19031
391	5666.96094
392	10775.1074
393	22261.3691
394	46993.4414
```

### 5. Time-dependent absorption measurement

This file contains the excitation intensity measured in the presence of the sample as a function of time.

Required columns:

| Column | Meaning |
|---|---|
| `t` | Time in seconds |
| `counts` | Measured intensity |
| `ref_file` | Filename of the time-dependent excitation reference |
| `wl0` | Detection wavelength in nanometres |
| `bth` | Detection bandwidth in nanometres |
| `t0` | Start of excitation in seconds |
| `t1` | End of excitation in seconds |
| `OD` | Filename of the neutral-density-filter spectrum, or `0` when no filter was used |

Example:

```text
t	counts	ref_file	wl0	bth	t0	t1	OD
0	5.66825056	ref_400_400.txt	400	13	30	330	0
0.6	1.88941681
1.2	9.44708443
1.8	11.3365011
2.4	5.66825056
```

Only the first row needs to contain the metadata values.

### 6. Time-dependent emission measurement

This file contains the emission intensity as a function of time.

Required columns:

| Column | Meaning |
|---|---|
| `t` | Time in seconds |
| `counts` | Measured intensity |
| `wl0` | Detection wavelength in nanometres |
| `bth` | Detection bandwidth in nanometres |
| `t0` | Start of excitation in seconds |
| `t1` | End of excitation in seconds |
| `OD` | Filename of the neutral-density-filter spectrum, or `0` when no filter was used |

Example:

```text
t	counts	wl0	bth	t0	t1	OD
0	15.9283524	524	13	30	31.8	0
0.6	17.3763847
1.2	17.3763847
1.8	10.1362247
2.4	13.0322886
```

Only the first row needs to contain the metadata values.

## Additional files

### Time-dependent excitation reference

The filename of this file is read from the `ref_file` column in the time-dependent absorption measurement.

Required columns:

| Column | Meaning |
|---|---|
| `t` | Time in seconds |
| `counts` | Measured intensity |
| `t0` | Start of excitation in seconds |
| `t1` | End of excitation in seconds |

Example:

```text
t	counts	t0	t1
0	5.66825056	30	330
0.6	5.66825056
1.2	11.3365011
1.8	11.3365011
2.4	5.66825056
```

### Neutral-density-filter spectrum

This file is optional. Its filename is read from the `OD` column of the absorption or emission measurement.

Use `0` in the `OD` column when no neutral-density filter was used.

Required columns:

| Column | Meaning |
|---|---|
| `wl` | Wavelength in nanometres |
| `OD` | Optical density |

Example:

```text
wl	OD
250	0.954242499
250.5	0.999999994
251	0.367976785
251.5	0.221848758
252	0.812913357
```

## Example dataset

An example measurement is available in the [`examples`](examples) directory.

The example currently contains:

| File | Measurement |
|---|---|
| `LumS.txt` | Luminescence spectrum |
| `PersS.txt` | Persistent luminescence spectrum |
| `source_e400.txt` | Source spectrum |
| `source_SAO_e400.txt` | Source + sample spectrum |
| `ref_400_400.txt` | Time-dependent excitation reference |
| `OD1.txt` | Neutral-density-filter spectrum |
| `sample_400_400_300s.txt` | Time-dependent absorption measurement |
| `sample_400_524_300s.txt` | Time-dependent emission measurement |

To test the program:

1. Start the application.
2. Select the files from the `examples` directory.
3. Keep the default background interval unless a different interval is required.
4. Click **Calculate**.
5. Review the calculated values and the four plots.
6. Use **Save plots...** to export the figure.

## Citation

When using PersLQY Calculator in research, please cite:

```text
Castaing, V.; Romero, M.; Rytz, D.; Lozano, G.; Míguez, H.
Quantification of Emission Efficiency in Persistent Luminescent Materials.
Advanced Optical Materials 2024, 12, 2401638.
https://doi.org/10.1002/adom.202401638
```

No additional contact with the authors is required for publication use.

## Contact and updates

Project updates are available through the [Multifunctional Optical Materials Group website](https://mom.icms.us-csic.es/).
