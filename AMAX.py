'''
Created on 7 May 2014

@author: Neil Nutt, neilnutt[at]googlemail[dot]com

Used to calculate QMED from flow data
Called from within the QMED tab

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

import wx
import numpy as np

class AmaxFrame(wx.Frame):
    def __init__(self, parent):
      super(AmaxFrame, self).__init__(parent,title="Amax series",size=(500,500))

      
      self.InitUI(parent)
      self.Layout()
      self.Refresh()
      self.Centre()
      self.Show()
      
    def InitUI(self,parent):
        self.panel = wx.Panel(self,-1)
        self.p = parent
        
        
        self.delimitor_label = wx.StaticText(self.panel, -1, "Delimitor")
        self.delimitor = wx.TextCtrl(self.panel, -1, ",")
        self.header_rows_label = wx.StaticText(self.panel, -1, "Number of header rows")
        self.header_rows = wx.TextCtrl(self.panel, -1, "1")
        self.flow_data_column_label = wx.StaticText(self.panel, -1, "Flow data in column")
        self.flow_data_column = wx.TextCtrl(self.panel, -1, "1")
        self.data_series_entry = wx.TextCtrl(self.panel, -1, "Data series entry", size=(450,300),style=wx.TE_MULTILINE)
        
        self.load_flow_btn = wx.Button(self.panel, -1, ' Load flow series ')
        self.cancel_flow_btn = wx.Button(self.panel, -1, ' Cancel ')
        self.save_flow_btn = wx.Button(self.panel, -1, ' Save ')
        self.load_flow_btn.Bind(wx.EVT_BUTTON, self.OnLoadFlowSeries)
        self.cancel_flow_btn.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.save_flow_btn.Bind(wx.EVT_BUTTON, self.OnSave)   
        
        sizer = wx.GridBagSizer(vgap=10, hgap=10)
        sizer.Add(self.delimitor_label, pos=(0, 0), span=(1,1))
        sizer.Add(self.delimitor, pos=(1, 0), span=(1,1))
        sizer.Add(self.header_rows_label, pos=(0, 1), span=(1,1))
        sizer.Add(self.header_rows, pos=(1, 1), span=(1,1))
        sizer.Add(self.flow_data_column_label, pos=(0, 2), span=(1,1))
        sizer.Add(self.flow_data_column, pos=(1, 2), span=(1,1))
        sizer.Add(self.data_series_entry, pos=(3, 0), span=(1,4))
        
        sizer.Add(self.load_flow_btn, pos=(4, 0), span=(1,1))
        sizer.Add(self.cancel_flow_btn, pos=(4, 2), span=(1,1))
        sizer.Add(self.save_flow_btn, pos=(4, 3), span=(1,1))
      
        
        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 20)
        self.panel.SetSizerAndFit(border)
        self.panel.Fit()
        
        self.panel.Layout()
        self.panel.Refresh()
    
    def OnLoadFlowSeries(self,event):
      loadBox = wx.FileDialog(self, "Open flow series file", "", "","", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
      
      #self.title_label.SetLabel(str(self.p.title.GetValue()))
      if loadBox.ShowModal() == wx.ID_OK:
        filePath = loadBox.GetPath()
        f = open(filePath,'r')
        lines = f.readlines()
        text = ""
        for line in lines:
          #print line
          self.data_series_entry.AppendText(str(line))
        #self.data_series_entry.SetLabel(str(text))
        
    
    def OnCancel(self,event):
      self.Destroy()
    
    def OnSave(self,event):
      user_enterer_data_series = self.data_series_entry.GetValue()
      header_rows = int(self.header_rows.GetValue())
      separator = self.delimitor.GetValue()
      column = int(self.flow_data_column.GetValue())-1
      lines = user_enterer_data_series.split('\n')
      self.p.data_series = list()
      self.p.amax_data_series = list()
      for line in lines[header_rows:]:
        data_entry = line.split(separator)
        if len(data_entry) > column:
          self.p.amax_data_series.append(float(data_entry[column]))
        
      print self.p.amax_data_series
      median = np.median(self.p.amax_data_series)
      self.p.qmed_obs_amax.SetLabel(str(median))
      self.Destroy()
    
if __name__ == "__main__":
    app = wx.App(redirect=False)
    #app = wx.App(redirect=True,filename='error_log.txt')
    AmaxFrame(None).Show()
    app.MainLoop()