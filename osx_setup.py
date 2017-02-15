import os
import shutil

home = os.path.expanduser('~')
desktop = os.path.join(home, 'Desktop')
location = os.path.dirname(__file__)

if os.path.isdir(os.path.join(home, 'transit_simulator')):
    shutil.rmtree(os.path.join(home, 'transit_simulator'))
    
shutil.copytree(os.path.join(location, 'transit_simulator'), os.path.join(home, 'transit_simulator'))

shutil.copy(os.path.join(location, 'transit_simulator.command'), os.path.join(location, 'transit_simulator_test.command'))

w = open(os.path.join(location, 'transit_simulator_test.command'), 'a')
w.write('python {0}'.format(os.path.join(home, 'transit_simulator')))
w.close()

shutil.move(os.path.join(location, 'transit_simulator_test.command'), os.path.join(desktop, 'transit_simulator.command'))