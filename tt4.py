#!/usr/bin/python
'''
Test Test 4
'''

import sys
import wx



class LabelStaticText(wx.StaticText):
    def __init__(self, *args, **kwargs):
        super(LabelStaticText, self).__init__(*args, **kwargs)
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(10)
        self.SetFont(font)
        self.SetForegroundColour('BLUE')


class ValueTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super(ValueTextCtrl, self).__init__(*args, **kwargs)
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(10)
        self.SetFont(font)
        #self.SetInitialSize((200, 20))
        #self.SetBackgroundColour(wx.Colour(200,175,120))


class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TestFrame, self).__init__(*args, **kwargs)
        self.SetSize((500, 200))
        self.InitUI()

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the test GUI
        '''
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)

        
        panel.SetSizer(hbox)


    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


def main():
    app = wx.App()
    TestFrame(None, title='Test Frame')
    app.MainLoop()


if __name__ == '__main__':
    main()
