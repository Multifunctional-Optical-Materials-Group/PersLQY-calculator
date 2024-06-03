# PersLQY-calculator
Persistent Luminescence Quantum Yield Calculator
## **Instalation**:
Install python3 and the folowing python packages: ```matplotlib```, ```numpy```, ```pandas``` and ```tkinter```.

## **Usage**:
Before running the script, you will need the following files:

- Photoluminescence spectra: Text file containing two columns. First column must correspond to wavelength in nanometers, and second column to intensity.
  ```
  wl	counts
420	0.00899413512876429
420.5	0.00987102886128422
421	0.0096912224891284
421.5	0.0102467026352578
422	0.0108732897365367
  ```

## Input arguments:

- ```data_file``` full path to .mat file containing Reflectance and Transmitance data to fit. Variables inside this file must be:
  - ```wl_exp``` wavelength in nm.
  - ```RSample_S``` reflectance (in %) for S polarization.
  - ```RSample_P``` reflectance (in %) for P polarization.
  - ```TSample_S``` transmittance (in %) for S polarization.
  - ```TSample_S``` transmittance (in %) for P polarization.

Reflectance and transmittance variables are matrices of dimension ```(m x n)``` where ```m``` is the number of measured wavelengths and ```n``` is the number of measurements for different incident angles.
- ```wl``` wavelength (in nm) vector
- ```theta``` incident angles struct:
   - ```theta.values``` vector containing the incident angles (in degrees) of the measurements to fit.
   - ```theta.index``` vector containing the indices of the corresponding angles.
 - ```models``` cell of structs containing the information of each layer.
 - ```foptions``` options struct.

### Models struct:
All the required information of each layer is stored inside a ```model``` struct. We make a distinction between known layers and unknown layers.
  - Known layers:
    - Forouhi-Bloomer model :
      - ```model.type = "Fh-N"```
      - ```model.Eg``` Bandgap in Ev
      - ```model.n0``` low frequency refractive index
      - ```model.fi``` fi parameter (length should be equal to the number of oscillators)
      - ```model.Ei``` Ei parameter (length should be equal to the number of oscillators)
      - ```model.Gi``` Gi parameter (length should be equal to the number of oscillators)
      - ```model.D``` layer thickness in nm
    - Real Cauchy model
      - ```model.type = "Ch-n"```
      - ```model.A``` vector with real Cauchy parameters ```[ A1 , A2 , A3 ]```
      - ```model.D``` layer thickness in nm
    - Complex Cauchy model
      - ```model.type = "Ch-nk"```
      - ```model.A``` vector with real Cauchy parameters ```[ A1 , A2 , A3 , A4 , A5 , A6 ]```
      - ```model.D``` layer thickness in nm
    - Linear refractive index gradient
      - ```model.type = "lin-grad"```
      - ```model.n1``` refractive index of the first layer
      - ```model.n2``` refractive index of the last layer
      - ```model.nlayers``` number of layers
      - ```model.D``` total tickness in nm
    - Constant refractive index
      - ```model.type = "cnst"```
      - ```model.n``` refractive index
      - ```model.D``` layer thickness in nm
    - Load from .mat file
      - ```model.type = "file"```
      - ```model.filename``` full path to the nk .mat file. The variables inside this file must be:
        - ```wl``` wavelenth in nm
        - ```n``` real part of the refractive index
        - ```k``` imaginary part of the refractive index
  - Unknown layers
      - Forouhi-Bloomer model :
        - ```model.type = "U-Fh-N"```
        - ```model.l_Eg``` lower bound for the bandgap in Ev
        - ```model.u_Eg``` upper bound for the bandgap in Ev
        - ```model.l_n0``` lower bound for the low frequency refractive index
        - ```model.u_n0``` upper bound for the low frequency refractive index
        - ```model.l_fi``` lower bound for the fi parameter (length should be equal to the number of oscillators)
        - ```model.u_fi``` upper bound for the fi parameter (length should be equal to the number of oscillators)
        - ```model.l_Ei``` lower bound for the Ei parameter (length should be equal to the number of oscillators)
        - ```model.u_Ei``` upper bound for the Ei parameter (length should be equal to the number of oscillators)
        - ```model.l_Gi``` lower bound for the Gi parameter (length should be equal to the number of oscillators)
        - ```model.u_Gi``` upper bound for the Gi parameter (length should be equal to the number of oscillators)
        - ```model.l_D```  lower bound for the layer thickness in nm
        - ```model.u_D```  upper bound for the layer thickness in nm
      - Real Cauchy model
        - ```model.type = "U-Ch-n"```
        - ```model.l_A```  lower bound for the vector with real Cauchy parameters ```[ A1 , A2 , A3 ]```
        - ```model.u_A```  upper bound for the vector with real Cauchy parameters ```[ A1 , A2 , A3 ]```
        - ```model.l_D```  lower bound for the layer thickness in nm
        - ```model.u_D```  layer thickness in nm
      - Complex Cauchy model
        - ```model.type = "U-Ch-nk"```
        - ```model.l_A```  lower bound for the vector with complex Cauchy parameters ```[ A1 , A2 , A3 , A4 , A5 , A6 ]```
        - ```model.u_A```  upper bound for the vector with complex Cauchy parameters ```[ A1 , A2 , A3 , A4 , A5 , A6 ]```
        - ```model.l_D```  lower bound for the layer thickness in nm
        - ```model.u_D```  upper bound for the layer thickness in nm
      - Linear refractive index gradient
        - ```model.type = "U-lin-grad"```
        - ```model.l_n1``` lower bound for the refractive index of the first layer
        - ```model.u_n1``` upper bound for the refractive index of the first layer
        - ```model.l_n2``` lower bound for the refractive index of the last layer
        - ```model.u_n2``` upper bound for the refractive index of the last layer
        - ```model.nlayers``` number of layers
        - ```model.l_D``` lower bound for the total tickness in nm
        - ```model.u_D``` upper bound for the total tickness in nm
      - Constant refractive index
        - ```model.type = "U-cnst"```
        - ```model.l_n``` lower bound for the refractive index
        - ```model.u_n``` upper bound for the refractive index
        - ```model.l_D```  lower bound for the layer thickness in nm
        - ```model.u_D```  upper bound for the layer thickness in nn
      - Load from .mat file
        - ```model.type = "U-file"```
        - ```model.l_D```  lower bound for the layer thickness in nm
        - ```model.u_D```  upper bound for the layer thickness in nn
        - ```model.filename``` full path to the nk .mat file. The variables inside this file must be:
        - ```wl``` wavelenth in nm
        - ```n``` real part of the refractive index
        - ```k``` imaginary part of the refractive index

Once all the models are properly defined, they must be packed in a cell array: ```models = {model_1 model_2 model_3 model_4}```.

### Options struct:
- ```foptions.method```
  - ```"fmincon"``` use Matlab ```fmincon``` minimization.
  - ```"genetic"``` use Matlab genetic algorithm minimization.


- ```foptions.itermax``` maximum number of iterations.
- ```foptions.poppize``` genetic algorithm population size.
- ```foptions.parallel``` use Matlab parallelization (true or false).
- ```foptions.lcoher``` coherence length (```1e4``` is recommended).
- ```foptions.scatt``` apply scattering correction (only for R&T of non-absorbing media).
  
