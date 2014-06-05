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
import feh_statistical


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
      
      
      self.fgc_notes = wx.TextCtrl(self, -1, "Notes on FGC", size=(400,210),style=wx.TE_MULTILINE)

      
      standard_flood_growth_curve_names=['1','2','3','4','5','6','7']
      self.floodGrowthCurveSelector = wx.ListBox(self, id=-1, size=(200,50),style=wx.LB_SINGLE, choices=standard_flood_growth_curve_names, name='Standard curve')
      self.floodGrowthCurveSelector.SetSelection(0)
      
      sizer = wx.GridBagSizer(vgap=5, hgap=10)
      sizer.Add(self.fgc_notes, pos=(0,0), span=(7,4))


      sizer.Add(self.floodGrowthCurveSelector, pos=(0,4),span=(3,3))
    
      
      border = wx.BoxSizer()
      border.Add(sizer, 0, wx.ALL, 20)
      self.SetSizerAndFit(border)
      self.Fit()





class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,size=(750,200), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class PoolingPanel(wx.Panel):
    def __init__(self, parent,cds_tab,qmed_tab):
      wx.Panel.__init__(self, parent)
      self.cds_tab=cds_tab
      
      #self.data_series = None
      #self.amax_data_series = None
      
      self.fgc_notes = wx.TextCtrl(self, -1, "Notes on FGC", size=(400,210),style=wx.TE_MULTILINE)
      
      self.station_search_distance_label = wx.StaticText(self, -1, "Station search distance")
      
      self.selected_years_of_record_label = wx.StaticText(self, -1, "Selected years of data")
      self.selected_years_of_record = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)
      self.selected_stations_count_label = wx.StaticText(self, -1, "Number of stations")
      self.selected_stations_count = wx.TextCtrl(self, -1, "-", style =wx.TE_READONLY)

      self.add_next_best_station_btn = wx.Button(self, -1, ' Add next best station ')
      self.remove_worst_station_btn = wx.Button(self, -1, ' Remove worst station ')
      self.station_search_distance = wx.TextCtrl(self, -1, "1000.0")
      self.refresh_stations_btn = wx.Button(self, -1, ' Refresh stations ')
      self.add_station_btn = wx.Button(self, -1, ' Add station ')  
      self.remove_station_btn = wx.Button(self, -1, ' Remove station ')
      self.clear_user_stations_btn = wx.Button(self, -1, ' Clear add/removes ')
      
      self.refresh_stations_btn.Bind(wx.EVT_BUTTON, self.OnRefreshStations)
      self.add_station_btn.Bind(wx.EVT_BUTTON, self.OnAddStation)
      self.remove_station_btn.Bind(wx.EVT_BUTTON, self.OnRemoveStation)
      self.clear_user_stations_btn.Bind(wx.EVT_BUTTON, self.OnClearUser)
      
      self.winfap_2008_weighting = wx.RadioButton(self, -1, 'WINFAP 2008 weighting', style=wx.RB_GROUP)
      self.feh_1999_weighting = wx.RadioButton(self, -1, "FEH 1999 weighting")
      self.distance_weighting  = wx.RadioButton(self, -1, 'Distance weighting')
      self.equal_weighting  = wx.RadioButton(self, -1, 'Equal weighting')
      self.user_weighting  = wx.RadioButton(self, -1, 'User weighting')
      
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.winfap_2008_weighting.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.feh_1999_weighting.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.distance_weighting.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.equal_weighting.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.SetWeightingUpdate, id=self.user_weighting.GetId())
      
      self.Bind(wx.EVT_RADIOBUTTON, self.AddNextBestStation, id=self.user_weighting.GetId())
      self.Bind(wx.EVT_RADIOBUTTON, self.RemoveWorstStation, id=self.user_weighting.GetId())
       
      
      fitting_methods=['L-moments median (L-MED)','L-moments mean (L-MOM)','Generalised extreme variable (GEV)']
      self.fittingMethodSelector = wx.ListBox(self, id=-1, size=(200,50),style=wx.LB_SINGLE, choices=fitting_methods, name='Fitting method')
      self.fittingMethodSelector.SetSelection(0)
          
      sizer = wx.GridBagSizer(vgap=5, hgap=10)
      sizer.Add(self.fgc_notes, pos=(0,0), span=(7,4))
      
      self.table = wx.Panel(self, -1)
      self.list = CheckListCtrl(self.table)
      self.list.InsertColumn(0, 'STATION')
      self.list.InsertColumn(1, 'DISTANCE')
      self.list.InsertColumn(2, 'AREA')
      self.list.InsertColumn(3, 'SAAR')
      self.list.InsertColumn(4, 'BFIHOST')
      self.list.InsertColumn(5, 'FARL')
      self.list.InsertColumn(6, 'FPEXT')
      self.list.InsertColumn(7, 'RECORDS')
      self.list.InsertColumn(8, 'QMED?')
      self.list.InsertColumn(9, 'POOLING?')
      self.list.InsertColumn(10, 'L-CV')
      self.list.InsertColumn(11, 'W1')
      self.list.InsertColumn(12, 'L-SKEW')
      self.list.InsertColumn(13, 'W2')
      
      self.findStations()
      self.refreshStations()
      
      sizer.Add(self.table, pos=(9,0),span=(1,6),flag=wx.EXPAND)
      sizer.Add(self.station_search_distance_label, pos=(10,0),span=(1,1))
      sizer.Add(self.station_search_distance, pos=(10,1),span=(1,1))
      sizer.Add(self.refresh_stations_btn, pos=(10,2),span=(1,1))
      sizer.Add(self.add_station_btn, pos=(10,3),span=(1,1))
      sizer.Add(self.remove_station_btn, pos=(10,4),span=(1,1))
      sizer.Add(self.clear_user_stations_btn, pos=(10,5),span=(1,1))        
      sizer.Add(self.winfap_2008_weighting, pos=(11,0),span=(1,2))
      sizer.Add(self.feh_1999_weighting, pos=(12,0),span=(1,2))
      sizer.Add(self.equal_weighting, pos=(13,0),span=(1,2))
      sizer.Add(self.distance_weighting, pos=(14,0),span=(1,2))
      sizer.Add(self.user_weighting, pos=(15,0),span=(1,2))
      
      sizer.Add(self.fittingMethodSelector, pos=(0,4),span=(3,3))
      
      sizer.Add(self.selected_years_of_record_label, pos=(12,4),span=(1,1))
      sizer.Add(self.selected_years_of_record, pos=(12,5),span=(1,1))
      sizer.Add(self.selected_stations_count_label, pos=(13,4),span=(1,1))
      sizer.Add(self.selected_stations_count, pos=(13,5),span=(1,1))

      sizer.Add(self.add_next_best_station_btn, pos=(4,6),span=(1,1))
      sizer.Add(self.remove_worst_station_btn, pos=(5,6),span=(1,1))
      
      border = wx.BoxSizer()
      border.Add(sizer, 0, wx.ALL, 20)
      self.SetSizerAndFit(border)
      self.Fit()
      
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
            station_cds['l-cv']=0.0
            station_cds['l-skew']=0.0
            station_cds['w1']=1.0
            station_cds['w2']=1.0

            
            station_cds['user_added'] = None
            
            self.stations.append(station_cds)
       
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
      for station_cds in self.stations:
            station_cds['distance'] = 0.001*(((station_cds['centroidx']-self.location_centroid_x)**2.0+(station_cds['centroidy']-self.location_centroid_y)**2.0))**0.5
            if station_cds['distance'] > self.search_distance and station_cds['user_added'] != True:
              pass
            elif station_cds['user_added'] == False:
              pass
            else:
              if bool(self.feh_1999_weighting.GetValue()) == True:
                pass
                #qmed_cds = feh_statistical.qmed_cds2008(station_cds['dtmarea'],station_cds['saar'],station_cds['farl'],station_cds['bfihost'])
              if bool(self.winfap_2008_weighting.GetValue()) == True:
                pass
                #qmed_cds = feh_statistical.qmed_cds1999(station_cds['dtmarea'],station_cds['saar'],station_cds['farl'],station_cds['sprhost'],station_cds['bfihost'])
              if bool(self.equal_weighting.GetValue()) == True:
                pass
                #qmed_cds = feh_statistical.area_based_qmed(station_cds['dtmarea'])
              if bool(self.user_weighting.GetValue()) == True:
                pass
                #qmed_cds = station_cds['qmed_obs']
              
              try:
                station_cds['qmed_error'] = station_cds['qmed_obs']/qmed_cds
              except:
                station_cds['qmed_error'] = 0.0
              station_cds['asg'] = feh_statistical.calc_asg(station_cds['distance'])
  
              index = self.list.InsertStringItem(sys.maxint, str(int(station_cds['station'])))
              self.list.SetStringItem(index, 1, str(station_cds['distance']))
              self.list.SetStringItem(index, 2, str(station_cds['dtmarea']))
              self.list.SetStringItem(index, 3, str(int(station_cds['saar'])))
              self.list.SetStringItem(index, 4, str(station_cds['bfihost']))
              self.list.SetStringItem(index, 5, str(station_cds['farl']))
              self.list.SetStringItem(index, 6, str(station_cds['fpext']))
              self.list.SetStringItem(index, 7, str(station_cds['records']))
              self.list.SetStringItem(index, 8, str(station_cds['suitqmed']))
              self.list.SetStringItem(index, 9, str(station_cds['suitpool']))
              self.list.SetStringItem(index, 10, str(station_cds['l-cv']))
              self.list.SetStringItem(index, 11, str(station_cds['w1']))             
              self.list.SetStringItem(index, 12, str(station_cds['l-skew']))
              self.list.SetStringItem(index, 13, str(station_cds['w2']))


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
          
    def SetWeightingUpdate(self,event):
      pass
    
    def AddNextBestStation(self,event):
      pass
    
    def RemoveWorstStation(self,event):
      pass
        
        

      