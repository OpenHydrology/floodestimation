'''
Created on 7 May 2014

@author: NUT67271
'''

import wx,os
import numpy as np

def createDatabase(searchPath,outfile):
  f = open(outfile,'w')
  f.write("VERSION, STATION, NAME, GRID, IHDTM X, IHDTM Y , CENTROID X, CENTROID Y, DTM AREA, ALTBAR, ASPBAR, BFIHOST, DPLBAR, DPSBAR, FARL, FPEXT, LDP, PROPWET, RMED1H, RMED1D, RMED2D, SAAR, SAAR4170, SPRHOST, URBCONC1990, URBEXT1990, URBLOC1990, URBCONC2000, URBEXT2000, URBLOC2000,SUIT QMED, SUIT POOL, QMed_obs,\n")

  searchForDirectories(searchPath,f)
  
  f.close()

def searchForDirectories(searchPath,f):
  list = os.listdir(searchPath)
  for item in list:
    currentPath = os.path.join(searchPath,item)
    if os.path.isdir(currentPath):
      print item
      searchForDirectories(currentPath,f)
    elif os.path.isfile(currentPath):
      if item.lower().endswith('cd3'):
        readFile(currentPath,f)
 
def qmedFromAmFile(file):
  amaxSeries = list()
  f = open(file,'r')
  
  lines = f.readlines()
  ams = False
  
  for line in lines:
    if ams == False:
      if line.startswith('[AM Values]'):
        ams=True
    elif ams==True:
      if line.startswith('[END}'):
        pass
      else:
        try:
          flow = float(line.split(',')[1])
          amaxSeries.append(flow)
        except:
          pass
  try:
    qmed = np.median(amaxSeries)
  except:
    print file,amaxSeries
  
  return qmed
  
def readFile(filePath,f):
            FILE = open(filePath,"r") 
  ## The following lines extract the values from the .cd3 file
            marker = 1         
            linecount = 1
            for line in FILE.read().split('\n'):
               if line[:7] == "VERSION":
                    VERSION=line[8:]
                    
               if marker == 1:
                    STATION = line
                    marker = 0
               if line == "[STATION NUMBER]":
                    marker = 1
                    

               if line[:4] == "NAME":
                    NAME=line[5:]

               if line[:8] == "LOCATION":
                    LOCATION=line[9:]

               if line[:9] == "IHDTM NGR":  ## this captures the x and y co-ordinates in one go (already x,y)
                    GRID=line[10:12]
                    IHDTM_NGR=line[-13:]
                    if IHDTM_NGR[0]== ",":  ## this if removes shorter grid references
                          IHDTM_NGR = list()
                          IHDTM_NGR = line[-12:]

               if line[:12] == "CENTROID NGR":  ## this captures the x and y co-ordinates in one go (already x,y)
                     CENTROID_NGR=line[-13:]
                     if CENTROID_NGR[0] == ",": ## this if removes shorter grid references
                          CENTROID_NGR = list()
                          CENTROID_NGR = line[-12:]

               if line[:8] == "DTM AREA":
                     AREA=line[9:]
                     
               if line[:6] == "ALTBAR":
                     ALTBAR=line[7:]

               if line[:6] == "ASPBAR":
                     ASPBAR=line[7:]
                     
               if line[:6] == "ASPVAR":
                     ASPVAR=line[7:]
                     
               if line[:7] == "BFIHOST":
                     BFIHOST=line[8:]
                     
               if line[:6] == "DPLBAR":
                     DPLBAR=line[7:]
                     
               if line[:6] == "DPSBAR":
                     DPSBAR=line[7:]
                     
               if line[:4] == "FARL":
                     FARL=line[5:]
                     
               if line[:5] == "FPEXT":
                     FPEXT=line[6:]

               if line[:3] == "LDP":
                    LDP=line[4:]                   

               if line[:7] == "PROPWET":
                    PROPWET=line[8:]

               if line[:7] == "RMED-1H":
                    RMED1H=line[8:]
                    
               if line[:7] == "RMED-1D":
                    RMED1D=line[8:]

               if line[:7] == "RMED-2D":
                    RMED2D=line[8:]

               if line[:5] == "SAAR,":
                    SAAR=line[5:]

               if line[:8] == "SAAR4170":
                    SAAR4170=line[9:]

               if line[:7] == "SPRHOST":
                    SPRHOST=line[8:]

               if line[:11] == "URBCONC1990":
                    URBCONC1990=line[12:]

               if line[:10] == "URBEXT1990":
                    URBEXT1990=line[11:]

               if line[:10] == "URBLOC1990":
                    URBLOC1990=line[11:]

               if line[:11] == "URBCONC2000":
                    URBCONC2000=line[12:]

               if line[:10] == "URBEXT2000":
                    URBEXT2000=line[11:]

               if line[:10] == "URBLOC2000":
                    URBLOC2000=line[11:]

               if line[:4] == "QMED":
                    SUIT_QMED=line[5:]

               if line[:7] == "POOLING":
                    SUIT_POOL=line[8:]                 

            #filecount = filecount + 1
            FILE.close()
            
            if GRID.lower() !='gb' or SUIT_QMED.lower() != 'yes':
              return
            
            amFile = filePath[:-3]+'AM'
            
            qmed = qmedFromAmFile(amFile)
           
            #if filename[-3:]  == suffix:
            try:
              f.write(str(VERSION)+","+str(STATION)+","+str(NAME)+","+str(GRID)+","+str(IHDTM_NGR)+","+str(CENTROID_NGR)+","+str(AREA)+","+str(ALTBAR)+","+str(ASPBAR)+","+str(BFIHOST)+","+str(DPLBAR)+","+str(DPSBAR)+","+str(FARL)+","+str(FPEXT)+","+str(LDP)+","+str(PROPWET)+","+str(RMED1H)+","+str(RMED1D)+","+str(RMED2D)+","+str(SAAR)+","+str(SAAR4170)+","+str(SPRHOST)+","+str(URBCONC1990)+","+str(URBEXT1990)+","+str(URBLOC1990)+","+str(URBCONC2000)+","+str(URBEXT2000)+","+str(URBLOC2000)+","+str(SUIT_QMED)+","+str(SUIT_POOL)+","+str(qmed)+', \n')
            except:
              pass


