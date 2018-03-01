import platform
import os

name = 'transit_simulator'

os.chdir(os.path.abspath(os.path.dirname(__file__)))

from transit_simulator import __get_abspath__

app_dir = __get_abspath__()
system = platform.system()

excecutable = {'Darwin': 'command', 'Linux': 'sh', 'Windows': 'cmd'}

# create shortcut
try:
    shortcut = os.path.join(os.path.expanduser('~'), 'Desktop', name + '.' + excecutable[system])
    w = open(shortcut, 'w')
    w.write('python \"' + app_dir + '\"')
    w.close()
except IOError:
    shortcut = os.path.join(os.path.expanduser('~'), name + '.' + excecutable[system])
    w = open(shortcut, 'w')
    w.write('python \"' + app_dir + '\"')
    w.close()

if system == 'Darwin':
    os.system('chmod 755 ' + shortcut)
elif system == 'Linux':
    os.system('chmod +x ' + shortcut)
