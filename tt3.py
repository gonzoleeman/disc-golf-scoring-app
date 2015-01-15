#!/usr/bin/python
'''
Test Test 2
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
        self.SetInitialSize((200, 20))
        self.SetBackgroundColour('GREEN')


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

        labelColour = 'BLUE'

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
        st1 = LabelStaticText(panel, label='Label Field 1')
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        lcont.Add(hbox1, flag=wx.RIGHT|wx.ALIGN_RIGHT, border=0)

        lcont.AddSpacer(10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = LabelStaticText(panel, label='Longer Label Field 2')
        hbox2.Add(st2, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        lcont.Add(hbox2, flag=wx.RIGHT|wx.ALIGN_RIGHT, border=0)

        lcont.AddSpacer(10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = LabelStaticText(panel, label='And Field 3')
        hbox3.Add(st3, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        lcont.Add(hbox3, flag=wx.RIGHT|wx.ALIGN_RIGHT, border=0)

        ### now set up right side ####

        rcont.AddSpacer(10)

        tc1 = ValueTextCtrl(panel,
#                            size=(250, 20),
                            value='Try1 -- this line can be quite long')
        rcont.Add(tc1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        
        rcont.AddSpacer(10)

        tc2 = ValueTextCtrl(panel,
#                            size=(200, 20),
                            value='Try2 -- this line, too, dude!')
        rcont.Add(tc2, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        rcont.AddSpacer(10)
        
        tc3 = ValueTextCtrl(panel,
#                            size=(350, 20),
                            value='Try3 -- Just a shorty')
        rcont.Add(tc3, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)

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
