
import winlib
import renmas.gui 

win = renmas.gui.MainWindow(500, 500, "Test")
win.redraw()

win2 = renmas.gui.MainWindow(400, 400, "Another Window")
win2.redraw()

winlib.MainLoop()

