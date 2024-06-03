# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 10:58:48 2023

@author: manuelra
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pan
import tkinter as tk
import os
from tkinter.filedialog import askopenfilename

#%matplotlib qt
tk.Tk().withdraw() # part of the import if you are not using other tkinter functions

# Ask for files
fLumS = askopenfilename(title="Select Lum spectra file",initialdir="./",filetypes=[("Data File",".txt"),("All files","*")])
initdir = os.path.dirname(fLumS)

fPersS = askopenfilename(title="Select Pers spectra file",initialdir=initdir,filetypes=[("Data File",".txt"),("All files","*")])

fExcS = askopenfilename(title="Select Source spectra file",initialdir=initdir,filetypes=[("Data File",".txt"),("All files","*")])
fAbsS = askopenfilename(title="Select Source + Sample spectra file",initialdir=initdir,filetypes=[("Data File",".txt"),("All files","*")])

fAbs = askopenfilename(title="Select Absorption file",initialdir=initdir,filetypes=[("Data File",".txt"),("All files","*")])
fEmi = askopenfilename(title="Select Emission file",initialdir=initdir,filetypes=[("Data File",".txt"),("All files","*")])

#%%
# Read files
LumS = pan.read_table(fLumS)
PersS = pan.read_table(fPersS)
ExcS = pan.read_table(fExcS)
AbsS = pan.read_table(fAbsS)

Abs = pan.read_table(fAbs)
Emi = pan.read_table(fEmi)

wl1 = Emi.wl0[0]-Emi.bth[0]/2
wl2 = Emi.wl0[0]+Emi.bth[0]/2
t0 = Emi.t0[0]
t1 = Emi.t1[0]

OD_emi_present = False
if Emi.OD[0] !=0 :
    fOD_emi = initdir+'/'+Emi.OD[0]
    OD_emi = pan.read_table(fOD_emi)
    OD_emi_wl = OD_emi.wl
    OD_emi_T = 10**(-OD_emi.OD)
    OD_emi_present = True

wl1_exc = Abs.wl0[0]-Abs.bth[0]/2
wl2_exc = Abs.wl0[0]+Abs.bth[0]/2

OD_abs_present = False
if Abs.OD[0] !=0 :
    fOD_abs = initdir+'/'+Abs.OD[0]
    OD_abs = pan.read_table(fOD_abs)
    OD_abs_wl = OD_abs.wl
    OD_abs_T = 10**(-OD_abs.OD)
    OD_abs_present = True

# Absoption reference filename is contained in each absorption file
fAbs_ref = initdir+'/'+Abs.ref_file[0]
Abs_ref = pan.read_table(fAbs_ref)
Abs_ref_t0 = Abs_ref.t0[0]
Abs_ref_t1 = Abs_ref.t1[0]
Abs_t0 = Abs.t0[0]
Abs_t1 = Abs.t1[0]

#%% Correct Lum+Pers Time-spectra
i_Lum_wl1 = (np.abs(LumS.wl - wl1)).argmin()
i_Lum_wl2 = (np.abs(LumS.wl - wl2)).argmin()
FLum = np.abs(np.trapz(x=LumS.wl,y=LumS.counts)/np.trapz(x=LumS.wl[i_Lum_wl1:i_Lum_wl2+1],y=LumS.counts[i_Lum_wl1:i_Lum_wl2+1]))

i_Pers_wl1 = (np.abs(PersS.wl - wl1)).argmin()
i_Pers_wl2 = (np.abs(PersS.wl - wl2)).argmin()
FPers = np.abs(np.trapz(x=PersS.wl,y=PersS.counts)/np.trapz(x=PersS.wl[i_Pers_wl1:i_Pers_wl2+1],y=PersS.counts[i_Pers_wl1:i_Pers_wl2+1]))

# Filter correction
if OD_emi_present == True :
    i_OD_emi_wl1 = (np.abs(OD_emi.wl - wl1)).argmin()
    i_OD_emi_wl2 = (np.abs(OD_emi.wl - wl2)).argmin()
    iEmi = np.interp(x = OD_emi.wl[i_OD_emi_wl1:i_OD_emi_wl2+1], xp = LumS.wl, fp = LumS.counts)
    ODc_emi = np.trapz(x=OD_emi.wl[i_OD_emi_wl1:i_OD_emi_wl2+1],y= iEmi) / np.trapz(x=OD_emi.wl[i_OD_emi_wl1:i_OD_emi_wl2+1],y=OD_emi_T[i_OD_emi_wl1:i_OD_emi_wl2+1] * iEmi)
else :
    ODc_emi = 1

i_t0 = (np.abs(Emi.t - t0)).argmin()
i_t1 = (np.abs(Emi.t - t1)).argmin()
# Lum_Pers_c = np.zeros((len(Emi.counts),))
Lum_Pers_c = Emi.counts-np.mean(Emi.counts[-100:]) # substract background
Lum_Pers_c[i_t0:i_t1+1] = Lum_Pers_c[i_t0:i_t1+1]*FLum*ODc_emi
Lum_Pers_c[i_t1+1:] = Lum_Pers_c[i_t1+1:]*FPers*ODc_emi ###

