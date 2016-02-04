#!/usr/bin/python
'''
Test Test 4
'''

import sys
import wx


class BitmapPanel(wx.Panel):
    """
    class BitmapPanel creates a panel with an image on it, inherits wx.Panel
    """
    def __init__(self, parent, id):
        # create the panel
        wx.Panel.__init__(self, parent, id)
        try:
            imageFile = 'Test.jpg'
	    self.img = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

            # bitmap upper left corner is in the position tuple (x, y) = (5, 5)
	    wx.StaticBitmap(self, -1, self.img, (5, 5),
                            (self.img.GetWidth(), self.img.GetHeight()))
        except IOError:
            print "Image file %s not found" % imageFile
            raise SystemExit

    def getSize(self):
        '''Return Bitmap size'''
        return (self.img.GetWidth(), self.img.GetHeight())


class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TestFrame, self).__init__(*args, **kwargs)
        self.InitUI()

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the test GUI
        '''
        panel = BitmapPanel(self, -1)
        (img_x, img_y) = panel.getSize()
        self.SetSize((img_x + 10, img_y + 10))

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


def main():
    app = wx.App()
    TestFrame(None, title='Test Frame')
    app.MainLoop()


if __name__ == '__main__':
    main()
