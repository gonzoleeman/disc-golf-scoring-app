#!/usr/bin/python
'''
Test Test 1
'''

import sys
import wx



class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TestFrame, self).__init__(*args, **kwargs)
        self.SetSize((400, 200))
        self.InitUI()

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the test GUI
        '''
        panel = wx.Panel(self)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(10)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.AddSpacer(10)
        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='This static text is Centered')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)

        vbox.AddSpacer(10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='This static text is Left-Justified')
        st2.SetFont(font)
        hbox2.Add(st2, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox2, flag=wx.LEFT|wx.ALIGN_LEFT)

        vbox.AddSpacer(10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel,
                            label='This static text is Right-Justified ??')
        st2.SetFont(font)
        hbox3.Add(st2, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox3, flag=wx.RIGHT|wx.ALIGN_RIGHT)

        panel.SetSizer(vbox)

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        print "DEBUG: Test GUI Initialized"



def main():
    app = wx.App()
    TestFrame(None, title='Test Frame')
    app.MainLoop()


if __name__ == '__main__':
    main()
