import os
import sys
import tempfile

def setup_environment():
    # 获取应用程序的基础路径
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    # 设置ImageMagick环境
    magick_home = os.path.join(application_path, 'imagemagick')
    os.environ['MAGICK_HOME'] = magick_home
    os.environ['PATH'] = magick_home + os.pathsep + os.environ.get('PATH', '')

    # 创建本地临时目录
    temp_dir = os.path.join(application_path, 'Temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # 设置临时目录环境变量
    os.environ['TMP'] = temp_dir
    os.environ['TEMP'] = temp_dir
    os.environ['TMPDIR'] = temp_dir
    os.environ['MAGICK_TEMPORARY_PATH'] = temp_dir
    os.environ['MAGICK_TMPDIR'] = temp_dir
    tempfile.tempdir = temp_dir

    # 创建ImageMagick配置目录
    if not os.path.exists(magick_home):
        os.makedirs(magick_home)

    # 创建delegates.xml
    delegates_path = os.path.join(magick_home, 'delegates.xml')
    if not os.path.exists(delegates_path):
        with open(delegates_path, 'w', encoding='utf-8') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<delegatemap>
  <delegate decode="dds" command="convert &quot;%i&quot; &quot;%o&quot;"/>
  <delegate decode="tga" command="convert &quot;%i&quot; &quot;%o&quot;"/>
</delegatemap>''')

    # 创建policy.xml
    policy_path = os.path.join(magick_home, 'policy.xml')
    if not os.path.exists(policy_path):
        with open(policy_path, 'w', encoding='utf-8') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<policymap>
  <policy domain="coder" rights="read|write" pattern="TGA" />
  <policy domain="coder" rights="read|write" pattern="DDS" />
  <policy domain="coder" rights="read|write" pattern="*" />
  <policy domain="resource" name="temporary-path" value="%s" />
</policymap>''' % temp_dir.replace('\\', '/'))

    # 创建magic.xml
    magic_path = os.path.join(magick_home, 'magic.xml')
    if not os.path.exists(magic_path):
        with open(magic_path, 'w', encoding='utf-8') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<magicmap>
  <magic name="TGA" offset="0" target="0x0,0x0,0x2,0x0,0x0,0x0,0x0,0x0"/>
  <magic name="DDS" offset="0" target="44 44 53 20"/>
</magicmap>''')

    # 设置环境变量
    os.environ['MAGICK_CONFIGURE_PATH'] = magick_home
    os.environ['MAGICK_CODER_MODULE_PATH'] = magick_home

    # 设置Python环境
    if not os.environ.get('PYTHONPATH'):
        os.environ['PYTHONPATH'] = application_path
    else:
        os.environ['PYTHONPATH'] = application_path + os.pathsep + os.environ['PYTHONPATH']

setup_environment() 