import ROOT
import plotfactory as pf
import numpy as np
import sys
from array import array
from pdb import set_trace

def readData(data_file):
    #####################################################
    # import data into a ROOT tree
    #####################################################
    input_file  = ROOT.TFile("data.root","recreate")
    ttree       = ROOT.TTree("tree","raw data for UWis")

    #define variables as numpy arrays
    t_event     = array('i',[0])
    t_DOY       = array('f',[0])
    t_Year      = array('i',[0])
    t_Month     = array('i',[0]) 
    t_Day       = array('i',[0])
    t_Time      = array('i',[0])
    t_Rain_mm   = array('f',[0])
    t_Tair_C    = array('f',[0])
    t_PAR_umol  = array('f',[0])
    t_co2_ppm   = array('f',[0])
    t_NEE_umol  = array('f',[0])
    t_GPP_umol  = array('f',[0])
    t_TER_umol  = array('f',[0])
    t_ET_mm     = array('f',[0])
    t_LE_W      = array('f',[0])
    t_H_W       = array('f',[0])

    # define ROOT tree branches
    ttree.Branch('event'    ,t_event     ,'event/I')
    ttree.Branch('DOY'      ,t_DOY       ,'DOY/F')
    ttree.Branch('Year'     ,t_Year      ,'Year/I')
    ttree.Branch('Month'    ,t_Month     ,'Month/I') 
    ttree.Branch('Day'      ,t_Day       ,'Day/I')
    ttree.Branch('Time'     ,t_Time      ,'Time/I')
    ttree.Branch('Rain_mm'  ,t_Rain_mm   ,'Rain_mm/F')
    ttree.Branch('Tair_C'   ,t_Tair_C    ,'Tair_C/F')
    ttree.Branch('PAR_umol' ,t_PAR_umol  ,'PAR_umol/F')
    ttree.Branch('co2_ppm'  ,t_co2_ppm   ,'co2_ppm/F')
    ttree.Branch('NEE_umol' ,t_NEE_umol  ,'NEE_umol/F')
    ttree.Branch('GPP_umol' ,t_GPP_umol  ,'GPP_umol/F')
    ttree.Branch('TER_umol' ,t_TER_umol  ,'TER_umol/F')
    ttree.Branch('ET_mm'    ,t_ET_mm     ,'ET_mm/F')
    ttree.Branch('LE_W'     ,t_LE_W      ,'LE_W/F')
    ttree.Branch('H_W'      ,t_H_W       ,'H_W/F')

    
    import csv

    with open(data_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                try:
                    t_event    [0]= line_count 
                    t_DOY      [0]= float(row[0])
                    t_Year     [0]= int(row[1])
                    t_Month    [0]= int(row[2])
                    t_Day      [0]= int(row[3])
                    t_Time     [0]= int(row[4])
                    t_Rain_mm  [0]= float(row[5])
                    t_Tair_C   [0]= float(row[6])
                    t_PAR_umol [0]= float(row[7])
                    t_co2_ppm  [0]= float(row[8])
                    t_NEE_umol [0]= float(row[9])
                    t_GPP_umol [0]= float(row[10])
                    t_TER_umol [0]= float(row[11])
                    t_ET_mm    [0]= float(row[12])
                    t_LE_W     [0]= float(row[13])
                    t_H_W      [0]= float(row[14])
                    line_count += 1
                    ttree.Fill()
                except:
                    set_trace()
    
    input_file.Write()
    input_file.Close()

def makePlot_TH2F(ttree, x_var, y_var, n_x, x_min, x_max, n_y, y_min, y_max):

    plot_name   = 'x:%s; y:%s'%(x_var,y_var)
    can         = ROOT.TCanvas(plot_name,plot_name)
    hist        = ROOT.TH2F('h','', n_x, x_min, x_max, n_y, y_min, y_max)

    hist.SetTitle(';%s;%s'%(x_var,y_var))
    ttree.Draw('%s:%s >> hist'%(y_var,x_var))
    hist.Draw('colz')
    set_trace()
    


if __name__ == '__main__':
    data_file = '/home/dehuazhu/playground/UwisAna/data.csv'
    readData(data_file)


    pf.setpfstyle()
    input_tree_file = ROOT.TFile('data.root')
    input_tree = input_tree_file.Get('tree')
    # makePlot(ttree, x_var, y_var, x_min, x_max, y_min, y_max)

    # makePlot_TH2F(input_tree, 'DOY', 'NEE_umol', 100, 152., 159., 100, -30., 30.)
    makePlot_TH2F(input_tree, 'PAR_umol', 'NEE_umol', 25, 0., 2500., 25, -35., 20.)
    

