'''
Created on 27 Apr 2014

@author: Neil Nutt, neilnutt[at]googlemail[dot]com

Tab for generating the flood growth curve

    Statistical Flood Estimation Tool
    Copyright (C) 2014  Neil Nutt, neilnutt[at]googlemail[dot]com
    https://github.com/OpenHydrology/StatisticalFloodEstimationTool

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''
import wx,os,sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import wx.lib.plot as plot
import feh_statistical,config


class MainPanel(wx.Panel):
    def __init__(self,parent,cds_tab,qmed_tab):
        #wx.Frame.__init__(self, None, title="Notebook Remove Pages Example")
        wx.Panel.__init__(self, parent)
        
        self.cds_tab = cds_tab
        self.qmed_tab=qmed_tab
        
        #pannel  = wx.Panel(self)
        vbox    = wx.BoxSizer(wx.VERTICAL)
        hbox    = wx.BoxSizer(wx.HORIZONTAL)

        self.buttonInsertStandard = wx.Button(self, id=wx.ID_ANY, label="Add standard FGC", size=(100, 25))
        self.buttonInsertStandard.Bind(wx.EVT_BUTTON, self.onButtonInsertStandard)
        hbox.Add(self.buttonInsertStandard)

        self.buttonInsertStatistical = wx.Button(self, id=wx.ID_ANY, label="Add statistical FGC", size=(100, 25))
        self.buttonInsertStatistical.Bind(wx.EVT_BUTTON, self.onButtonInsertStatistical)
        hbox.Add(self.buttonInsertStatistical)

        vbox.Add(hbox)

        self.Notebook3 = wx.Notebook(self)
        vbox.Add(self.Notebook3, 2, flag=wx.EXPAND)

        self.SetSizer(vbox)

        self.pageCounter = 0
        self.addStandardPage()

    def addStatisticalPage(self):
        self.pageCounter += 1
        page      = PoolingPanel(self.Notebook3,self.cds_tab,self.qmed_tab)
        pageTitle = "FGC: {0}".format(str(self.pageCounter))
        self.Notebook3.AddPage(page, pageTitle)

    def addStandardPage(self):
        self.pageCounter += 1
        page      = StandardPanel(self.Notebook3,self.cds_tab,self.qmed_tab)
        pageTitle = "FGC: {0}".format(str(self.pageCounter))
        self.Notebook3.AddPage(page, pageTitle)


    def onButtonRemove(self, event):   
        self.Notebook3.DeletePage(0)

    def onButtonInsertStatistical(self, event):   
        self.addStatisticalPage()
        self.Layout()
        self.Refresh()

    def onButtonInsertStandard(self, event):   
        self.addStandardPage()
        self.Layout()
        self.Refresh()



class StandardPanel(wx.Panel):
    def __init__(self, parent,cds_tab,qmed_tab):
      wx.Panel.__init__(self, parent)
      self.cds_tab=cds_tab
      
      
      self.fgc_notes = wx.TextCtrl(self, -1, "Notes on use of standard FSR growth curve", size=(400,100),style=wx.TE_MULTILINE)

      
      standard_flood_growth_curve_names=['1','2','3','4','5','6','7','8','9','10']
      self.floodGrowthCurveSelector = wx.ListBox(self, id=-1, size=(200,100),style=wx.LB_SINGLE, choices=standard_flood_growth_curve_names, name='Standard curve')
      self.floodGrowthCurveSelector.SetSelection(0)
      
      self.list_ctrl = wx.ListCtrl(self, size=(350,200),style=wx.LC_REPORT|wx.BORDER_SUNKEN)
      self.list_ctrl.InsertColumn(0, 'RP (yr)', width=100)
      self.list_ctrl.InsertColumn(1, 'AEP (%)', width=100)
      self.list_ctrl.InsertColumn(2, 'Growth factor', width=100)
      
      self.addStardardRPs()
      self.floodGrowthCurveSelector.Bind(wx.EVT_LISTBOX, self.onChangeGrowthCurve)
      
      sizer = wx.GridBagSizer(vgap=5, hgap=10)
      sizer.Add(self.fgc_notes, pos=(0,0), span=(1,4))
      sizer.Add(self.list_ctrl,pos=(1,0),span=(1,4))

      sizer.Add(self.floodGrowthCurveSelector, pos=(0,4),span=(3,2))
      
      self.updateFloodGrowthCurves()
      
      border = wx.BoxSizer()
      border.Add(sizer, 0, wx.ALL, 20)
      self.SetSizerAndFit(border)
      self.Fit()
      
    def onChangeGrowthCurve(self,event):    
      self.updateFloodGrowthCurves()

      
    def updateFloodGrowthCurves(self):
      # Find out what growth curve is selected
      from numpy import interp
      i = self.floodGrowthCurveSelector.GetSelection()
      fgcName =self.floodGrowthCurveSelector.GetString(i)
      #fgcName = self.list_ctrl.GetItemText(0)
      yrs = [2,5,10,25,50,100,500]
      
      
      if fgcName == '1':   
        fgcfs = [1.0,1.33,1.61,2.01,2.36,2.76,3.61]
      elif fgcName == '2':
        fgcfs = [1.0,1.22,1.56,1.99,2.38,2.89,3.79]
      elif fgcName == '3':
        fgcfs = [1.0,1.33,1.54,1.81,2.02,2.21,2.90]
      elif fgcName == '4':
        fgcfs = [1.0,1.38,1.67,2.10,2.47,2.89,4.07]
      elif fgcName == '5':
        fgcfs = [1.0,1.45,1.85,2.53,3.18,4.00,5.64]
      elif fgcName == '6':
        fgcfs = [1.0,1.45,1.84,2.43,2.98,3.63,5.10]
      elif fgcName == '7':
        fgcfs = [1.0,1.45,1.84,2.43,2.98,3.63,5.10]        
      elif fgcName == '8':
        fgcfs = [1.0,1.40,1.69,2.09,2.41,2.75,3.88]       
      elif fgcName == '9':
        fgcfs = [1.0,1.30,1.53,1.84,2.09,2.34,3.08]      
      elif fgcName == '10':
        fgcfs = [1.0,1.28,1.48,1.76,1.99,2.24,2.94] 

        
      for i in range(self.list_ctrl.GetItemCount()):
        rp = float(self.list_ctrl.GetItem(i,0).GetText())
        growthFactor = round(interp(rp,yrs,fgcfs),3)
        self.list_ctrl.SetStringItem(i, 2, str(growthFactor))
      
    def  addStardardRPs(self):
      events = [[2.0,0.5],[10.0,0.1],[50.0,0.02],[100.0,0.01],[200.0,0.05],[500.0,0.002]]
      self.index =0
      for rp,aep, in events:     
        index = self.list_ctrl.InsertStringItem(sys.maxint, str(rp))
        self.list_ctrl.SetStringItem(index, 1, str(aep))
        self.list_ctrl.SetStringItem(index, 2, str('-'))
        self.index += 1




class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,size=(750,150), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class PoolingPanel(wx.Panel):
    def __init__(self, parent,cds_tab,qmed_tab):
      wx.Panel.__init__(self, parent)
      self.cds_tab=cds_tab
      
      #self.data_series = None
      #self.amax_data_series = None
      self.subject_saar = float(self.cds_tab.saar.GetValue())
      self.subject_carea = float(self.cds_tab.carea.GetValue())
      self.subject_farl = float(self.cds_tab.farl.GetValue())
      self.subject_fpext = float(self.cds_tab.fpext.GetValue())
      
      self.fgc_notes = wx.TextCtrl(self, -1, "Notes on FGC", size=(400,100),style=wx.TE_MULTILINE)
      
      self.station_search_distance_label = wx.StaticText(self, -1, "Station search distance")
      
      self.selected_years_of_record_label = wx.StaticText(self, -1, "Selected years of data")
      self.selected_years_of_record = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.selected_stations_count_label = wx.StaticText(self, -1, "Number of stations")
      self.selected_stations_count = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.pooled_lcv_label = wx.StaticText(self, -1, "L-CV")
      self.pooled_lcv = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.pooled_lskew_label = wx.StaticText(self, -1, "L-SKEW")
      self.pooled_lskew = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)      
      self.goodness_of_fit_label = wx.StaticText(self, -1, "Goodness of fit")
      self.goodness_of_fit = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.heterogeneity_label = wx.StaticText(self, -1, "Heterogeneity")
      self.heterogeneity = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)

      self.delete_tab_btn = wx.Button(self, -1, ' Delete tab ')
      self.duplicate_tab_btn = wx.Button(self, -1, ' Duplicate tab ')

      self.sort_by_geo_dist_btn = wx.Button(self, -1, 'Sort by geo dist')
      self.sort_by_hyd_dist_btn = wx.Button(self, -1, 'Sort by hyd dist')
      self.sort_by_user_dist_btn = wx.Button(self, -1, 'Sort by user dist')
      self.station_search_distance = wx.TextCtrl(self, -1, "1000.0")
      self.refresh_stations_btn = wx.Button(self, -1, ' Refresh stations ')
      self.add_station_btn = wx.Button(self, -1, ' Add station ')  
      self.remove_station_btn = wx.Button(self, -1, ' Remove station ')
      self.clear_user_stations_btn = wx.Button(self, -1, ' Clear add/removes ')
      self.refresh_pooling_group_btn = wx.Button(self, -1, ' Refresh pooling ')
      
      self.list_ctrl = wx.ListCtrl(self, size=(350,200),style=wx.LC_REPORT|wx.BORDER_SUNKEN)
      self.list_ctrl.InsertColumn(0, 'RP (yr)', width=100)
      self.list_ctrl.InsertColumn(1, 'AEP (%)', width=100)
      self.list_ctrl.InsertColumn(2, 'Growth factor', width=100)
      
      self.addStardardRPs()

      self.add_rp_btn = wx.Button(self, label="Add RP")
      self.add_rp_btn.Bind(wx.EVT_BUTTON, self.add_rp)
      self.plot_pooling_group = wx.Button(self, label="Plot pooling group")
      self.plot_pooling_group.Bind(wx.EVT_BUTTON, self.onPlotPoolingGroup)
      
      self.refresh_pooling_group_btn.Bind(wx.EVT_BUTTON, self.OnRefreshPoolingGroup)
      self.refresh_stations_btn.Bind(wx.EVT_BUTTON, self.OnRefreshStations)
      self.add_station_btn.Bind(wx.EVT_BUTTON, self.OnAddStation)
      self.remove_station_btn.Bind(wx.EVT_BUTTON, self.OnRemoveStation)
      self.clear_user_stations_btn.Bind(wx.EVT_BUTTON, self.OnClearUser)
      self.delete_tab_btn.Bind(wx.EVT_BUTTON, self.OnDeleteTab)
      self.duplicate_tab_btn.Bind(wx.EVT_BUTTON, self.OnDuplicateTab)
      self.sort_by_geo_dist_btn.Bind(wx.EVT_BUTTON, self.SortByGeoDist)
      self.sort_by_hyd_dist_btn.Bind(wx.EVT_BUTTON, self.SortByHydDist)
      self.sort_by_user_dist_btn.Bind(wx.EVT_BUTTON, self.SortByUserDist)
      
      self.winfap3_weighting = wx.RadioButton(self, -1, 'WINFAP3 hyd dist weighting', style=wx.RB_GROUP)
      self.geo_distance_weighting  = wx.RadioButton(self, -1, 'Geo dist weighting')
      self.user_dist_weighting  = wx.RadioButton(self, -1, 'User dist weighting')
      
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.winfap3_weighting.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.geo_distance_weighting.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.user_dist_weighting.GetId())
      

      
      fitting_methods=['L-moments median (L-MED)','L-moments mean (L-MOM) - not implemented','Generalised extreme variable (GEV) - not implemented']
      self.fittingMethodSelector = wx.ListBox(self, id=-1, size=(200,50),style=wx.LB_SINGLE, choices=fitting_methods, name='Fitting method')
      self.fittingMethodSelector.SetSelection(0)
          
      sizer = wx.GridBagSizer(vgap=5, hgap=10)
      sizer.Add(self.fgc_notes, pos=(0,0), span=(3,4))
      
      self.table = wx.Panel(self, -1)
      self.list = CheckListCtrl(self.table)
      self.list.InsertColumn(0, 'STATION')
      self.list.InsertColumn(1, 'GEO DIST')
      self.list.InsertColumn(2,'HYD DIST')
      self.list.InsertColumn(3, 'AREA')
      self.list.InsertColumn(4, 'SAAR')
      self.list.InsertColumn(5, 'BFIHOST')
      self.list.InsertColumn(6, 'FARL')
      self.list.InsertColumn(7, 'FPEXT')
      self.list.InsertColumn(8, 'RECORDS')
      self.list.InsertColumn(9, 'QMED?')
      self.list.InsertColumn(10, 'POOLING?')
      self.list.InsertColumn(11, 'L-CV')
      self.list.InsertColumn(12, 'L-CV W')
      self.list.InsertColumn(13, 'L-SKEW')
      self.list.InsertColumn(14, 'L-SKEW W')
      
      self.findStations()
      self.refreshStations()
      
      sizer.Add(self.table, pos=(5,0),span=(4,6),flag=wx.EXPAND)
      sizer.Add(self.station_search_distance_label, pos=(10,0),span=(1,1))
      sizer.Add(self.station_search_distance, pos=(10,1),span=(1,1))
      sizer.Add(self.refresh_stations_btn, pos=(10,2),span=(1,1))
      sizer.Add(self.add_station_btn, pos=(10,3),span=(1,1))
      sizer.Add(self.remove_station_btn, pos=(10,4),span=(1,1))
      sizer.Add(self.clear_user_stations_btn, pos=(10,5),span=(1,1))        
      sizer.Add(self.winfap3_weighting, pos=(12,0),span=(1,2))
      sizer.Add(self.geo_distance_weighting, pos=(13,0),span=(1,2))
      sizer.Add(self.user_dist_weighting, pos=(14,0),span=(1,2))
      
      sizer.Add(self.fittingMethodSelector, pos=(0,4),span=(3,2))
  
      sizer.Add(self.sort_by_geo_dist_btn, pos=(5,7),span=(1,1))
      sizer.Add(self.sort_by_hyd_dist_btn, pos=(6,7),span=(1,1))
      sizer.Add(self.sort_by_user_dist_btn, pos=(7,7),span=(1,1))  
      sizer.Add(self.refresh_pooling_group_btn,pos=(8,7),span=(1,1))
      
      sizer.Add(self.selected_years_of_record_label, pos=(12,4),span=(1,1))
      sizer.Add(self.selected_years_of_record, pos=(12,5),span=(1,1))
      sizer.Add(self.selected_stations_count_label, pos=(13,4),span=(1,1))
      sizer.Add(self.selected_stations_count, pos=(13,5),span=(1,1))
      sizer.Add(self.pooled_lcv_label,pos=(14,4),span=(1,1))
      sizer.Add(self.pooled_lcv,pos=(14,5),span=(1,1))
      sizer.Add(self.pooled_lskew_label,pos=(15,4),span=(1,1))
      sizer.Add(self.pooled_lskew,pos=(15,5),span=(1,1))

      sizer.Add(self.goodness_of_fit_label ,pos=(16,4),span=(1,1))
      sizer.Add(self.goodness_of_fit ,pos=(16,5),span=(1,1))
      sizer.Add(self.heterogeneity_label,pos=(17,4),span=(1,1))     
      sizer.Add(self.heterogeneity,pos=(17,5),span=(1,1)) 
      
      sizer.Add(self.delete_tab_btn ,pos=(1,7),span=(1,1))
      sizer.Add(self.duplicate_tab_btn ,pos=(0,7),span=(1,1))
      
      sizer.Add(self.list_ctrl,pos=(12,6),span=(4,4))
      sizer.Add(self.add_rp_btn,pos=(10,7),span=(1,1))
      sizer.Add(self.plot_pooling_group,pos=(10,8),span=(1,1))
      
      border = wx.BoxSizer()
      border.Add(sizer, 0, wx.ALL, 20)
      self.SetSizerAndFit(border)
      self.Fit()
      
    def  addStardardRPs(self):
      events = [[2.0,0.5],[10.0,0.1],[50.0,0.02],[100.0,0.01],[200.0,0.05],[1000.0,0.001]]
      self.index =0
      for rp,aep, in events:     
        index = self.list_ctrl.InsertStringItem(sys.maxint, str(rp))
        self.list_ctrl.SetStringItem(index, 1, str(aep))
        self.list_ctrl.SetStringItem(index, 2, str('-'))
        self.index += 1
    
    def onPlotPoolingGroup(self,event):  
      frm = wx.Frame(self, -1, 'Flood growth curve', size=(600,450))
      client = plot.PlotCanvas(frm)
      client.SetEnableLegend(True)
      self.data_a = [(2,1), (2.5,1.4), (10,2), (30,2.7), (50,3), (100,3.5)]
      self.data_b = [(2,1), (2.5,1.7), (3,1.9), (40,2.8), (5,2.9), (70,3.2), (150,3.3)]
      
      #circle dot square triangle triangle_down cross plus 
      station_a = plot.PolyMarker(self.data_a, legend='Dummy Station A', colour='green', marker='square', size=1)
      station_b = plot.PolyMarker(self.data_b, legend='Dummy Station B', colour='blue', marker='circle', size=1)
      fitted_line = plot.PolyLine(self.fitted_fgc_tupples, legend='Fitted FGC', colour='black', width=1)
      gc = plot.PlotGraphics([station_a,station_b,fitted_line], 'Flood growth curve', 'Return period (1 in x yrs)', 'Flood growth factor (unitless)')
      client.Draw(gc, xAxis=(2,1000), yAxis=(0,5.0))
      frm.Show(True)
                
    def add_rp(self, event):
      line = "Line %s" % self.index
      self.list_ctrl.InsertStringItem(self.index, "?")
      self.list_ctrl.SetStringItem(self.index, 1, "?")
      self.list_ctrl.SetStringItem(self.index, 2, "?")
      self.index += 1
      
    def findStations(self):
          #self.qmed_databse = "C:\\Users\\nut67271\\workspace\\StatisticalFloodEstimationTool\\qmed_db.csv"
          if os.path.isfile('preferences.txt')==False:
            '''Initialise preferences '''
            import Preferences
            Preferences.PreferencesFrame(self).Show()
      
            self.Refresh()
            self.Update()  
          else:
            pf = open('preferences.txt','r')
            lines = pf.readlines()
            
            for line in lines:
              if line.startswith('#'):
                pass
              elif line.startswith('qmed_cds_dbs_path'):
                self.qmed_cds_dbs_path = line.split(':')[-1].replace('\n','')          
                if os.path.isfile(self.qmed_cds_dbs_path) == False:
                  self.OnQMedDatabseError()
                  print 'QMED DB not found, need to raise error'
                  self.stations = list()
                  return
      
            
          f = open(self.qmed_cds_dbs_path,'r')
          lines = f.readlines()
          
          headers = lines[0].split(',')
          station_cds_index=list()
          i=0
          
          for header in headers:
            label = header.replace(' ','').lower()
            station_cds_index.append(label)
            i=i+1
          
          self.stations = list()
          
          
          for line in lines[1:]:
            entries = line.split(',')
            
            station_cds=dict()
            i=0
            for field in station_cds_index:
              try:
                station_cds[field]=float(entries[i])
              except ValueError:
                station_cds[field]=str(entries[i])
              except IndexError:
                pass
              i=i+1
            
            # Now pull out amax values
            station_cds['amaxList'] = list()
            for i in range(len(station_cds_index),len(entries)-1):
              
              station_cds['amaxList'].append(float(entries[i])/station_cds['qmed_obs'])
             
            self.location_centroid_x =float(self.cds_tab.centroid_x.GetValue())
            self.location_centroid_y = float(self.cds_tab.centroid_y.GetValue())
            station_cds['distance'] = 0.001*(((station_cds['centroidx']-self.location_centroid_x)**2.0+(station_cds['centroidy']-self.location_centroid_y))**2.0)**0.5        
            
            station_cds['records']=len(station_cds['amaxList'])
            
            station_cds['hy_dist'] = feh_statistical.calc_feh_hyd_dist(self,station_cds)
            
            try:            
              QMed,kappa,beta_GL_LMED,location  = feh_statistical.fitGLbyLMED(station_cds['amaxList'])
              station_cds['l-cv']=beta_GL_LMED
              station_cds['l-skew']=-kappa
              lcv_w,lskew_w = feh_statistical.calc_weights(station_cds['hy_dist'],station_cds['records'])
              station_cds['lcv_w']=lcv_w
              station_cds['lskew_w']=lskew_w
            
              station_cds['user_added'] = None
            
              self.stations.append(station_cds)
              
            except ZeroDivisionError:
              pass
              #print station_cds['station']
              
            except ValueError:
              print station_cds['station']
      

    def OnClearUser(self,event):
        i=0
        for station_cds in self.stations:
          self.stations[i]['user_added'] = None
          i=i+1
        self.list.DeleteAllItems()     
        self.refreshStations()
        self.Refresh()
        self.Update()  
              
    def OnRefreshStations(self,event): 
      self.list.DeleteAllItems()     
      self.refreshStations()
      self.Refresh()
      self.Update()
      
    def refreshStations(self):
      self.search_distance =float(self.station_search_distance.GetValue())
      
      self.stations.sort(key = lambda station_cds: station_cds['hy_dist'])
      
      for station_cds in self.stations:
            station_cds['distance'] = 0.001*(((station_cds['centroidx']-self.location_centroid_x)**2.0+(station_cds['centroidy']-self.location_centroid_y)**2.0))**0.5
            if station_cds['distance'] > self.search_distance and station_cds['user_added'] != True:
              pass
            elif station_cds['user_added'] == False:
              pass
            else:
              if bool(self.winfap3_weighting.GetValue()) == True:
                pass
                #qmed_cds = feh_statistical.qmed_cds1999(station_cds['dtmarea'],station_cds['saar'],station_cds['farl'],station_cds['sprhost'],station_cds['bfihost'])
              if bool(self.geo_distance_weighting.GetValue()) == True:
                pass
                #qmed_cds = feh_statistical.area_based_qmed(station_cds['dtmarea'])
              if bool(self.user_dist_weighting.GetValue()) == True:
                pass
                #qmed_cds = station_cds['qmed_obs']
              '''
              try:
                station_cds['qmed_error'] = station_cds['qmed_obs']/qmed_cds
              except:
                station_cds['qmed_error'] = 0.0
              station_cds['asg'] = feh_statistical.calc_asg(station_cds['distance'])
              '''
              index = self.list.InsertStringItem(sys.maxint, str(int(station_cds['station'])))
              self.list.SetStringItem(index, 1, str(station_cds['distance']))
              self.list.SetStringItem(index, 2, str(station_cds['hy_dist']))
              self.list.SetStringItem(index, 3, str(station_cds['dtmarea']))
              self.list.SetStringItem(index, 4, str(int(station_cds['saar'])))
              self.list.SetStringItem(index, 5, str(station_cds['bfihost']))
              self.list.SetStringItem(index, 6, str(station_cds['farl']))
              self.list.SetStringItem(index, 7, str(station_cds['fpext']))
              self.list.SetStringItem(index, 8, str(station_cds['records']))
              self.list.SetStringItem(index, 9, str(station_cds['suitqmed']))
              self.list.SetStringItem(index, 10, str(station_cds['suitpool']))
              self.list.SetStringItem(index, 11, str(station_cds['l-cv']))
              self.list.SetStringItem(index, 12, str(station_cds['lcv_w']))             
              self.list.SetStringItem(index, 13, str(station_cds['l-skew']))
              self.list.SetStringItem(index, 14, str(station_cds['lskew_w']))


    def OnAddStation(self,event):
        stations_txt = list()
        stations_ids =list()
        for station_cds in self.stations:
          stations_txt.append(str(station_cds['station']))
          stations_ids.append(station_cds['station'])
        dlg = wx.SingleChoiceDialog(self, 'Add station', 'Which station do you want to add?', stations_txt, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
          i = 0
          for station_cds in self.stations:
            if dlg.GetStringSelection() == str(station_cds['station']):
              self.stations[i]['user_added'] = True
            i=i+1
          dlg.Destroy()
          self.list.DeleteAllItems()     
          self.refreshStations()
          self.Refresh()
          self.Update()



    def OnRemoveStation(self,event):
        stations_txt = list()
        stations_ids =list()
        stations_count = self.list.GetItemCount()
        for i in range(stations_count):
          stations_txt.append(str(self.list.GetItem(i,0).GetText()))
          stations_ids.append(self.list.GetItem(i,0).GetText())
        
        dlg = wx.SingleChoiceDialog(self, 'Remove station', 'Which station do you want to remove?', stations_txt, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
          i = 0
          for station_cds in self.stations:
            if dlg.GetStringSelection() == str(int(station_cds['station'])):
              self.stations[i]['user_added'] = False
            i=i+1
          dlg.Destroy()
          self.list.DeleteAllItems()     
          self.refreshStations()
          self.Refresh()
          self.Update()
          
    def OnRefreshPoolingGroup(self,event):
      self.calcWeights()
      self.updateFloodGrowthCurves()

    def updateFloodGrowthCurves(self):
      beta = self.weighted_lcv
      kappa = -self.weighted_lskew
      self.fitted_fgc_tupples=list()
      for i in range(self.list_ctrl.GetItemCount()):
        rp = float(self.list_ctrl.GetItem(i,0).GetText())
        growthFactor = feh_statistical.calculateGrowthFactor_GL_LMED(beta,kappa,rp)
        self.list_ctrl.SetStringItem(i, 2, str(growthFactor))
        self.fitted_fgc_tupples.append((rp,growthFactor))

    def calcWeights(self):   ####
      weighted_lcvs=list()
      lcv_weights=list()
      weighted_lskews=list()
      lskew_weights=list()
      years_of_data=list()
      stations = self.list.GetItemCount()
      
      if True == True:
      #if bool(self.distance_decay_update.GetValue()) == True: 
        for i in range(stations):
          if bool(self.list.IsChecked(i)) == True:
            years = int(self.list.GetItem(i,8).GetText())
            lcv = float(self.list.GetItem(i,11).GetText())
            lcv_w = float(self.list.GetItem(i,12).GetText())
            lskew = float(self.list.GetItem(i,13).GetText())
            lskew_w = float(self.list.GetItem(i,14).GetText())
            weighted_lcvs.append(lcv*lcv_w)
            lcv_weights.append(lcv_w)
            weighted_lskews.append(lskew*lskew_w)
            lskew_weights.append(lskew_w)
            years_of_data.append(years)
        if len(weighted_lcvs) == 0:
          raise "No stations selected"
        else:
          self.weighted_lcv = sum(weighted_lcvs)/sum(lcv_weights)
          self.weighted_lskew = sum(weighted_lskews)/sum(lskew_weights)
          years_of_data = sum(years_of_data)
          number_of_stations = len(weighted_lcvs)
        self.pooled_lcv.SetLabel(str(self.weighted_lcv))
        self.pooled_lskew.SetLabel(str(self.weighted_lskew))
        self.selected_years_of_record.SetLabel(str(years_of_data))
        self.selected_stations_count.SetLabel(str(number_of_stations))
        
      
      self.Refresh()
      self.Update()

          
    def SetWeightingUpdate(self,event):
      pass
    
    def SortByGeoDist(self,event):
      pass
    
    def SortByHydDist(self,event):
      pass
  
    def SortByUserDist(self,event):
      pass
   
    def OnDeleteTab(self,event):
        pass
    
    def OnDuplicateTab(self,event):
        pass
        

      