'''
Created on 27 Apr 2014

@author: Neil Nutt, neilnutt[at]googlemail[dot]com

Main body, to be called first

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
import wx,os
import FrontPage,CatchmentDescriptors,QMED,GrowthCurve,Summary




class MainFrame(wx.Frame):
    def __init__(self, parent):
      super(MainFrame, self).__init__(parent,title="Statistical Flood Estimation Tool",size=(600,600))

      # --- initialize other settings
      self.dirName = ""
      self.fileName = ""
      self.title = ""

      
      self.InitUI()
      self.Centre()
      self.Show()
      
    def InitUI(self):
        self.panel = wx.Panel(self,-1)
      
        menubar = wx.MenuBar()

        #  Defining the file menu
        fileMenu = wx.Menu()
        mN = wx.MenuItem(fileMenu, wx.ID_NEW, '&New\tCtrl+N')
        mO = wx.MenuItem(fileMenu, wx.ID_OPEN, '&Open\tCtrl+O')
        mSA = wx.MenuItem(fileMenu, wx.ID_SAVEAS, '&Save as\tCtrl+ALT+S')
        mS = wx.MenuItem(fileMenu, wx.ID_SAVE, '&Save\tCtrl+S')
        fileMenu.AppendItem(mN)
        fileMenu.AppendItem(mO)
        fileMenu.AppendItem(mS)
        fileMenu.AppendItem(mSA)
        fileMenu.AppendSeparator()
        mQ = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        fileMenu.AppendItem(mQ)
        self.Bind(wx.EVT_MENU, self.OnNew, mN)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, mO)
        self.Bind(wx.EVT_MENU, self.OnFileSave, mS)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, mSA)
        self.Bind(wx.EVT_MENU, self.OnQuit, mQ)

        # Defining the edit menu
        editMenu = wx.Menu()
        mPreferences = wx.MenuItem(editMenu, wx.ID_ANY, '&Preferences')
        editMenu.AppendItem(mPreferences)
        self.Bind(wx.EVT_MENU,self.OnPreferences,mPreferences)     
        
        # Defining the help menu
        helpMenu = wx.Menu()
        mAbout = wx.MenuItem(helpMenu, wx.ID_ABOUT, '&About')
        helpMenu.AppendItem(mAbout)
        self.Bind(wx.EVT_MENU, self.OnAbout, mAbout)
         
        # Applying menus to the menu bar
        menubar.Append(fileMenu, '&File')
        menubar.Append(editMenu, '&Edit')
        menubar.Append(helpMenu,'&Help')


        self.SetMenuBar(menubar)


        # Here we create a notebook on the panel
        nb = wx.Notebook(self.panel)

        # create the page windows as children of the notebook
        self.page1 = FrontPage.Fpanel(nb)
        self.page2 = CatchmentDescriptors.Fpanel(nb,self.page1)
        self.page3 = QMED.Fpanel(nb,self.page2)
        #self.page4 = GrowthCurve.PoolingPanel(nb,self.page2,self.page3)
        self.page4 = GrowthCurve.MainPanel(nb,self.page2,self.page3)
        self.page5 = Summary.Fpanel(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(self.page1, "Overview")
        nb.AddPage(self.page2, "CDS")
        nb.AddPage(self.page3, "QMED")
        nb.AddPage(self.page4, "FGC")
        nb.AddPage(self.page5, "Summary")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)
        
        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        

        self.panel.Layout()
        self.Layout()
        self.Refresh()
    
    def OnPageChanging(self,e):
      #self.Refresh()
      #self.Update()
      e.Skip()
      
    def OnPageChanged(self,e):
      #self.page2.title_label.SetLabel(str(self.page1.title.GetValue()))
      #self.Refresh()
      #self.Update()
      e.Skip() 
        
    '''def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " FEH application tool \n developed in wxPython \n \n Prepare by Neil Nutt \n without warranty\n\n Visit wiki at https://github.com/OpenHydrology/StatisticalFloodEstimationTool/wiki", "FEH application tool", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.
