import os
import shutil
import platform

app = 'transit_simulator'
system = platform.system()

excecutable = {'Darwin': 'command', 'Linux': 'sh', 'Windows': 'cmd'}

current_app_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), app)
app_dir = os.path.join(os.path.expanduser('~'), app)

shortcut = os.path.join(os.path.expanduser('~'), 'Desktop', app + '.' + excecutable[system])

# install to home

if os.path.isdir(app_dir):
    shutil.rmtree(app_dir)
    shutil.copytree(current_app_dir, app_dir)
else:
    shutil.copytree(current_app_dir, app_dir)

# create shortcut

w = open(shortcut, 'w')
w.write('python ' + app_dir)
w.close()

if system == 'Darwin':
    os.system('chmod 755 ' + shortcut)
elif system == 'Linux':
    os.system('chmod +x' + shortcut)

try:
    import numpy
    print '\nPackage numpy already installed.'
except ImportError:
    os.system("pip install numpy")
try:
    import matplotlib
    print '\nPackage matplotlib already installed.'
except ImportError:
    os.system("pip install matplotlib")
try:
    import quantities
    print '\nPackage quantities already installed.'
except ImportError:
    os.system("pip install quantities")

print '\n'
raw_input('Installation completed. Press enter to exit.')