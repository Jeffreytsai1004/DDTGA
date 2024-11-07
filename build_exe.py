import PyInstaller.__main__
import sys
import os
from PIL import Image

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取site-packages路径
site_packages = os.path.join(current_dir, 'python', 'Lib', 'site-packages')
ctk_path = os.path.join(site_packages, 'customtkinter')

# 转换图标
icon_path = os.path.join(current_dir, 'icon', 'logo.png')
if os.path.exists(icon_path):
    ico_path = os.path.join(current_dir, 'icon', 'logo.ico')
    if not os.path.exists(ico_path):
        # 使用PIL转换PNG为ICO
        img = Image.open(icon_path)
        img.save(ico_path, format='ICO')
else:
    ico_path = None

# ImageMagick配置
imagemagick_dlls = []
if os.path.exists(os.path.join(current_dir, 'imagemagick')):
    for file in os.listdir(os.path.join(current_dir, 'imagemagick')):
        if file.endswith('.dll'):
            src = os.path.join(current_dir, 'imagemagick', file)
            dst = os.path.join('imagemagick', file)
            imagemagick_dlls.append((src, dst))

# 创建ImageMagick配置文件
imagemagick_dir = os.path.join(current_dir, 'imagemagick')
if not os.path.exists(imagemagick_dir):
    os.makedirs(imagemagick_dir)

# 创建delegates.xml
with open(os.path.join(imagemagick_dir, 'delegates.xml'), 'w', encoding='utf-8') as f:
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<delegatemap>
  <delegate decode="dds" command="convert &quot;%i&quot; &quot;%o&quot;"/>
  <delegate decode="tga" command="convert &quot;%i&quot; &quot;%o&quot;"/>
</delegatemap>''')

# 创建policy.xml
with open(os.path.join(imagemagick_dir, 'policy.xml'), 'w', encoding='utf-8') as f:
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<policymap>
  <policy domain="coder" rights="read|write" pattern="TGA" />
  <policy domain="coder" rights="read|write" pattern="DDS" />
  <policy domain="coder" rights="read|write" pattern="*" />
</policymap>''')

# 创建magic.xml
with open(os.path.join(imagemagick_dir, 'magic.xml'), 'w', encoding='utf-8') as f:
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<magicmap>
  <magic name="TGA" offset="0" target="0x0,0x0,0x2,0x0,0x0,0x0,0x0,0x0"/>
  <magic name="DDS" offset="0" target="44 44 53 20"/>
</magicmap>''')

# 添加配置文件到打包列表
imagemagick_configs = [
    ('delegates.xml', 'imagemagick'),
    ('policy.xml', 'imagemagick'),
    ('magic.xml', 'imagemagick')
]

# 构建PyInstaller参数
pyinstaller_args = [
    os.path.join(current_dir, 'image_converter.py'),
    '--noconfirm',
    '--windowed',
    '--onefile',
    '--name', 'DDSTGA',
    '--add-data', f'{ctk_path};customtkinter/',
    '--add-data', f'{os.path.join(site_packages, "customtkinter")};customtkinter/',
    *[f'--add-binary={src};{dst}' for src, dst in imagemagick_dlls],
    '--collect-all', 'customtkinter',
    '--collect-all', 'tkinter',
    '--collect-all', 'PIL',
    '--collect-all', 'wand',
    '--hidden-import', 'customtkinter',
    '--hidden-import', 'tkinter',
    '--hidden-import', 'PIL._tkinter_finder',
    '--hidden-import', 'wand.api',
    '--hidden-import', 'pkg_resources.py2_warn',
    '--runtime-hook', os.path.join(current_dir, 'runtime_hook.py'),
    '--distpath', os.path.join(current_dir, 'dist'),
    '--workpath', os.path.join(current_dir, 'build'),
    '--specpath', current_dir,
    '--noupx',
    '--clean',
    *[f'--add-data={os.path.join(current_dir, "imagemagick", src)};{dst}' for src, dst in imagemagick_configs],
]

# 如果有图标，添加图标参数
if ico_path and os.path.exists(ico_path):
    pyinstaller_args.extend(['--icon', ico_path])

PyInstaller.__main__.run(pyinstaller_args) 