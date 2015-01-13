#!/usr/bin/python
'''
Test Test 2
'''

import sys
import wx



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

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        lbox = wx.BoxSizer(wx.VERTICAL)
        rbox = wx.BoxSizer(wx.VERTICAL)

        lcont = lbox
        rcont = rbox

        hbox.Add(lcont, flag=wx.TOP|wx.LEFT|wx.BOTTOM)
        hbox.Add(rcont, flag=wx.TOP|wx.RIGHT|wx.BOTTOM)

        ### set up left box ###

        lcont.AddSpacer(10)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Label Field 1',
                            style=wx.DOUBLE_BORDER)
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        lcont.Add(hbox1, flag=wx.RIGHT|wx.ALIGN_RIGHT)

        lcont.AddSpacer(10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Longer Label Field 2')
        st2.SetFont(font)
        hbox2.Add(st2, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        lcont.Add(hbox2, flag=wx.RIGHT|wx.ALIGN_RIGHT)

        lcont.AddSpacer(10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label='And Field 3')
        st3.SetFont(font)
        hbox3.Add(st3, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        lcont.Add(hbox3, flag=wx.RIGHT|wx.ALIGN_RIGHT)

        ### now set up right side ####

        rcont.AddSpacer(10)

        st4 = wx.StaticText(panel, label='Try1 -- this line can be quite long')
        st4.SetFont(font)

        rcont.Add(st4, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        rcont.AddSpacer(10)

        st5 = wx.StaticText(panel, label='Try2 -- this line, too, dude!')
        st5.SetFont(font)

        rcont.Add(st5, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        rcont.AddSpacer(10)

        st6 = wx.StaticText(panel, label='Try3 -- Just a shorty')
        st6.SetFont(font)

        rcont.Add(st6, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        ### set size for our panel to top-level box ###
        
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
