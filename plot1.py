import ROOT
import plotfactory as pf
import numpy as np
import sys
from array import array
from pdb import set_trace


def makeCummulativePlots(files,trees):
    # c2200 = ROOT.TCanvas('c2200','c2200')
    # c2300 = ROOT.TCanvas('c2300','c2300')
    # c2400 = ROOT.TCanvas('c2400','c2400')
    # c2500 = ROOT.TCanvas('c2500','c2500')
    # c2600 = ROOT.TCanvas('c2600','c2600')
    # c2700 = ROOT.TCanvas('c2700','c2700')
    # c2800 = ROOT.TCanvas('c2800','c2800')
    # c2900 = ROOT.TCanvas('c2900','c2900')
    # c3000 = ROOT.TCanvas('c3000','c3000')
    # canvases = [c2200,c2300,c2400,c2500,c2600,c2700,c2800,c2900,c3000]

    c2900_DriftVelocity = ROOT.TCanvas('c2900_DriftVelocity','c2900_DriftVelocity')
    canvases = [c2900_DriftVelocity]

    for i in np.arange(len(files)):
        print (files[i], trees[i], canvases[i])
        canvases[i].cd()
        trees[i].Draw("chn{}_v:chn{}_t")
        canvases[i].Update()
        canvases[i].SaveAs(canvases[i].GetName()+'.png')

def sanityCheck(arr_time, arr_voltage):
    result = False
    if len(arr_time) != len(arr_voltage):
        print ('time and voltage arrays have unequal number of entries, aboarting...')
        result = False
    elif len(arr_time) == len(arr_voltage):
        result = True
    return result
    
def makeEventHistogram(hist,entry):
    hist.Reset()
    currentBin = 0
    time = 0 
    voltage = 0
    
    for i in np.arange(len(entry.chn1_t)):
        time = entry.chn1_t[i]
        currentBin = hist.FindBin(time)
        if (abs(entry.chn1_v[i]) > abs(hist.GetBinContent(currentBin))):
            hist.SetBinContent(currentBin,(-1)*entry.chn1_v[i])
    return hist

def subtractBackground(hist_SinglePulse,spectrum):
    hist_SinglePulse_Background = spectrum.Background(hist_SinglePulse,50,"")
    hist_SinglePulse.Add(hist_SinglePulse_Background,-1)
    return hist_SinglePulse

def findMainPeak(spectrum, numberPeaksFound):
    maxAmplitude   = 0
    maxSignalIndex = 0
    for i in np.arange(numberPeaksFound): 
        currentAmplitude = spectrum.GetPositionY()[i]
        if triggerTolerance(spectrum.GetPositionX()[i]) and (currentAmplitude > maxAmplitude) and (currentAmplitude) < 0.5: 
            maxAmplitude = currentAmplitude
            maxSignalIndex = i
    return maxAmplitude, spectrum.GetPositionX()[maxSignalIndex]

def triggerTolerance(peakTime):
    # minTime = 600
    minTime = 0
    maxTime = 3000
    if (peakTime > minTime) and (peakTime < maxTime):
        return True
    else: return False

def eventSelection(numberPeaksFound, mainPeak_Time, mainPeak_Amplitude, integral):
    goodEvent = False
    pass_numberPeaksFound = numberPeaksFound > 0
    pass_mainPeak_Time = triggerTolerance(mainPeak_Time)
    # pass_mainPeak_Time = (mainPeak_Time > 500) and (mainPeak_Time < 1500)
    # pass_mainPeak_Time = mainPeak_Time > 0
    # pass_mainPeak_Amplitude = (mainPeak_Amplitude > 0.) and (mainPeak_Amplitude < 0.1)
    pass_mainPeak_Amplitude = mainPeak_Amplitude < 0.5
    # pass_mainPeak_Amplitude = mainPeak_Amplitude < 0.07
    pass_integral = integral > 1.
    goodEvent = pass_numberPeaksFound and pass_mainPeak_Time and pass_mainPeak_Amplitude and pass_integral
    return goodEvent

def drawHist(hist):
    can_Pulse = ROOT.TCanvas('can_Pulse','can_Pulse')
    can_Pulse.cd()
    hist_SinglePulse.Draw()
    can_Pulse.Update()

def printEvent(i,numberPeaksFound,integral,mainPeak_Amplitude,mainPeak_Time,goodEvent):
    print ('event number: %d'%i)
    print ('\tpeaks:\t\t %d'%numberPeaksFound)
    print ('\tintegral:\t %.3f'%integral)
    print ('\tmaxamp:\t\t %.3f'%mainPeak_Amplitude)
    print ('\ttime:\t\t %.1f'%mainPeak_Time)
    print ('\tgoodEvent:\t %s'%goodEvent)

