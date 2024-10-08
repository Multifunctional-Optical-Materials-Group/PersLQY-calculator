# PersLQY-calculator
Persistent Luminescence Quantum Yield Calculator

## **Citation**:

This code is part of ***Quantification of Emission Efficiency in Persistent Luminescent Materials***, a work which is currently under revision process in [Advanced Optical Materials](https://onlinelibrary.wiley.com/journal/21951071).
If you use this software for publication purposes, please contact the authors. Check our [group website](https://mom.icms.us-csic.es/) for updates. 

## **Instalation & Usage**:
- Install ```python3```.
- Install the folowing python packages: ```matplotlib```, ```numpy```, ```pandas``` and ```tkinter```. This can be done in Windows by running the ```install.bat``` file.
- Run the ```PersLQY_calc.py``` in python. This can be done in Windows by running the ```PersLQY.bat``` file.

## **Data files**:
Before running the script, you will need the following files for each PersLQY measurement:

- **Photoluminescence spectra**: Text file containing two columns. First column must correspond to wavelength in nanometers, and second column to intensity. Headers should be included as in the following example:
  ```
  wl	counts
  420	0.00899413512876429
  420.5	0.00987102886128422
  421	0.0096912224891284
  421.5	0.0102467026352578
  422	0.0108732897365367
  ...................
  ```
- **Persistent luminescence spectra**: Text file containing two columns. First column must correspond to wavelength in nanometers, and second column to intensity.
  ```
  wl	counts
  420	0.003013006393295
  440	0.010150615158934
  450	0.0221624961338828
  460	0.0573174014402506
  470	0.140815487509773
  ...................
  ```
- **Excitation source spectra**: Text file containing two columns. First column must correspond to wavelength in nanometers, and second column to intensity.
  ```
  wl	counts
  390	1157.52478
  391	10705.6113
  392	19559.9336
  393	43986.3203
  394	93591.3359
  ...................
  ```
- **Excitation source + Sample spectra**: Text file containing two columns. First column must correspond to wavelength in nanometers, and second column to intensity. This corresponds to the excitation intensity which not absorbed by the sample.
  ```
  wl	counts
  390	1159.19031
  391	5666.96094
  392	10775.1074
  393	22261.3691
  394	46993.4414
  ...................
  ```

- **Reference for the time-dependent excitation**: Text file containing four columns. First column must correspond to time in seconds, second column to intensity, third column to $t_0$ (time in seconds at which excitation starts) and fourth column to $t_1$ (time in seconds at which excitation stops). This is used as a reference for calculating the number of photon absorbed during the PersLQY measurement.
  ```
  t	counts  t0  t1
  0	5.66825056	30	330
  0.6	5.66825056
  1.2	11.3365011
  1.8	11.3365011
  2.4	5.66825056
  ...................
  ```

- **Neutral density filter measurement**: Text file containing two columns. First column must correspond to wavelength in nanometers, and second column to optical density. This file is used to correct measurements in which a filter is used.
  ```
  wl	OD
  250	0.954242499
  250.5	0.999999994
  251	0.367976785
  251.5	0.221848758
  252	0.812913357
  ...................
  ```

- **Time-dependent absorption**: Text file containing four eight columns. This correspond to the time-dependent measurement of the excitation intensity which not absorbed by the sample, which is used to calculate the number of photon absorbed during the PersLQY measurement.
    - Column 1: Time in seconds
    - Column 2: Measured intensity
    - Column 3: File name of the reference for the time-dependent excitation file.
    - Column 4: Measured wavelength in nanometers.
    - Column 5: Bandwidth of the measurement in nanometers.
    - Column 6: $t_0$ in seconds
    - Column 7: $t_1$ in seconds
    - Column 8: File name of the neutral density filter file (```0``` if not used).

      
  ```
  t	counts	ref_file	wl0	bth	t0	t1	OD
  0	5.66825056	ref_400_400.txt	400	13	30	330	0
  0.6	1.88941681
  1.2	9.44708443
  1.8	11.3365011
  2.4	5.66825056
  ...................
  ```

- **Time-dependent emission**: Text file containing four seven columns. This correspond to the time-dependent measurement of the emission intensity, which is used to calculate the number of photon emitted during the PersLQY measurement.
    - Column 1: Time in seconds
    - Column 2: Measured intensity
    - Column 3: Measured wavelength in nanometers.
    - Column 4: Bandwidth of the measurement in nanometers.
    - Column 5: $t_0$ in seconds
    - Column 6: $t_1$ in seconds
    - Column 7: File name of the neutral density filter file (```0``` if not used).

      
  ```
  t	counts	wl0	bth	t0	t1	OD
  0	15.9283524	524	13	30	31.8	0
  0.6	17.3763847
  1.2	17.3763847
  1.8	10.1362247
  2.4	13.0322886
  ...................
  ```
  
## **Example**:
In the folder ```examples``` there are the following files:
- ```LumS.txt```: Photoluminescence spectra.
- ```PersS.txt```: Persistent luminescence spectra.
- ```source_e400.txt```: Excitation source reference spectra.
- ```source_SAO_e400.txt```: Excitation source + sample spectra.
- ```ref_400_400.txt```: Reference for the time-dependent excitation.
- ```OD1.txt```: Optical density of a filter.
- ```sample_400_400.txt```: Time-dependent  excitation source + sample intensity.
- ```sample_400_524.txt```: Time-dependent  emission intensity.

After running ```PersLQY.bat``` file, the folowing result should appear:
<p align="center">
  <img height="300" src=examples/result.png>
</p>

Also, an image named ```measurement.png``` should appear in the directory of your measurements:
<p align="center">
  <img height="500" src=examples/measurement.png>
</p>