'''

    def OnAbout(self, e):
        
        description = """        The Statistical Flood Estimation Tool is a means of implementing current statistical
        procedures for estimating the magnitude of flood flows in the United Kingdom using the methods 
        detailed in the Flood Estimation Handbook and subsequent updates.  This is an early development
        version, it is intended that additional features will be implemented in the coming months and years.
"""

        licence = """The Statistical Flood Estimation Tool is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

The Statistical Flood Estimation Tool is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA

EXCEPTION CLAUSE:

A. Organisations (commercial, academic, educational, private individual or
  any other body) must publicly state via this software project's website
  that they have undertaken a validation process of this software prior to 
  its use.  In submitting their public declaration, organisations should 
  provide details of the findings of their review including any caveats or
  exclusions of use.  Organisations must record errors or bugs they find within
  the software project's issue reporting system. This exclusion of use permits 
  reasonable use of the software by organisations for testing and validation.
  
  Software project website:
  https://github.com/OpenHydrology/StatisticalFloodEstimationTool/wiki


"""



        info = wx.AboutDialogInfo()

        #info.SetIcon(wx.Icon('icon.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Statistical Flood Estimation Tool')
        info.SetVersion('Pre-release 0.0.1')
        info.SetDescription(description)
        info.SetCopyright('(C) 2014 Neil Nutt')
        info.SetWebSite('https://github.com/OpenHydrology/StatisticalFloodEstimationTool')
        info.SetLicence(licence)
        info.AddDeveloper('Neil Nutt neilnutt{at]googlemail[dot]com')

        wx.AboutBox(info)

    def OnPreferences(self,e):
      '''
      Load up preferences screen
      '''
      import Preferences
      
      Preferences.PreferencesFrame(self).Show()

      self.Refresh()
      self.Update()   


    def OnFileOpen(self, e):
        """ File|Open event - Open dialog box. """
        dlg = wx.FileDialog(self, "Open", self.dirName, self.fileName,
                           "Text Files (*.hyd)|*.hyd|All Files|*.*", wx.OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()

            import shelve
            
            shelveObject=shelve.open(os.path.join(self.dirName, self.fileName))
            for key in shelveObject:
              globals()[key]=shelveObject[key]
            shelveObject.close()

            ### - this will read in Unicode files (since I'm using Unicode wxPython
            #if self.rtb.LoadFile(os.path.join(self.dirName, self.fileName)):
            #    self.SetStatusText("Opened file: " + str(self.rtb.GetLastPosition()) + 
            #                       " characters.", SB_INFO)
            #    self.ShowPos()
            #else:
            #    self.SetStatusText("Error in opening file.", SB_INFO)

            ### - but we want just plain ASCII files, so:
            #try:
                #f = file(os.path.join(self.dirName, self.fileName), 'r')
                #self.page1.title.SetValue(f.read())
                #self.SetTitle(self.page1.title)
                #self.SetStatusText("Opened file: " + str(self.title.GetLastPosition()) +" characters.", SB_INFO)
                #self.ShowPos()
                #f.close()
            #except:
                #print "Failed"
                #self.PushStatusText("Error in opening file.", SB_INFO)
        dlg.Destroy()

#---------------------------------------
    def OnFileSave(self, e):
        """ File|Save event - Just Save it if it's got a name. """
        import shelve
        if (self.fileName != "") and (self.dirName != ""):
            #try:
                shelveObject = shelve.open(os.path.join(self.dirName, self.fileName),'n')
                for key in dir():
                  try:
                    shelveObject[key] = globals()[key]
                  except:
                    pass # __builtins__ and shelveObject cannot be shelved
                shelveObject.close()
                #f = file(os.path.join(self.dirName, self.fileName), 'w')
                #f.write(self.page1.title.GetValue())
                #self.PushStatusText("Saved file: " + str(self.rtb.GetLastPosition()) + " characters.", SB_INFO)
                #f.close()
                #return True
            #except:
                #self.PushStatusText("Error in saving file.", SB_INFO)
                #print "Save failed"
                #pass
                
                #return False
        else:
            ### - If no name yet, then use the OnFileSaveAs to get name/directory
            return self.OnFileSaveAs(e)

#---------------------------------------
    def OnFileSaveAs(self, e):
        """ File|SaveAs event - Prompt for File Name. """
        ret = False
        dlg = wx.FileDialog(self, "Save As", self.dirName, self.fileName,
                           "Text Files (*.hyd)|*.hyd|All Files|*.*", wx.SAVE)
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            ### - Use the OnFileSave to save the file
            if self.OnFileSave(e):
                self.SetTitle(self.page1.title.GetValue())
                ret = True
        dlg.Destroy()
        return ret

    def OnNew(self,e):
      pass

    #def RandomNumber(self,e):
     # self.st1.SetLabel(str(time.time()))
          
        
        
    def OnQuit(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()



if __name__ == "__main__":
    app = wx.App(redirect=False)
    #app = wx.App(redirect=True,filename='error_log.txt')
    MainFrame(None).Show()
    app.MainLoop()
