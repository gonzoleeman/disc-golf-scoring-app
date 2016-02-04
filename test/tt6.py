#!/usr/bin/python
'''
Test Test 6
'''

import sys
import wx


class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TestFrame, self).__init__(*args, **kwargs)
        self.InitUI()

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the test GUI
        '''
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        button1 = wx.Button(panel, label='Button 1')
        button2 = wx.Button(panel, label='Button 2')

        hbox.Add(button1)
        hbox.AddStretchSpacer(2)
        hbox.Add(button2)

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
