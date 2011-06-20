
import ctypes
import win32con

from ctypes import windll
c_long = ctypes.c_long
c_int = ctypes.c_int
c_uint = ctypes.c_uint
c_wchar = ctypes.c_wchar
c_wchar_p = ctypes.c_wchar_p

kernel32 = windll.kernel32
user32 = windll.user32


WNDPROC = ctypes.WINFUNCTYPE(c_long, c_int, c_uint, c_int, c_int)
NULL = 0
MsgBox = user32.MessageBoxW

CreateWindowEx = user32.CreateWindowExW
CreateWindowEx.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int]

def ErrorIfZero(handle):
    if handle == 0:
        raise ctypes.WinError
    else:
        return handle
CreateWindowEx.restype = ErrorIfZero



class RECT(ctypes.Structure):
    _fields_ = [('left', c_long),
                ('top', c_long),
                ('right', c_long),
                ('bottom', c_long)]
    def __init__(self, left=0, top=0, right=0, bottom=0 ):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [('hdc', c_int),
                ('fErase', c_int),
                ('rcPaint', RECT),
                ('fRestore', c_int),
                ('fIncUpdate', c_int),
                ('rgbReserved', c_wchar * 32)]

class POINT(ctypes.Structure):
    _fields_ = [('x', c_long),
                ('y', c_long)]
    def __init__( self, x=0, y=0 ):
        self.x = x
        self.y = y

class MSG(ctypes.Structure):
    _fields_ = [('hwnd', c_int),
                ('message', c_uint),
                ('wParam', c_int),
                ('lParam', c_int),
                ('time', c_int),
                ('pt', POINT)]

def MessageBox(caption, text, keys=None):
    result = MsgBox(None, text, caption, 0)
    return result

class WNDCLASS(ctypes.Structure):
    _fields_ = [('style', c_uint),
                ('lpfnWndProc', WNDPROC),
                ('cbClsExtra', c_int),
                ('cbWndExtra', c_int),
                ('hInstance', c_int),
                ('hIcon', c_int),
                ('hCursor', c_int),
                ('hbrBackground', c_int),
                ('lpszMenuName', c_wchar_p),
                ('lpszClassName', c_wchar_p)]

    def __init__(self,
                 wndProc,
                 style=win32con.CS_HREDRAW | win32con.CS_VREDRAW,
                 clsExtra=0,
                 wndExtra=0,
                 menuName=None,
                 className="PythonWin32",
                 instance=None,
                 icon=None,
                 cursor=None,
                 background=None,
                 ):

        if not instance:
            instance = windll.kernel32.GetModuleHandleW(c_int(win32con.NULL))
        if not icon:
            icon = user32.LoadIconW(c_int(win32con.NULL),
                                     c_int(win32con.IDI_APPLICATION))
        if not cursor:
            cursor = user32.LoadCursorW(c_int(win32con.NULL),
                                         c_int(win32con.IDC_ARROW))
        if not background:
            background = windll.gdi32.GetStockObject(c_int(win32con.WHITE_BRUSH))

        self.lpfnWndProc=wndProc
        self.style=style
        self.cbClsExtra=clsExtra
        self.cbWndExtra=wndExtra
        self.hInstance=instance
        self.hIcon=icon
        self.hCursor=cursor
        self.hbrBackground=background
        self.lpszMenuName=menuName
        self.lpszClassName=className


def pump_messages():
    """Calls message loop"""
    msg = MSG()
    pMsg = pointer(msg)

    while user32.GetMessageW(pMsg, None, 0, 0):
        user32.TranslateMessage(pMsg)
        user32.DispatchMessageW(pMsg)

    return msg.wParam

