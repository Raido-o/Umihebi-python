from unicodedata import east_asian_width
import colorama
from colorama import Fore
from colorama import Style

colorama.init()

def printWarning(warningMessage):
    print(Fore.YELLOW + Style.BRIGHT + '\n[Warning] ' + Style.RESET_ALL + warningMessage)

def bindAllChildren(widget, sequence, func):
    widget.bind(sequence, func)
    for child in widget.winfo_children():
        bindAllChildren(child, sequence, func)

def getEastAsianWidthCount(eastAsianText):
    '''
    文字列の長さを測る
    len()と違い全角文字は2文字としてカウントされる

    Parameters
    ----------
    eastAsianText : str
        長さを測る文字列

    Returns
    -------
    count : int
        文字列の長さ
    '''
    count = 0
    for char in eastAsianText:
        if east_asian_width(char) in 'FWA':
            count += 2
        else:
            count += 1
    return count

def cloneWidget(widget, master=None):
    """
    Create a cloned version o a widget

    Parameters
    ----------
    widget : tkinter widget
        tkinter widget that shall be cloned.
    master : tkinter widget, optional
        Master widget onto which cloned widget shall be placed. If None, same master of input widget will be used. The
        default is None.

    Returns
    -------
    cloned : tkinter widget
        Clone of input widget onto master widget.

    """
    # Get main info
    parent = master if master else widget.master
    cls = widget.__class__

    # Clone the widget configuration
    cfg = {key: widget.cget(key) for key in widget.configure()}
    cloned = cls(parent, **cfg)

    # Clone the widget's children
    for child in widget.winfo_children():
        child_cloned = cloneWidget(child, master=cloned)
        if child.grid_info():
            grid_info = {k: v for k, v in child.grid_info().items() if k not in {'in'}}
            child_cloned.grid(**grid_info)
        elif child.place_info():
            place_info = {k: v for k, v in child.place_info().items() if k not in {'in'}}
            child_cloned.place(**place_info)
        else:
            pack_info = {k: v for k, v in child.pack_info().items() if k not in {'in'}}
            child_cloned.pack(**pack_info)

    return cloned
