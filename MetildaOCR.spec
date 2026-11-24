# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = []
binaries = []
hiddenimports = []
datas += copy_metadata('Jinja2')
datas += copy_metadata('MarkupSafe')
datas += copy_metadata('PyYAML')
datas += copy_metadata('Pygments')
datas += copy_metadata('aiohappyeyeballs')
datas += copy_metadata('aiohttp')
datas += copy_metadata('aiosignal')
datas += copy_metadata('aistudio_sdk')
datas += copy_metadata('altgraph')
datas += copy_metadata('annotated-doc')
datas += copy_metadata('annotated-types')
datas += copy_metadata('anyio')
datas += copy_metadata('attrs')
datas += copy_metadata('bce-python-sdk')
datas += copy_metadata('certifi')
datas += copy_metadata('cffi')
datas += copy_metadata('chardet')
datas += copy_metadata('charset-normalizer')
datas += copy_metadata('click')
datas += copy_metadata('colorama')
datas += copy_metadata('colorlog')
datas += copy_metadata('crc32c')
datas += copy_metadata('cryptography')
datas += copy_metadata('customtkinter')
datas += copy_metadata('darkdetect')
datas += copy_metadata('filelock')
datas += copy_metadata('flatbuffers')
datas += copy_metadata('frozenlist')
datas += copy_metadata('fsspec')
datas += copy_metadata('future')
datas += copy_metadata('h11')
datas += copy_metadata('hf-xet')
datas += copy_metadata('httpcore2')
datas += copy_metadata('httpx2')
datas += copy_metadata('huggingface_hub')
datas += copy_metadata('idna')
datas += copy_metadata('imagesize')
datas += copy_metadata('markdown-it-py')
datas += copy_metadata('mdurl')
datas += copy_metadata('modelscope')
datas += copy_metadata('modelscope-hub')
datas += copy_metadata('mpmath')
datas += copy_metadata('multidict')
datas += copy_metadata('networkx')
datas += copy_metadata('numpy')
datas += copy_metadata('onnxruntime')
datas += copy_metadata('opencv-contrib-python')
datas += copy_metadata('packaging')
datas += copy_metadata('paddleocr')
datas += copy_metadata('paddlex')
datas += copy_metadata('pandas')
datas += copy_metadata('pefile')
datas += copy_metadata('pillow')
datas += copy_metadata('pip')
datas += copy_metadata('prettytable')
datas += copy_metadata('propcache')
datas += copy_metadata('protobuf')
datas += copy_metadata('psutil')
datas += copy_metadata('py-cpuinfo')
datas += copy_metadata('pyclipper')
datas += copy_metadata('pycparser')
datas += copy_metadata('pycryptodome')
datas += copy_metadata('pydantic')
datas += copy_metadata('pydantic_core')
datas += copy_metadata('pyinstaller')
datas += copy_metadata('pyinstaller-hooks-contrib')
datas += copy_metadata('pymupdf')
datas += copy_metadata('pymupdf4llm')
datas += copy_metadata('pymupdf_layout')
datas += copy_metadata('pypdfium2')
datas += copy_metadata('python-bidi')
datas += copy_metadata('python-dateutil')
datas += copy_metadata('pywin32-ctypes')
datas += copy_metadata('regex')
datas += copy_metadata('requests')
datas += copy_metadata('rich')
datas += copy_metadata('ruamel.yaml')
datas += copy_metadata('safetensors')
datas += copy_metadata('setuptools')
datas += copy_metadata('shapely')
datas += copy_metadata('shellingham')
datas += copy_metadata('six')
datas += copy_metadata('sympy')
datas += copy_metadata('tabulate')
datas += copy_metadata('tokenizers')
datas += copy_metadata('torch')
datas += copy_metadata('torchvision')
datas += copy_metadata('tqdm')
datas += copy_metadata('transformers')
datas += copy_metadata('truststore')
datas += copy_metadata('typer')
datas += copy_metadata('typing-inspection')
datas += copy_metadata('typing_extensions')
datas += copy_metadata('tzdata')
datas += copy_metadata('ujson')
datas += copy_metadata('urllib3')
datas += copy_metadata('wcwidth')
datas += copy_metadata('yarl')
hiddenimports += collect_submodules('transformers')
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('paddleocr')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('paddlex')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MetildaOCR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MetildaOCR',
)