def analyseSingleWorkingPoint(histograms,tree):
    #reset histograms (empty all entries)
    for hist in histograms: hist.Reset() 

    hist_SinglePulse    = histograms[0]
    hist_NumberOfPeaks  = histograms[1]
    hist_Amplitude      = histograms[2]
    hist_Integral       = histograms[3]
    hist_Time           = histograms[4]

    # for i,entry in enumerate(trees[5]):
    for i,entry in enumerate(tree):
        # basic sanity check of the event
        resultSanityCheck = sanityCheck(entry.chn1_t,entry.chn1_v)
        if resultSanityCheck == False: set_trace()

        # generate pulse, find peak(s), subtract background, compute keyMetrics
        hist_SinglePulse                    = makeEventHistogram(hist_SinglePulse,entry)
        spectrum                            = ROOT.TSpectrum(200)
        numberPeaksFound                    = spectrum.Search(hist_SinglePulse,1,"",0.1)
        hist_SinglePulse                    = subtractBackground(hist_SinglePulse,spectrum)
        integral                            = hist_SinglePulse.Integral()
        mainPeak_Amplitude, mainPeak_Time   = findMainPeak(spectrum, numberPeaksFound)

        # evaluate if this event is valid or not
        goodEvent = eventSelection(numberPeaksFound, mainPeak_Time, mainPeak_Amplitude, integral )

        # print event results in the terminal
        if verbose == True:
            printEvent(i,numberPeaksFound,integral,mainPeak_Amplitude,mainPeak_Time,goodEvent)

        # # debug: uncomment to draw the peak you want to investigate
        # # if goodEvent == False:
        # # if i > 500:
        # if True:
            # drawHist(hist_SinglePulse)
            # set_trace()

        # if the event is bad, dump it
        if goodEvent == False: continue

        # filling the histograms
        hist_NumberOfPeaks.Fill(numberPeaksFound)
        hist_Amplitude.Fill(mainPeak_Amplitude)
        hist_Integral.Fill(integral)
        hist_Time.Fill(mainPeak_Time)

    #extract the amplitude AverageValue and StdDev
    amplitude_Mean      = hist_Amplitude.GetMean()
    amplitude_StdDev    = hist_Amplitude.GetStdDev()

    return amplitude_Mean, amplitude_StdDev

pf.setpfstyle()

verbose = True

# f2200 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2200V.root")
# f2300 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2300V.root")
# f2400 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2400V.root")
# f2500 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2500V.root")
# f2600 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2600V.root")
# f2700 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2700V.root")
# f2800 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2800V.root")
# f2900 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2900V.root")
# f3000 = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode3000V.root")
# files = [f2200,f2300,f2400,f2500,f2600,f2700,f2800,f2900,f3000]

# t2200 = f2200.Get("tree")
# t2300 = f2300.Get("tree")
# t2400 = f2400.Get("tree")
# t2500 = f2500.Get("tree")
# t2600 = f2600.Get("tree")
# t2700 = f2700.Get("tree")
# t2800 = f2800.Get("tree")
# t2900 = f2900.Get("tree")
# t3000 = f3000.Get("tree")
# trees = [t2200,t2300,t2400,t2500,t2600,t2700,t2800,t2900,t3000]

f2900_DriftVelocity = ROOT.TFile.Open("data/20191114_Cathode3000V_Anode2900V_DriftVelocity.root")
t2900_DriftVelocity = f2900_DriftVelocity.Get("tree")
files=[f2900_DriftVelocity]
trees=[t2900_DriftVelocity]

# makeCummulativePlots(files,trees)
# set_trace()

#######################################
# start of drift velocity
#######################################
f = ROOT.TFile("20191114_Cathode3000V_Anode2900V_DriftVelocity_Tree.root","recreate")
ttree = ROOT.TTree("tree","analysis result for driftvelocity") 

t_event       = array('i',[0])
t_n_peaks     = array('i',[0])
t_amplitude   = array('f',[0])
t_time        = array('f',[0])
t_integral    = array('f',[0])

ttree.Branch('event',t_event,'event/I')
ttree.Branch('n_peaks',t_n_peaks,'n_peaks/I')
ttree.Branch('amplitude',t_amplitude,'amplitude/F')
ttree.Branch('time',t_time,'time/F')
ttree.Branch('integral',t_integral,'integral/F')

hist_SinglePulse    = ROOT.TH1F('hist_SinglePulse','hist_SinglePulse',500,0,3200) 

