import ctypes
SPI_SETDESKWALLPAPER = 20
ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, "D:\HiDT_application\images\daytime\content\Test2.jpg", 0)