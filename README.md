# PersLQY-calculator
Persistent Luminescence Quantum Yield Calculator
## **Instalation**:
Install ```python3``` and the folowing python packages: ```matplotlib```, ```numpy```, ```pandas``` and ```tkinter```.

## **Usage**:
Before running the script, you will need the following files:

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

