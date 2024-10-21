import traceback
from types import TracebackType
from gui import QCMainWindow
from qtpy.QtWidgets import QApplication
import sys


def _our_excepthook(
    type: type[BaseException], value: BaseException, tb: TracebackType | None
) -> None:
    """Excepthook that prints the traceback to the console.

    By default, Qt's excepthook raises sys.exit(), which is not what we want.
    """
    # this could be elaborated to do all kinds of things...
    traceback.print_exception(type, value, tb)


if __name__ == "__main__":
    app = QApplication([])
    window = QCMainWindow()
    window.show()
    # this is to avoid the application crashing. if an error occurs, it will be printed
    # to the console instead.
    sys.excepthook = _our_excepthook
    app.exec()