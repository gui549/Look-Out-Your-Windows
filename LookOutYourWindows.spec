# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['WindowsGui.py'],
             pathex=['c:\\Users\\user\\Desktop\\HiDT\\Look-Out-Your-Windows\\venv\\Lib\\site-packages', 'C:\\Users\\user\\Desktop\\HiDT\\Look-Out-Your-Windows'],
             binaries=[('icon.ico', '.'), ('images/styles/morning.jpg', 'image/styles'), ('images/styles/afternoon.jpg', 'image/styles'), ('images/styles/evening.jpg', 'image/styles'), ('images/styles/night.jpg', 'image/styles')],
             datas=[('GUI/MainGui.ui', 'GUI'), ('GUI/SaveGui.ui', 'GUI'), ('configs/daytime.yaml', 'config'), ('trained_models/enhancer/enhancer.pth', 'trained_models/enhancer'), ('trained_models/generator/daytime.pt', 'trained_models/generator')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='LookOutYourWindows',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='LookOutYourWindows')
