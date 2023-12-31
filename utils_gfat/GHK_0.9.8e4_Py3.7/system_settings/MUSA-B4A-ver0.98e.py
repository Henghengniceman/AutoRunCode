# This Python script will be executed from within the main lidar_correction_ghk.py
# Probably it will be better in the future to let the main script rather read a conguration file,
# which might improve the portability of the code within an executable.
# Due to problems I had with some two letter variables, most variables are now with at least
# three letters mixed small and capital.

# Error calculation?
# False: only calculate the GHK-parameters. True: calculate also errors. Can take a long time.
Error_Calc = True

# Header for the identification of the lidar system
EID = "po"				# Earlinet station ID
LID = "MUSA B4A" 	# Additional lidar ID (short descriptive text)
print("    Lidar system :", EID, ", ", LID)

# +++ IL Laser beam polarisation and +-Uncertainty [Note: (Qin^2 + Vin^2) <= 1]
Qin, dQin, nQin = 0.9442, 0.0037,  1	# second Stokes vector parameter; default 1 => according to \Potenza\Aldos_correction.odt
Vin, dVin, nVin = 0.0, 0.0,  0	# fourth Stokes vector parameter; default 0  => corresponds to LDR 0.0005 with DOP 1
RotL, dRotL, nRotL 	= 93.0, 0.1, 1	# rotation of laser polarization in degrees; default 0

# +++ ME Emitter optics and +-Uncertainty;  default = no emitter optics
DiE, dDiE, nDiE 	= 0.0, 	0.1, 	0	#  Diattenuation; default 0
TiE 		        = 1.0		        # Unpolarized transmittance; default 1
RetE, dRetE, nRetE 	= 0., 	1., 	0	# Retardance in degrees; default 0
RotE, dRotE, nRotE 	= 0., 	0.5, 	0	# beta: Rotation of optical element in degrees; default 0

# +++ MO Receiver optics including telescope 
DiO,  dDiO, nDiO 	= -0.055, 0.003, 	1	# Diattenuation; default 0
TiO 				= 0.9 	# unpolarized transmission; default 1
RetO, dRetO, nRetO 	= 90., 	180., 	7 	# Retardance in degrees; default 0
RotO, dRotO, nRotO 	= 0., 	0.1, 	0	# gamma: Rotation of optical element in degrees; default 0
 
# +++++ PBS MT Transmitting path defined with TS, TP, and cleaning PolFilter extinction ratio ERaT, and +-Uncertainty
#   --- Polarizing beam splitter transmitting path
TP,   dTP, nTP	 	= 0.95,	0.01,   1	# p-transmission of the PBS 
TS,   dTS, nTS	 	= 0.001, 0.001,   1	# s-transmission of the PBS
RetT, dRetT, nRetT	= 0.00,	180., 	0 # Retardance in degrees
#   --- Pol.Filter behind transmitted path of PBS
ERaT, dERaT, nERaT	 = 1e-3,  5e-4,   1 # Extinction ratio
RotaT, dRotaT, nRotaT = 0.,   1.,   1 # Rotation of the Pol.-filter in degrees; usually 0° because TP >> TS, but for PollyXTs it can also be 90°
#   --                            
TiT = 0.5 * (TP + TS)    # do not change this
DiT = (TP-TS)/(TP+TS)    # do not change this
DaT = (1-ERaT)/(1+ERaT)    # do not change this
TaT = 0.5*(1+ERaT)    # do not change this

# +++++ PBS MR Reflecting path defined with RS, RP, and cleaning PolFilter extinction ratio ERaR  and +-Uncertainty
#   ---- for PBS without absorption the change of RS and RP must depend on the change of TP and TS. Hence the values and uncertainties are not independent.
RS_RP_depend_on_TS_TP = True
#   --- Polarizing beam splitter reflecting path
if(RS_RP_depend_on_TS_TP): 
    RP, dRP, nRP        = 1-TP,  0.00, 0    # do not change this
    RS, dRS, nRS        = 1-TS,  0.00, 0    # do not change this
else:
    RP, dRP, nRP        = 0.00,  0.00, 0    # change this if RS_RP_depend_on_TS_TP = False; reflectance of the PBS for parallel polarized light
    RS, dRS, nRS        = 0.36,  0.02, 1    # change this if RS_RP_depend_on_TS_TP = False; reflectance of the PBS for cross polarized light
