'''
Created on 27 Apr 2014

@author: NUT67271
'''
import wx

class Fpanel(wx.Panel):
    def __init__(self, parent):
      wx.Panel.__init__(self, parent)
      t = wx.StaticText(self, -1, "This is where the results are summarised", (20,20))