for i,entry in enumerate(t2900_DriftVelocity):
    # basic sanity check of the event
    resultSanityCheck = sanityCheck(entry.chn1_t,entry.chn1_v)
    if resultSanityCheck == False: set_trace()

    # generate pulse, find peak(s), subtract background, compute keyMetrics
    hist_SinglePulse                    = makeEventHistogram(hist_SinglePulse,entry)
    spectrum                            = ROOT.TSpectrum(200)
    numberPeaksFound                    = spectrum.Search(hist_SinglePulse,1,"",0.1)
    hist_SinglePulse                    = subtractBackground(hist_SinglePulse,spectrum)
    integral                            = hist_SinglePulse.Integral()
    mainPeak_Amplitude, mainPeak_Time   = findMainPeak(spectrum, numberPeaksFound)

    # evaluate if this event is valid or not
    goodEvent = eventSelection(numberPeaksFound, mainPeak_Time, mainPeak_Amplitude, integral )

    # print event results in the terminal
    if verbose == True:
        printEvent(i,numberPeaksFound,integral,mainPeak_Amplitude,mainPeak_Time,goodEvent)

    # # debug: uncomment to draw the peak you want to investigate
    # # if goodEvent == False:
    # # if i > 500:
    # if True:
        # drawHist(hist_SinglePulse)
        # set_trace()

    # if the event is bad, dump it
    if goodEvent == False: continue

    # fill the tree
    t_event[0] = i
    t_n_peaks[0] = numberPeaksFound
    t_amplitude[0] = mainPeak_Amplitude
    t_time[0] = mainPeak_Time
    t_integral[0] = integral
    ttree.Fill()

f.Write()
f.Close()

set_trace()
#######################################
# end of driftvelocity
#######################################

hist_SinglePulse    = ROOT.TH1F('hist_SinglePulse','hist_SinglePulse',500,0,3200) 
hist_NumberOfPeaks  = ROOT.TH1I('hist_NumberOfPeaks','hist_NumberOfPeaks',200,0,200)
hist_Amplitude      = ROOT.TH1F('hist_Amplitude','hist_Amplitude',50,0.0,0.2)
hist_Integral       = ROOT.TH1F('hist_Integral','hist_Integral',50,0,200)
hist_Time           = ROOT.TH1F('hist_Time','hist_Time',500,0,3200)
histograms = [hist_SinglePulse, hist_NumberOfPeaks, hist_Amplitude, hist_Integral, hist_Time]


amplitude_Mean, amplitude_StdDev = analyseSingleWorkingPoint(histograms,trees[0])
print('amplitude_Mean: %f; amplitude_StdDev: %f'%(amplitude_Mean,amplitude_StdDev))
set_trace()

# can_GasAmplification = ROOT.TCanvas('can_GasAmplification','can_GasAmplification',800,500)
# anode_voltage       = array( 'f', [2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0])
# anode_voltage_sigma = array( 'f', [0.,0.,0.,0.,0.,0,0,0,0])
# amplitude_mean      = array( 'f', [16,26,47,66,107,140,161,165,167])
# amplitude_sigma     = array( 'f', [2,4,5,9,16,15,6,4,3])
# gr_GasAmplification = ROOT.TGraphErrors(len(anode_voltage),anode_voltage,amplitude_mean,anode_voltage_sigma, amplitude_sigma)
# gr_GasAmplification.Draw('AP')
# gr_GasAmplification.GetXaxis().SetTitle('anode voltage [kV]')
# gr_GasAmplification.GetYaxis().SetTitle('average peak height [mV]')
# gr_GasAmplification.GetYaxis().SetRangeUser(7.,500.)
# can_GasAmplification.SetLogy()
# can_GasAmplification.Update()
# can_GasAmplification.SaveAs('GasAmplification.root')
# set_trace()

#draw all the histograms of a specific working point
can_NumberOfPeaks   = ROOT.TCanvas('can_NumberOfPeaks','can_NumberOfPeaks')
can_Amplitude       = ROOT.TCanvas('can_Amplitude','can_Amplitude')
can_Integral        = ROOT.TCanvas('can_Integral','can_Integral')
can_Time            = ROOT.TCanvas('can_Time','can_Time')

can_NumberOfPeaks.cd()
hist_NumberOfPeaks.Draw()
hist_NumberOfPeaks.GetXaxis().SetTitle('number of peaks')
can_NumberOfPeaks.Update()
can_NumberOfPeaks.SaveAs('can_NumberOfPeaks.png')

can_Amplitude.cd()
hist_Amplitude.Draw()
hist_Amplitude.GetXaxis().SetTitle('amplitude')
can_Amplitude.Update()
can_Amplitude.SaveAs('can_Amplitude.png')
can_Amplitude.SaveAs('can1_Amplitude.root')

can_Integral.cd()
hist_Integral.Draw()
hist_Integral.GetXaxis().SetTitle('integral')
can_Integral.Update()
can_Integral.SaveAs('can_Integral.png')

can_Time.cd()
hist_Time.Draw()
hist_Time.GetXaxis().SetTitle('time of the peak')
can_Time.Update()
can_Time.SaveAs('can_Time.png')

set_trace()