RetR, dRetR, nRetR	    = 0.0,   180., 0    # Retardance in degrees
#   --- Pol.Filter behind reflected path of PBS
ERaR, dERaR, nERaR	    = 1e-3,  5e-4,   1 # Extinction ratio
RotaR, dRotaR, nRotaR   = 90.,   1.,   1  # Rotation of the Pol.-filter in degrees; usually 90° because RS >> RP, but for PollyXTs it can also be 0°
#   --
TiR = 0.5 * (RP + RS)    # do not change this
DiR = (RP-RS)/(RP+RS)    # do not change this
DaR = (1-ERaR)/(1+ERaR)    # do not change this
TaR = 0.5*(1+ERaR)    # do not change this

# NEW --- Additional ND filter transmission (attenuation) during the calibration
TCalT, dTCalT, nTCalT  = 1, 0.01, 0		# transmitting path, default 1, 0, 0
TCalR, dTCalR, nTCalR = 1, 0.0001, 0		# reflecting path, default 1, 0, 0

# +++ Orientation of the PBS with respect to the reference plane (see Improvements_of_lidar_correction_ghk_ver.0.9.8_190124.pdf)
#    Y = +1: polarisation in reference plane is finally transmitted, 
#    Y = -1: polarisation in reference plane is finally reflected.
Y = -1.

# +++ Calibrator 
# --- Calibrator Type used; defined by matrix values below
TypeC = 6	#Type of calibrator: 1 = mechanical rotator; 2 = hwp rotator (fixed retardation); 3 = linear polarizer; 4 = qwp; 5 = circular polarizer; 6 = real HWP calibration +-22.5°
# --- Calibrator Location
LocC = 4 #location of calibrator: 1 = behind laser; 2 = behind emitter; 3 = before receiver; 4 = before PBS
# --- MC Calibrator parameters
if TypeC == 1:  #mechanical rotator
	DiC, dDiC, nDiC 	= 0., 	0., 	0
	TiC = 1.
	RetC, dRetC, nRetC 	= 0., 	0., 	0
	RotC, dRotC, nRotC 	= 0., 	0.2, 	1	#constant calibrator offset epsilon
	# Rotation error without calibrator: if False, then epsilon = 0 for normal measurements	
	RotationErrorEpsilonForNormalMeasurements = True	# 	is in general True for TypeC == 1 calibrator
elif TypeC == 2:   # HWP rotator
	DiC, dDiC, nDiC 	= 0., 	0., 	0
	TiC = 1.
	RetC, dRetC, nRetC 	= 180., 0., 	0
	#NOTE: use here twice the HWP-rotation-angle
	RotC, dRotC, nRotC 	= 0.0, 	0.1, 	1	#constant calibrator offset epsilon
	RotationErrorEpsilonForNormalMeasurements = True	# 	is in general True for TypeC == 2 calibrator
elif TypeC == 3:   # linear polarizer calibrator. Diattenuation DiC = (1-ERC)/(1+ERC); ERC = extinction ratio of calibrator
	DiC, dDiC, nDiC 	= 0.9998, 0.00019, 2	# ideal 1.0
	TiC = 0.4	# ideal 0.5
	RetC, dRetC, nRetC 	= 0, 	180., 	0
	RotC, dRotC, nRotC 	= 0.0, 	0.1, 	0	#constant calibrator offset epsilon
	RotationErrorEpsilonForNormalMeasurements = False	# 	is in general False for TypeC == 3 calibrator
elif TypeC == 4:   # QWP calibrator
	DiC, dDiC, nDiC 	= 0.0, 	0., 	0	# ideal 1.0
	TiC = 1.0	# ideal 0.5
	RetC, dRetC, nRetC 	= 90., 	0., 	0
	RotC, dRotC, nRotC 	= 0.0, 	0.1, 	1	#constant calibrator offset epsilon
	RotationErrorEpsilonForNormalMeasurements = False	# 	is  False for TypeC == 4 calibrator
elif TypeC == 6:   # real half-wave plate calibration at +-22.5°  => rotated_diattenuator_X22x5deg.odt
	DiC, dDiC, nDiC 	= 0., 	0., 	0
	TiC = 1.
	RetC, dRetC, nRetC 	= 180., 0., 	0
    #Note: use real HWP angles here
	RotC, dRotC, nRotC 	= -46.785, 	0.115, 	1	#constant calibrator offset epsilon
	RotationErrorEpsilonForNormalMeasurements = True	# 	is in general True for TypeC == 6 calibrator
else:
	print ('calibrator not implemented yet')
	sys.exit()

# --- LDRCal assumed atmospheric linear depolarization ratio during the calibration measurements in calibration range with almost clean air (first guess)
# LDRCal,dLDRCal,nLDRCal= 0.009, 0.005, 0     # spans the interference filter influence 
LDRCal,dLDRCal,nLDRCal= 0.0040, 0.01, 0     # 

