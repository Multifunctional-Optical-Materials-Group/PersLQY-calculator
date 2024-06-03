# PersLQY-calculator
Persistent Luminescence Quantum Yield Calculator
## **Instalation**:
Install python3 and the folowing python packages: ```matplotlib```, ```numpy```, ```pandas``` and ```tkinter```.

## Suported Models:
- Constant refractive index model: $n(\lambda) = n0$
- Real Cauchy Model: $n(\lambda) = A_{1} + 10^{4}\frac{A_{2}}{\lambda^2} + 10^{9}\frac{A_{3}}{\lambda^4}$
- Imaginary Cauchy Model: $n(\lambda) = A_{1} + 10^{4}\frac{A_{2}}{\lambda^2} + 10^{9}\frac{A_{3}}{\lambda^4} + A_{4}\cdot i + 10^{4}\frac{A_{5}}{\lambda^2}\cdot i + 10^{9}\frac{A_{6}}{\lambda^4}\cdot i$
- Forouhi-Bloomer model: $n(\lambda) = n_0 + \sum_{j=1,2,3,4} \frac{B_j\cdot (E(\lambda)-E_j) + C_j}{(E(\lambda)-E_j)^2 + G_j^2} + \frac{f_j\cdot (E(\lambda)-E_g)^2\cdot \delta(E(\lambda)-E_g)}{(E(\lambda)-E_j)^2+G_j^2}\cdot i$, being $\delta$ the step function.
- Linear gradient model: $n_j(\lambda)= \frac{n_2-n_1}{N-1}\cdot j$, being $N$ the number of sublayers.

## **Usage**:
ReTraF function call takes the following form:
```
[models_out,N,D,Data_exp,Data_theor,xbest,foptions_out] = ReTraF(wl,theta,models,data_file,foptions)
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
  
