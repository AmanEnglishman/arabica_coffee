import logging
from escpos.printer import Network

logger = logging.getLogger("printer")


def print_receipt(ip: str, port: int, text: str) -> None:
    p = Network(ip, port=port, timeout=5)
    try:
        # Encode Cyrillic: cp866 (DOS Cyrillic) works with most ESC/POS printers
        p.charcode("CP866")
        for line in text.split("\n"):
            try:
                p._raw(line.encode("cp866", errors="replace") + b"\n")
            except Exception:
                p._raw(line.encode("ascii", errors="replace") + b"\n")
        p.cut()
    finally:
        p.close()