# ====================================================
# NOTE: there is no need to change anything below.
# ====================================================
# !!! don't change anything in this section !!!
bPlotEtax = False    # plot error histogramms for Etax
# NEW *** Only for signal noise errors *** 
nNCal = 0           # error nNCal, calibration signals: one-sigma (fixed) in nNCal steps to left and right
nNI   = 0           # error nNI, 0° signals: one-sigma (fixed) in nNI steps to left and right; NI signals are calculated from NCalT and NCalR in main programm, but noise is assumed to be independent.

#   --- number of photon counts in the signal summed up in the calibration range during the calibration measurements
NCalT = 40000		# default 1e6, assumed the same in +45° and -45° signals; counts with ND-filter TCalT 
NCalR = 40000		# default 1e6, assumed the same in +45° and -45° signals; counts with ND-filter TCalR 
NILfac = 1          # (relative duration (laser shots) of standard (0°) measurement to calibration measurements) * (range of std. meas. smoothing / calibration range); example: 100000#/5000# * 100/1000 = 2 
                    #  LDRmeas below will be used to calculate IR and IT of 0° signals.
# calculate signal counts only from parallel 0° signal assuming the same electronic amplification in both channels; overwrites above values
CalcFrom0deg = True
NI = 100000000 #number of photon counts in the parallel 0°-signal 40000
    
if(CalcFrom0deg):
    # either eFactT or eFacR is = 1 => rel. amplification
	eFacT = 1                     			# rel. amplification of transmitted channel, approximate values are sufficient; def. = 1
	eFacR = 1                    			# rel. amplification of reflected channel, approximate values are sufficient; def. = 1
	NILfac = 1           					# (relative duration (laser shots) of standard (0°) measurement to calibration measurements) * (range of std. meas. smoothing / calibration range); example: 100000#/5000# * 100/1000 = 2 

	NCalT = NI / NILfac * TCalT * eFacT		# photon counts in transmitted signal during calibration 
	NCalR = NI / NILfac * TCalR * eFacR	    # photon counts in reflected signal during calibration 
                        #  LDRmeas below will be used to calculate IR and IT of 0° signals.
# NEW *** End of signal noise error parameters ***  

# --- LDRtrue for simulation of measurement => LDRsim
LDRtrue = 0.004
LDRtrue2 = 0.004 # overwrite LDRrange[0]
# --- measured LDRm will be corrected with calculated parameters GHK
LDRmeas = 0.3

# --- this is just for correct transfer of the variables to the main file 
Qin0, dQin, nQin = Qin, dQin, nQin
Vin0, dVin, nVin = Vin, dVin, nVin
RotL0, dRotL, nRotL = RotL, dRotL, 	nRotL 
# Emitter
DiE0,  dDiE,  nDiE  = DiE,  dDiE, 	nDiE  
RetE0, dRetE, nRetE = RetE, dRetE, 	nRetE 
RotE0, dRotE, nRotE = RotE, dRotE, 	nRotE 
# Receiver
DiO0,  dDiO,  nDiO  = DiO,  dDiO, 	nDiO  
RetO0, dRetO, nRetO = RetO, dRetO, 	nRetO 
RotO0, dRotO, nRotO = RotO, dRotO, 	nRotO 
# Calibrator
DiC0,  dDiC,  nDiC  = DiC,  dDiC, 	nDiC  
RetC0, dRetC, nRetC = RetC, dRetC, 	nRetC 
RotC0, dRotC, nRotC = RotC, dRotC, 	nRotC 
# PBS
TP0,   dTP,   nTP   = TP,   dTP, 	nTP   
TS0,   dTS,   nTS   = TS,   dTS, 	nTS 
RetT0, dRetT, nRetT	= RetT, dRetT, nRetT

ERaT0, dERaT, nERaT	= ERaT, dERaT, nERaT
RotaT0,dRotaT,nRotaT= RotaT,dRotaT,nRotaT

RP0,   dRP,   nRP   = RP,   dRP,   nRP
RS0,   dRS,   nRS   = RS,   dRS,   nRS
RetR0, dRetR, nRetR	= RetR, dRetR, nRetR

ERaR0, dERaR, nERaR	= ERaR, dERaR, nERaR
RotaR0,dRotaR,nRotaR= RotaR,dRotaR,nRotaR

LDRCal0,dLDRCal,nLDRCal=LDRCal,dLDRCal,nLDRCal