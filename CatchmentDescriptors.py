'''
Created on 27 Apr 2014

@author: Neil Nutt, neilnutt[at]googlemail[dot]com

Tab used to store/collect catchment descriptors

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
import wx,os,cds_reader,time
import config

class Fpanel(wx.Panel):
    def __init__(self, parent,p):
        wx.Panel.__init__(self, parent)
        #title_label = wx.StaticText(self, -1, p.title.GetValue())
        self.parent =parent
        self.p=p
        #self.title_label = wx.StaticText(self, -1, "-")
        outlet_label = wx.StaticText(self, -1, "Outlet grid ref")
        centroid_label = wx.StaticText(self, -1, "Centroid grid ref" )                       
        carea_label = wx.StaticText(self, -1, "DTM_AREA")
        altbar_label = wx.StaticText(self, -1, "ALTBAR")
        aspbar_label = wx.StaticText(self, -1, "ASPBAR")
        aspvar_label = wx.StaticText(self, -1, "ASPVAR")
        bfihost_label = wx.StaticText(self, -1, "BFIHOST")
        dplbar_label = wx.StaticText(self, -1, "DPLBAR")
        dpsbar_label = wx.StaticText(self, -1, "DPSBAR")
        farl_label = wx.StaticText(self, -1, "FARL")
        fpext_label = wx.StaticText(self, -1, "FPEXT")
        ldp_label = wx.StaticText(self, -1, "LDP")
        propwet_label = wx.StaticText(self, -1, "PROPWET")
        saar_label = wx.StaticText(self, -1, "SAAR")
        sprhost_label = wx.StaticText(self, -1, "SPRHOST")
        urbconc1990_label = wx.StaticText(self, -1, "URBCONC1990")
        urbconc2000_label = wx.StaticText(self, -1, "URBCONC2000")
        urbext1990_label = wx.StaticText(self, -1, "URBEXT1990")
        urbext2000_label = wx.StaticText(self, -1, "URBEXT1990")
        urbloc1990_label = wx.StaticText(self, -1, "URBLOC1990")
        urbloc2000_label = wx.StaticText(self, -1, "URBLOC2000")
        chnl_width_label = wx.StaticText(self, -1, "Channel width")
        assessment_year_label = wx.StaticText(self, -1, "Assessment year")
        
        
        self.outlet_grid = wx.TextCtrl(self, -1, "GB")
        self.outlet_x = wx.TextCtrl(self, -1, "0")
        self.outlet_y = wx.TextCtrl(self, -1, "0")
        self.centroid_grid = wx.TextCtrl(self, -1, "GB")  
        self.centroid_x = wx.TextCtrl(self, -1, "0")
        self.centroid_y = wx.TextCtrl(self, -1, "0")        
        self.carea = wx.TextCtrl(self, -1, "0")
        self.altbar = wx.TextCtrl(self, -1, "0")
        self.aspbar = wx.TextCtrl(self, -1, "0")
        self.aspvar = wx.TextCtrl(self, -1, "0")
        self.bfihost = wx.TextCtrl(self, -1, "0")
        self.dplbar = wx.TextCtrl(self, -1, "0")
        self.dpsbar = wx.TextCtrl(self, -1, "0")
        self.farl = wx.TextCtrl(self, -1, "0")
        self.fpext = wx.TextCtrl(self, -1, "0")
        self.ldp = wx.TextCtrl(self, -1, "0")
        self.propwet = wx.TextCtrl(self, -1, "0")
        self.saar = wx.TextCtrl(self, -1, "0")
        self.sprhost = wx.TextCtrl(self, -1, "0")
        self.urbconc1990 = wx.TextCtrl(self, -1, "0")
        self.urbconc2000 = wx.TextCtrl(self, -1, "0")
        self.urbext1990 = wx.TextCtrl(self, -1, "0")
        self.urbext2000 = wx.TextCtrl(self, -1, "0")
        self.urbloc1990 = wx.TextCtrl(self, -1, "0")
        self.urbloc2000 = wx.TextCtrl(self, -1, "0")
        self.chnl_width = wx.TextCtrl(self, -1, "0")
        self.assessment_year = wx.TextCtrl(self, -1, time.asctime(time.localtime())[-4:])
        
        self.outlet_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.centroid_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.carea_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.altbar_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.aspbar_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.aspvar_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.bfihost_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.dplbar_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.dpsbar_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.farl_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.fpext_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.ldp_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.propwet_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.saar_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.sprhost_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.urbconc1990_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.urbconc2000_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.urbext1990_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.urbext2000_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.urbloc1990_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.urbloc2000_note = wx.TextCtrl(self, -1, "",size=(200,25))
        self.chnl_width_note = wx.TextCtrl(self, -1, "",size=(200,25))
        
        
        
        
        
        self.load_btn = wx.Button(self, -1, ' Load cds ')       
        self.cds_notes = wx.TextCtrl(self, -1, "Your notes", size=(500, 100), style=wx.TE_MULTILINE)
        
        #  Assign actions to buttons
        self.load_btn.Bind(wx.EVT_BUTTON, self.onLoadCds)
        
        # use gridbagsizer for layout of widgets
        sizer = wx.GridBagSizer(vgap=1, hgap=10)
        #sizer.Add(self.title_label,pos=(0,0))
        sizer.Add(outlet_label, pos=(1, 0))
        sizer.Add(centroid_label, pos=(2, 0))
        sizer.Add(carea_label, pos=(3, 0))
        sizer.Add(altbar_label, pos=(4, 0))
        sizer.Add(aspbar_label, pos=(5, 0))
        sizer.Add(aspvar_label, pos=(6, 0))
        sizer.Add(bfihost_label, pos=(7,0))
        sizer.Add(dplbar_label, pos=(8, 0))
        sizer.Add(dpsbar_label, pos=(9, 0))
        sizer.Add(farl_label, pos=(10, 0))
        sizer.Add(fpext_label, pos=(11, 0))
        sizer.Add(ldp_label, pos=(12, 0))
        sizer.Add(propwet_label, pos=(13, 0))
        sizer.Add(saar_label, pos=(14, 0))
        sizer.Add(sprhost_label, pos=(15, 0))
        sizer.Add(urbconc1990_label, pos=(16, 0))
        sizer.Add(urbconc2000_label, pos=(17, 0))
        sizer.Add(urbext1990_label, pos=(18, 0))
        sizer.Add(urbext2000_label, pos=(19, 0))
        sizer.Add(urbloc1990_label, pos=(20, 0))
        sizer.Add(urbloc2000_label, pos=(21, 0))
        sizer.Add(chnl_width_label, pos=(22, 0))
        sizer.Add(assessment_year_label, pos=(23, 0))
        
        sizer.Add(self.outlet_grid, pos=(1, 1))
        sizer.Add(self.outlet_x, pos=(1, 2))
        sizer.Add(self.outlet_y, pos=(1, 3))
        sizer.Add(self.centroid_grid, pos=(2, 1))
        sizer.Add(self.centroid_x, pos=(2, 2))
        sizer.Add(self.centroid_y, pos=(2, 3))
        sizer.Add(self.carea, pos=(3, 1))
        sizer.Add(self.altbar, pos=(4, 1))
        sizer.Add(self.aspbar, pos=(5, 1))
        sizer.Add(self.aspvar, pos=(6, 1))
        sizer.Add(self.bfihost, pos=(7,1))
        sizer.Add(self.dplbar, pos=(8, 1))
        sizer.Add(self.dpsbar, pos=(9, 1))
        sizer.Add(self.farl, pos=(10, 1))
        sizer.Add(self.fpext, pos=(11, 1))
        sizer.Add(self.ldp, pos=(12, 1))
        sizer.Add(self.propwet, pos=(13, 1))
        sizer.Add(self.saar, pos=(14, 1))
        sizer.Add(self.sprhost, pos=(15, 1))
        sizer.Add(self.urbconc1990, pos=(16, 1))
        sizer.Add(self.urbconc2000, pos=(17, 1))
        sizer.Add(self.urbext1990, pos=(18, 1))
        sizer.Add(self.urbext2000, pos=(19, 1))
        sizer.Add(self.urbloc1990, pos=(20, 1))
        sizer.Add(self.urbloc2000, pos=(21, 1))
        sizer.Add(self.chnl_width, pos=(22, 1))
        sizer.Add(self.assessment_year, pos=(23, 1))

        sizer.Add(self.outlet_note, pos=(1, 4))
        sizer.Add(self.centroid_note, pos=(2, 4))
        sizer.Add(self.carea_note, pos=(3, 4))
        sizer.Add(self.altbar_note, pos=(4, 4))
        sizer.Add(self.aspbar_note, pos=(5, 4))
        sizer.Add(self.aspvar_note, pos=(6, 4))
        sizer.Add(self.bfihost_note, pos=(7,4))
        sizer.Add(self.dplbar_note, pos=(8, 4))
        sizer.Add(self.dpsbar_note, pos=(9, 4))
        sizer.Add(self.farl_note, pos=(10, 4))
        sizer.Add(self.fpext_note, pos=(11, 4))
        sizer.Add(self.ldp_note, pos=(12, 4))
        sizer.Add(self.propwet_note, pos=(13, 4))
        sizer.Add(self.saar_note, pos=(14, 4))
        sizer.Add(self.sprhost_note, pos=(15, 4))
        sizer.Add(self.urbconc1990_note, pos=(16, 4))
        sizer.Add(self.urbconc2000_note, pos=(17, 4))
        sizer.Add(self.urbext1990_note, pos=(18, 4))
        sizer.Add(self.urbext2000_note, pos=(19, 4))
        sizer.Add(self.urbloc1990_note, pos=(20, 4))
        sizer.Add(self.urbloc2000_note, pos=(21, 4))
        sizer.Add(self.chnl_width_note, pos=(22, 4))

        sizer.Add(self.load_btn, pos=(24, 1), span=(1, 1))
        
        sizer.Add(self.cds_notes, pos=(25, 0), span=(1,5))
        
        # use boxsizer to add border around sizer
        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 20)
        self.SetSizerAndFit(border)
        self.Fit()
        
    def onLoadCds(self,event):
      #loadBox = wx.FileDialog(self,message="Open",defaultDir=os.getcwd(),defaultFile="CSV files (*.csv)|*.csv",style=wx.OPEN)
      loadBox = wx.FileDialog(self, "Open cds file", "", "","Catchment descriptor files (*.csv)|*.csv", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
      
      #self.title_label.SetLabel(str(self.p.title.GetValue()))
      if loadBox.ShowModal() == wx.ID_OK:
        filePath = loadBox.GetPath()
        cds = cds_reader.csvCds(filePath)
        
        self.outlet_grid.SetLabel(str(cds['CATCHMENT'][0]))
        self.outlet_x.SetLabel(str(cds['CATCHMENT'][1]))
        self.outlet_y.SetLabel(str(cds['CATCHMENT'][2]))
        try:
          self.centroid_grid.SetLabel(str(cds['CENTROID'][0]))
          self.centroid_x.SetLabel(str(cds['CENTROID'][1]))
          self.centroid_y.SetLabel(str(cds['CENTROID'][2]))
        except:   
          self.centroid_grid.SetLabel(str('-'))
          self.centroid_x.SetLabel(str('-'))
          self.centroid_y.SetLabel(str('-'))
        self.carea.SetLabel(str(cds['AREA']))
        self.altbar.SetLabel(str(cds['ALTBAR']))
        self.aspbar.SetLabel(str(cds['ASPBAR']))
        self.aspvar.SetLabel(str(cds['ASPVAR']))
        self.bfihost.SetLabel(str(cds['BFIHOST']))
        self.dplbar.SetLabel(str(cds['DPLBAR']))
        self.dpsbar.SetLabel(str(cds['DPSBAR']))
        self.farl.SetLabel(str(cds['FARL']))
        self.ldp.SetLabel(str(cds['LDP']))
        self.propwet.SetLabel(str(cds['PROPWET']))
        self.saar.SetLabel(str(cds['SAAR']))
        self.sprhost.SetLabel(str(cds['SPRHOST']))
        try:
          self.fpext.SetLabel(str(cds['FPEXT']))
        except:
          self.fpext.SetLabel(str('-'))
        try:
          self.urbconc1990.SetLabel(str(cds['URBCONC1990']))
          self.urbext1990.SetLabel(str(cds['URBEXT1990']))
          self.urbloc1990.SetLabel(str(cds['URBLOC1990']))
        except:
          self.urbconc1990.SetLabel(str('-'))
          self.urbext1990.SetLabel(str('-'))
          self.urbloc1990.SetLabel(str('-'))
        try:
          self.urbloc2000.SetLabel(str(cds['URBLOC2000']))
          self.urbconc2000.SetLabel(str(cds['URBCONC2000']))
          self.urbext2000.SetLabel(str(cds['URBEXT2000']))
        except:
          self.urbloc2000.SetLabel(str('-'))
          self.urbconc2000.SetLabel(str('-'))
          self.urbext2000.SetLabel(str('-'))
      loadBox.Destroy()
      
      self.Refresh()
      self.Update()