class PreferencesFrame(wx.Frame):
    def __init__(self, parent):
      super(PreferencesFrame, self).__init__(parent,title="Preferences...",size=(600,300))
      
      if os.path.isfile('preferences.txt')==False:
        '''Initialise preferences '''
        self.qmed_cds_dbs_path = "qmed_database.csv"
        self.amax_db_path = "amax_database.csv"
      else:
        pf = open('preferences.txt','r')
        lines = pf.readlines()
        
        for line in lines:
          if line.startswith('#'):
            pass
          elif line.startswith('qmed_cds_dbs_path'):
            self.qmed_cds_dbs_path = line.split(':')[-1]
          elif line.startswith('amax_db_path'):
            self.amax_db_path = line.split(':')[-1]
      
      self.InitUI(parent)
      self.Layout()
      self.Refresh()
      self.Centre()
      self.Show()
      
    def InitUI(self,parent):
        self.panel = wx.Panel(self,-1)
        self.p = parent
        
        
        self.qmed_cds_dbs_label = wx.StaticText(self.panel, -1, "CDS and QMED database")
        self.qmed_cds_dbs = wx.TextCtrl(self.panel, -1, self.qmed_cds_dbs_path)
        self.amax_db_label = wx.StaticText(self.panel, -1, "AMAX databse")
        self.amax_db = wx.TextCtrl(self.panel, -1, self.amax_db_path)
        
        self.hiflows_dataset_label = wx.StaticText(self.panel, -1, "For copyright the Hiflows dataset must be downloaded")
        
        self.generate_qmed_cds_dbs_btn = wx.Button(self.panel, -1, ' Create QMED & CDS database ')
        self.generate_amax_dbs_btn = wx.Button(self.panel, -1, ' Create AMAX database ')
        self.cancel_btn = wx.Button(self.panel, -1, ' Cancel ')
        self.save_btn = wx.Button(self.panel, -1, ' Save ')
        self.generate_qmed_cds_dbs_btn.Bind(wx.EVT_BUTTON, self.OnGenerateQmedCdsDb)
        self.generate_amax_dbs_btn.Bind(wx.EVT_BUTTON, self.OnGenerateAmaxDb)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.save_btn.Bind(wx.EVT_BUTTON, self.OnSave)
        
        sizer = wx.GridBagSizer(vgap=10, hgap=10)
        sizer.Add(self.qmed_cds_dbs_label, pos=(0, 0), span=(1,1))
        sizer.Add(self.qmed_cds_dbs, pos=(0, 1), span=(1,1))
        sizer.Add(self.amax_db_label, pos=(1, 0), span=(1,1))
        sizer.Add(self.amax_db, pos=(1, 1), span=(1,1))
        
        sizer.Add(self.generate_qmed_cds_dbs_btn, pos=(0, 2), span=(1,1))
        sizer.Add(self.generate_amax_dbs_btn, pos=(1, 2), span=(1,1))
        sizer.Add(self.hiflows_dataset_label,pos=(2,0), span=(1,3))
        sizer.Add(self.cancel_btn, pos=(4, 3), span=(1,1))
        sizer.Add(self.save_btn, pos=(4, 4), span=(1,1))
        
        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 20)
        self.panel.SetSizerAndFit(border)
        self.panel.Fit()
        
        self.panel.Layout()
        self.panel.Refresh()
    
    def OnGenerateQmedCdsDb(self,event):
      loadBox = wx.DirDialog(self, "Hiflows data directory ...","", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
      
      #self.title_label.SetLabel(str(self.p.title.GetValue()))
      if loadBox.ShowModal() == wx.ID_OK:
        searchPath = loadBox.GetPath()  
        outfile = 'qmed_database.csv'
        createDatabase(searchPath,outfile)
        self.qmed_cds_dbs.SetLabel(outfile)
    
    def OnGenerateAmaxDb(self,event):
      pass        
    
    def OnCancel(self,event):
      self.Destroy()
    
    def OnSave(self,event):
      self.qmed_cds_dbs_path = self.qmed_cds_dbs.GetValue()
      self.amax_db_path = self.amax_db.GetValue()
      
      pf = open('preferences.txt','w')
      
      pf.write('amax_db_path:'+str(self.amax_db_path)+'\n')
      pf.write('qmed_cds_dbs_path:'+str(self.qmed_cds_dbs_path))
      
      pf.close()
      self.Destroy()

    
if __name__ == "__main__":
    app = wx.App(redirect=False)
    #app = wx.App(redirect=True,filename='error_log.txt')
    PreferencesFrame(None).Show()
    app.MainLoop()