#%% Correct absorption
i_Exc_wl1 = (np.abs(ExcS.wl - wl1_exc)).argmin()
i_Exc_wl2 = (np.abs(ExcS.wl - wl2_exc)).argmin()
FExc = np.abs(np.trapz(x=ExcS.wl,y=ExcS.counts)/np.trapz(x=ExcS.wl[i_Exc_wl1:i_Exc_wl2+1],y=ExcS.counts[i_Exc_wl1:i_Exc_wl2+1]))

i_Abs_wl1 = (np.abs(AbsS.wl - wl1_exc)).argmin()
i_Abs_wl2 = (np.abs(AbsS.wl - wl2_exc)).argmin()
FAbs = np.abs(np.trapz(x=AbsS.wl,y=AbsS.counts)/np.trapz(x=AbsS.wl[i_Abs_wl1:i_Abs_wl2+1],y=AbsS.counts[i_Abs_wl1:i_Abs_wl2+1]))

# Filter correction
if OD_abs_present == True :
    i_OD_abs_wl1 = (np.abs(OD_abs.wl - wl1_exc)).argmin()
    i_OD_abs_wl2 = (np.abs(OD_abs.wl - wl2_exc)).argmin()
    iExc = np.interp(x = OD_abs.wl[i_OD_abs_wl1:i_OD_abs_wl2+1], xp = ExcS.wl, fp = ExcS.counts)
    ODc_abs = np.trapz(x=OD_abs.wl[i_OD_abs_wl1:i_OD_abs_wl2+1],y= iExc) / np.trapz(x=OD_abs.wl[i_OD_abs_wl1:i_OD_abs_wl2+1],y=OD_abs_T[i_OD_abs_wl1:i_OD_abs_wl2+1] * iExc)
else :
    ODc_abs = 1


#%% Calulate absorption

i_t0A_ref = (np.abs(Abs_ref.t - Abs_ref_t0)).argmin()
i_t1A_ref = (np.abs(Abs_ref.t - Abs_ref_t1)).argmin()
int_Abs1 = FExc*np.trapz(x=Abs_ref.t[i_t0A_ref:i_t1A_ref+1],y=Abs_ref.counts[i_t0A_ref:i_t1A_ref+1])*ODc_abs # Abs ref integration

i_t0A = (np.abs(Abs.t - Abs_t0)).argmin()
i_t1A = (np.abs(Abs.t - Abs_t1)).argmin()
int_Abs2 = FAbs*np.trapz(x=Abs.t[i_t0A:i_t1A+1],y=Abs.counts[i_t0A:i_t1A+1])*ODc_abs # Abs integration

if (t1!=Abs_t1)|(t1!=Abs_ref_t1) :
    int_Abs = int_Abs1*(t1-t0)/(Abs_ref_t1-Abs_ref_t0) - int_Abs2*(t1-t0)/(Abs_t1-Abs_t0)
else :
    int_Abs = int_Abs1 - int_Abs2
    
    
#%% Calculate PersQY
int_total = np.trapz(x=Emi.t[i_t0:],y=Lum_Pers_c[i_t0:])
int_Pers = np.trapz(x=Emi.t[i_t1+1:],y=Lum_Pers_c[i_t1+1:])

QY = int_total/int_Abs*100
PersQY = int_Pers/int_Abs*100

#%%

plt.figure(figsize=(18,18))
plt.subplot(221)
plt.plot(LumS.wl,LumS.counts,linewidth=5)
plt.plot(PersS.wl,PersS.counts,'--',linewidth=5)
plt.xlabel("Wavelength (nm)")
plt.title("Lum. & PersL spectra")

plt.subplot(222)
plt.plot(ExcS.wl,ExcS.counts,linewidth=5)
plt.plot(AbsS.wl,AbsS.counts,'--',linewidth=5)
plt.xlabel("Wavelength (nm)")
plt.title("Absorption spectra")

plt.subplot(223)
plt.plot(Abs_ref.t,Abs_ref.counts,linewidth=5)
plt.plot(Abs.t,Abs.counts,'--',linewidth=5)
plt.xlabel("Time (s)")
plt.title("Absorption")

plt.subplot(224)
plt.scatter(Emi.t,Emi.counts)
#plt.scatter(Emi.t,Emi.counts-np.mean(Emi.counts[-100:-1]))
#plt.scatter(Emi.t,Lum_Pers_c)
plt.xlabel("Time (s)")
plt.title("Emission")
plt.yscale('log')

plt.savefig("measurement.png")
# plt.figure(5)
# plt.plot(Emi.t[i_t1:-2],sci.integrate.cumtrapz(x=Emi.t[i_t1:-1],y=Lum_Pers_c[i_t1:-1]))

#%%

root = tk.Tk()
root.title("Results")
root.geometry("400x300")
# tk.Button(root, text="Enviar", width=75).pack()
tk.Label(root, text=f"\n QY = {QY : .2f}%  \n\n\n PersQY = {PersQY : .2f}% \n", font=("Arial", 25)).pack()
tk.Button(root, text='OK', width=100, height=50, anchor="c",borderwidth=5, command=root.destroy).pack()
tk.mainloop()
# tk.messagebox.showinfo(title="Result", message=f"QY = {QY : .2f}% and PersQY = {PersQY : .2f}%" , )
