#!/usr/bin/python
"""
This is from http://wiki.wxpython.org/Printing

License: MIT
"""

import wx
from wx import Printer as wxPrinter

from opts import opts
from utils import dprint


def GetErrorText():
    """
    Put your error text logic here.
    See Python Cookbook for a useful example of error text.
    """
    return 'Some error occurred.'

class MyPrintout(wx.Printout):
    def __init__(self, frame, lines=[]):
        """
        Prepares the Printing object.
        Note: change current_y for 1, 1.5, 2 spacing for lines.
        """
        wx.Printout.__init__(self)
        self.printer_config = wx.PrintData()
        self.printer_config.SetPaperId(wx.PAPER_LETTER)
        self.printer_config.SetOrientation(wx.LANDSCAPE)
        self.frame = frame
        self.doc_lines = lines
        self.doc_name = ''
        self.current_y = 15           # y should be either (15, 22, 30)
        if self.current_y == 15:
            self.num_lines_per_page = 50
        elif self.current_y == 22:
            self.num_lines_per_page = 35
        else:
            self.num_lines_per_page = 25

    def PrintText(self, lines, doc_name):
        """
        Prints the given lines.
        Currently doc_name logic doesn't exist.
        E.g. might be useful for a footer.
        """
        dprint("Print has been called. Lines passed in:")
        self.doc_lines = lines
        #for line in self.doc_lines:
        #    dprint("/%s/" % line)
        self.doc_name = doc_name
        pdd = wx.PrintDialogData()
        pdd.SetPrintData(self.printer_config)
        printer = wx.Printer(pdd)
        if not printer.Print(self.frame, self, prompt=True):
            wx.MessageBox("Unable to print the document.")
        else:
            # save possibly-updated printer config for next use, if any
            self.printer_config = printer.GetPrintDialogData().GetPrintData()

    def PreviewText(self, lines, doc_name):
        """
        This function displays the preview window for the text with the given header.
        """
        try:
            self.doc_name = doc_name
            self.doc_lines = lines

            #Destructor fix by Peter Milliken --
            print1 = MyPrintout(self.frame, lines=self.doc_lines)
            print2 = MyPrintout(self.frame, lines=self.doc_lines)
            preview = wx.PrintPreview(print1, print2, self.printer_config)
            if not preview.Ok():
                wx.MessageBox("Unable to display preview of document.")
                return
            preview_window = wx.PreviewFrame(preview, self.frame, \
                                             "Print Preview - %s" % doc_name)
            preview_window.Initialize()
            preview_window.SetPosition(self.frame.GetPosition())
            preview_window.SetSize(self.frame.GetSize())
            preview_window.MakeModal(True)
            preview_window.GetControlBar().SetZoomControl(100)
            preview_window.Show(True)
        except Exception, e:
            dprint("oh oh -- something failed:", e)
            wx.MessageBox(GetErrorText())

    def PageSetup(self):
        """
        This function handles displaying the Page Setup window
        and retrieving the user selected options.
        """
        dprint("PageSetup")
        config_dialog = wx.PrintDialog(self.frame)
        #config_dialog.GetPrintDialogData().SetPrintData(self.printer_config)
        #config_dialog.GetPrintDialogData().SetSetupDialog(True)
        config_dialog.ShowModal()
        #self.printer_config = config_dialog.GetPrintDialogData().GetPrintData()
        config_dialog.Destroy()

    def OnBeginDocument(self, start, end):
        """Do any end of document logic here."""
        dprint("OnBeginDocument(%s, %s)" % (start, end))
        self.base_OnBeginDocument(start,end)

    def OnEndDocument(self):
        """Do any end of document logic here."""
        dprint("OnEndDocument")
        self.base_OnEndDocument()

    def OnBeginPrinting(self):
        """Do printing initialization logic here."""
        dprint("OnBeginPrinting")
        self.base_OnBeginPrinting()

    def OnEndPrinting(self):
        """Do any post printing logic here."""
        dprint("OnEndPrinting")
        self.base_OnEndPrinting()

    def OnPreparePrinting(self):
        """Do any logic to prepare for printing here."""
        dprint("OnPreparePrinting: preview=%s" % self.IsPreview())
        self.base_OnPreparePrinting()

    def HasPage(self, page_num):
        """
        This function is called to determine if the specified page exists.
        """
        res = len(self.GetPageText(page_num))
        dprint("HasPage(%d): returning '%d > 0'" % (page_num, res))
        return res > 0

    def GetPageInfo(self):
        """
        This returns the page information: what is the page range available,
        and what is the selected page range.
        Currently the selected page range is always the available page range.
        This logic should be changed if you need
        greater flexibility.
        """
        minPage = 1
        maxPage = int(len(self.doc_lines) / self.num_lines_per_page) + 1
        fromPage, toPage = minPage, maxPage
        dprint("GetPageInfo: returning (%d,%d,%d,%d)" % \
               (minPage,maxPage,fromPage,toPage))
        return (minPage,maxPage,fromPage,toPage)

    def OnPrintPage(self, page_num):
        """
        This function / event is executed for each page that needs to be printed.
        """
        dprint("Print Page %d" % page_num)
        dc = self.GetDC()
        if self.IsPreview():
            dc_ppi = self.GetPPIScreen()[0]
            w_px = dc.GetSizeTuple()[0]
        else:
            dc_ppi = self.GetPPIPrinter()[0]
            w_px = self.GetPageSizePixels()[0]
        w_mm = self.GetPageSizeMM()[0]
        my_fs = 30 # desirable font size in points (1/72 of inch)
        mpi = 25.4
        # calulcate proper font size
        fs = round((my_fs * w_px * mpi) / (w_mm * dc_ppi))
        dprint("Calulcated font size (preview=%s): %d" % (self.IsPreview(), fs))
        dc.SetFont(wx.Font(fs, wx.MODERN, wx.NORMAL, wx.NORMAL, False,
                           'Courier New'))
        if self.IsPreview():
            col_offset_pts = 25
            line_spacing_pts = self.current_y
            line_offset_pts = 50
        else:
            col_offset_pts = 75
            line_spacing_pts = self.current_y * 4
            line_offset_pts = 50
        # draw each line of text
        # column offset stays the same, line offset increases
        x, y = col_offset_pts, line_offset_pts
        for line in self.GetPageText(page_num):
            dprint("Drawing line at (%d, %d): /%s/" % (x, y, line))
            dc.DrawText(line, x, y)
            y += line_spacing_pts
        return True

    def GetPageText(self, page_num):
        """
        This function returns the text to be displayed for the given page number.
        """
        dprint("Get Page Text %d" % page_num)
        start_idx = (page_num - 1) * self.num_lines_per_page
        end_idx = page_num * (self.num_lines_per_page - 1)
        lines_for_page = self.doc_lines[start_idx:end_idx]
        dprint("GetPageText: returning %d lines" % len(lines_for_page))
        #for line in lines_for_page:
        #    dprint("line: /%s/" % line)
        return lines_for_page
