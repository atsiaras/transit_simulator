__all__ = ['transit_simulator']

import os
import ttk

import numpy as np

from Tkinter import *
import tkFileDialog
from tkMessageBox import *

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasBase, FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler, MouseEvent

import exodata
import exodata.astroquantities as aq

from clablimb import *
from transit import *
from exoplanet_orbit import *
from oec import *


def initialise_window(window, window_name, windows_to_hide, windows_to_close, exit_python):

    def exit_command():

        for i in windows_to_close:
            i.destroy()

        for i in windows_to_hide:
            i.withdraw()

        if exit_python:
            os._exit(-1)

    window.wm_title(window_name)
    window.protocol('WM_DELETE_WINDOW', exit_command)

    window.withdraw()


def setup_window(window, objects, main_font=None, button_font=None, entries_bd=3):

    if button_font is None:
        button_font = ['times', 15, 'bold']

    if main_font is None:
        main_font = ['times', 15]

    for row in range(len(objects)):
        if len(objects[row]) == 0:
            label_empty = Label(window, text='')
            label_empty.grid(row=row, column=100)
        else:
            for obj in objects[row]:

                if obj[0].winfo_class() == 'Button':
                    obj[0].configure(font=button_font)
                elif obj[0].winfo_class() == 'Entry':
                    obj[0].configure(bd=entries_bd, font=main_font)
                elif obj[0].winfo_class() in ['Label', 'Radiobutton']:
                    obj[0].configure(font=main_font)

                if len(obj) == 4:
                    obj[0].grid(row=row, column=obj[1], columnspan=obj[2], rowspan=obj[3])
                elif len(obj) == 3:
                    obj[0].grid(row=row, column=obj[1], columnspan=obj[2])
                else:
                    obj[0].grid(row=row, column=obj[1])


def finalise_window(window, position=5, topmost=False):

    window.update_idletasks()

    if position == 1:
        x = 0
        y = 0

    elif position == 2:
        x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
        y = 0

    elif position == 3:
        x = window.winfo_screenwidth() - window.winfo_reqwidth()
        y = 0

    elif position == 4:
        x = 0
        y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2

    elif position == 5:
        x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
        y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2

    elif position == 6:
        x = window.winfo_screenwidth() - window.winfo_reqwidth()
        y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2

    elif position == 7:
        x = 0
        y = window.winfo_screenheight() - window.winfo_reqheight()

    elif position == 8:
        x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
        y = window.winfo_screenheight() - window.winfo_reqheight()

    elif position == 9:
        x = window.winfo_screenwidth() - window.winfo_reqwidth()
        y = window.winfo_screenheight() - window.winfo_reqheight()

    else:
        x = 0
        y = 0

    window.geometry('+%d+%d' % (x, y))

    window.update_idletasks()

    window.lift()
    window.wm_attributes("-topmost", 1)
    if not topmost:
        window.after_idle(window.attributes, '-topmost', 0)

    window.deiconify()


def test_float_positive_input(input_str, typing):

    if typing == '1':
        try:
            if float(input_str) >= 0:
                return True
            else:
                return False
        except ValueError:
            return False

    else:
        return True


def transit_simulator():

    # #########
    # create and initialise the window
    # #########

    root = Tk()
    root2 = Tk()

    initialise_window(root, 'Transit simulator', [], [root, root2], False)
    initialise_window(root2, 'Transit simulator', [root2], [], False)

    # get variables from log and set as tk variables those to be modified

    catalogue = exodata.OECDatabase(oec(), stream=True)

    planet_search = StringVar(value='HD 209458 b')
    planet = StringVar(value='HD 209458 b')
    metallicity = DoubleVar(value=0.0)
    temperature = DoubleVar(value=0.0)
    logg = DoubleVar(value=0.0)
    phot_filter = IntVar(value=7)
    period = DoubleVar(value=0.0)
    rp_over_rs = DoubleVar(value=0.0)
    sma_over_rs = DoubleVar(value=0.0)
    inclination = DoubleVar(value=0.0)
    eccentricity = DoubleVar(value=0.0)
    periastron = DoubleVar(value=0.0)

    # set progress variables, useful for updating the window

    update_planet = BooleanVar(root, value=True)
    update_planet_list = BooleanVar(root, value=True)
    open_root2 = BooleanVar(root, value=False)

    # create the plot in the additional window

    figure = matplotlib.figure.Figure()
    figure.patch.set_facecolor('white')
    ax1 = figure.add_subplot(122)
    ax2 = figure.add_subplot(221)
    ax3 = figure.add_subplot(223)
    canvas = FigureCanvasTkAgg(figure, root2)
    canvas.get_tk_widget().pack()
    NavigationToolbar2TkAgg(canvas, root2)

    # create widgets

    metallicity_label = Label(root, text='Stellar metallicity (dex)')
    metallicity_entry = Scale(root, from_=-5, to=1, resolution=0.5, variable=metallicity, orient=HORIZONTAL)
    metallicity_entry.set(metallicity.get())

    temperature_label = Label(root, text='Stellar temperature (K)')
    temperature_entry = Scale(root, from_=3500, to=7000, resolution=250, variable=temperature, orient=HORIZONTAL)

    logg_label = Label(root, text='Stellar surface gravity (cm/s^2, log)')
    logg_entry = Scale(root, from_=0.0, to=5.0, resolution=0.5, variable=logg, orient=HORIZONTAL)

    available_filters = ['U', 'B', 'V', 'R', 'I', 'J', 'H', 'K']
    phot_filter_label = Label(root, text='Filter')
    phot_filter_label_2 = Label(root, text=available_filters[phot_filter.get()])
    phot_filter_entry = Scale(root, from_=0, to=len(available_filters) - 1, resolution=1,
                              variable=phot_filter, showvalue=False, orient=HORIZONTAL)

    period_label = Label(root, text='Period (days)')
    period_entry = Entry(root, textvariable=period, validate='key')
    period_entry['validatecommand'] = (period_entry.register(test_float_positive_input), '%P', '%d')

    rp_over_rs_label = Label(root, text='Rp/Rs')
    rp_over_rs_entry = Scale(root, from_=0, to=0.15, resolution=0.005, variable=rp_over_rs, orient=HORIZONTAL)

    sma_over_rs_label = Label(root, text='a/Rs')
    sma_over_rs_entry = Scale(root, from_=1, to=20, resolution=0.1, variable=sma_over_rs, orient=HORIZONTAL)

    inclination_label = Label(root, text='Inclination (deg)')
    inclination_entry = Scale(root, from_=70, to=90, resolution=0.1, variable=inclination, orient=HORIZONTAL)

    eccentricity_label = Label(root, text='Eccentricity')
    eccentricity_entry = Scale(root, from_=0, to=1, resolution=0.01, variable=eccentricity, orient=HORIZONTAL)

    periastron_label = Label(root, text='Periastron (deg)')
    periastron_entry = Scale(root, from_=0, to=360, resolution=1, variable=periastron, orient=HORIZONTAL)

    planet_label = Label(root, text='     Planet     ')
    combostyle = ttk.Style()
    combostyle.theme_create('combostyle', parent='alt',
                            settings={'TCombobox': {'configure':
                                                    {'selectbackground': 'white',
                                                     'fieldbackground': 'white',
                                                     'background': 'white'}}})
    combostyle.theme_use('combostyle')
    planet_entry = ttk.Combobox(root, textvariable=planet, state='readonly')
    planet_search_entry = Entry(root, textvariable=planet_search)

    search_planet_button = Button(root, text='SEARCH')

    plot_button = Button(root, text='PLOT')

    exit_transit_simulator_button = Button(root, text='EXIT')

    # define the function that updates the window

    def update_window(*event):

        if not event:
            pass

        if update_planet_list.get():

            if isinstance(catalogue.searchPlanet(planet_search.get()), list):
                test_sample = []
                for test_planet in catalogue.searchPlanet(planet_search.get()):
                    if test_planet.isTransiting:
                        test_sample.append(test_planet)
                planet_entry['values'] = tuple([ppp.name for ppp in test_sample])
            elif catalogue.searchPlanet(planet_search.get()):
                planet_entry['values'] = tuple([catalogue.searchPlanet(planet_search.get()).name])
            else:
                planet_entry['values'] = tuple([])

            if len(planet_entry['values']) == 1:
                planet.set(planet_entry['values'][0])
                update_planet.set(True)
            else:
                planet.set('Choose Planet')

            update_planet_list.set(False)

        if update_planet.get():

            obj_planet = catalogue.searchPlanet(planet.get())

            if not np.isnan(obj_planet.star.Z):
                metallicity.set(obj_planet.star.Z)
            else:
                metallicity.set(0.0)
            if not np.isnan(obj_planet.star.T):
                temperature.set(float(obj_planet.star.T))
            else:
                temperature.set(0.0)
            if not np.isnan(obj_planet.star.calcLogg()):
                logg.set(round(float(obj_planet.star.calcLogg()), 3))
            else:
                logg.set(0.0)
            if not np.isnan(obj_planet.P):
                period.set(float(obj_planet.P))
            else:
                period.set(0.0)
            if not np.isnan(obj_planet.R) and not np.isnan(obj_planet.star.R):
                rp_over_rs.set(round(float(obj_planet.R.rescale(aq.m) / obj_planet.star.R.rescale(aq.m)), 5))
            else:
                rp_over_rs.set(0.0)
            if not np.isnan(obj_planet.calcSMA()) and not np.isnan(obj_planet.star.R):
                sma_over_rs.set(round(float(obj_planet.calcSMA().rescale(aq.m) /
                                            obj_planet.star.R.rescale(aq.m)), 5))
            else:
                sma_over_rs.set(0.0)
            if not np.isnan(obj_planet.i):
                inclination.set(float(obj_planet.i))
            else:
                inclination.set(0.0)
            if not np.isnan(obj_planet.e):
                eccentricity.set(float(obj_planet.e))
            else:
                eccentricity.set(0.0)
            if not np.isnan(obj_planet.periastron):
                periastron.set(float(obj_planet.periastron))
            else:
                periastron.set(90.0)

            update_planet.set(False)

        phot_filter_label_2.configure(text=available_filters[phot_filter.get()])

        planet_entry.selection_clear()

        plot_transit = True

        for input_entry in [phot_filter_entry, metallicity_entry, temperature_entry, logg_entry, period_entry,
                            rp_over_rs_entry, sma_over_rs_entry, inclination_entry, eccentricity_entry,
                            periastron_entry]:

            if len(str(input_entry.get())) == 0:
                plot_transit = False

        if plot_transit:

            if period.get() == 0 or rp_over_rs.get() == 0 or sma_over_rs.get() == 0:
                plot_transit = False

        if plot_transit:

            try:
                limb_darkening_coefficients = clablimb(logg.get(), temperature.get(), metallicity.get(),
                                                       available_filters[phot_filter.get()])

                time_array = np.arange(100 - period.get() / 4, 100 + period.get() / 4, 30. / 24. / 60. / 60.)

                position = exoplanet_orbit(period.get(), sma_over_rs.get(), eccentricity.get(), inclination.get(),
                                           periastron.get(), 100, time_array)

                time_array = time_array[np.where(np.abs(position[1]) < 1.5)]

                position = exoplanet_orbit(period.get(), sma_over_rs.get(), eccentricity.get(), inclination.get(),
                                           periastron.get(), 100, time_array)

                transit_light_curve = transit(limb_darkening_coefficients, rp_over_rs.get(), period.get(),
                                              sma_over_rs.get(), eccentricity.get(), inclination.get(),
                                              periastron.get(), 100, time_array)

                a1, a2, a3, a4 = limb_darkening_coefficients
                star_r = np.arange(0, 1, 0.01)
                star_m = np.sqrt(1 - star_r * star_r)
                star_i = (1.0 - a1 * (1.0 - star_m ** 0.5) - a2 * (1.0 - star_m)
                          - a3 * (1.0 - star_m ** 1.5) - a4 * (1.0 - star_m ** 2))

                cmap = matplotlib.cm.get_cmap('rainbow')
                color = cmap(1 - (temperature.get() - 3500) / (9000 - 3500))

                ax2.cla()
                ax2.set_aspect('equal')
                ax2.tick_params(axis='both', which='both',
                                bottom='off', left='off', top='off', right='off', labelbottom='off', labelleft='off')
                star_circle = matplotlib.patches.Circle((0, 0), 1, color=color, fc=color)
                planet_circle = matplotlib.patches.Circle((position[1][len(position[1]) / 2],
                                                           position[2][len(position[2]) / 2]),
                                                          rp_over_rs.get(), color='k', fc='k')
                ax2.add_patch(star_circle)
                ax2.add_patch(planet_circle)
                ax2.plot(position[1], position[2], c='k')
                ax2.set_xlim(-1.5, 1.5)
                ax2.set_ylim(-1.5, 1.5)

                ax3.cla()
                ax3.set_aspect(3.0)
                ax3.set_yticks([0, 0.5, 1.0])
                ax3.set_xticks([-1.0, 0, 1.0])
                ax3.plot(star_r, star_i, c=color)
                ax3.plot(-star_r, star_i, c=color)
                ax3.set_xlim(-1.5, 1.5)
                ax3.set_ylim(0.1, 1.1)
                ax3.set_ylabel('I / I0')
                ax3.set_xlabel('r / Rs')

                ax1.cla()
                ax1.plot((time_array - 100) * 24.0 * 60.0, 1000 * transit_light_curve, c='k')
                ylim_1 = int(min(transit_light_curve) * 200)
                ax1.set_ylim(1000 * ylim_1 / 200.0, 1001)
                ax1.tick_params(left='off', right='on', labelleft='off', labelright='on')
                ax1.set_ylabel('F / F0 (ppt)')
                ax1.set_xlabel('t - T0 (min)')

            except IndexError:

                ax1.cla()
                ax2.cla()
                ax3.cla()

        canvas.draw()

    update_window()

    # define actions for the different buttons, including calls to the function that updates the window

    def choose_planet(entry):

        if not entry:
            return 0

        update_planet.set(True)
        update_window()

    def search_planet():

        update_planet_list.set(True)
        update_window()

    def plot():

        open_root2.set(True)
        update_window()

        root2.deiconify()

    def exit_transit_simulator():
        root.destroy()
        root2.destroy()

    # connect actions to widgets

    planet_entry.bind('<<ComboboxSelected>>', choose_planet)
    # planet_search_entry.bind(sequence='<KeyRelease>', func=update_window)
    phot_filter_entry.bind("<ButtonRelease-1>", update_window)
    metallicity_entry.bind("<ButtonRelease-1>", update_window)
    temperature_entry.bind("<ButtonRelease-1>", update_window)
    logg_entry.bind("<ButtonRelease-1>", update_window)
    period_entry.bind(sequence='<KeyRelease>', func=update_window)
    rp_over_rs_entry.bind("<ButtonRelease-1>", update_window)
    sma_over_rs_entry.bind("<ButtonRelease-1>", update_window)
    inclination_entry.bind("<ButtonRelease-1>", update_window)
    eccentricity_entry.bind("<ButtonRelease-1>", update_window)
    periastron_entry.bind("<ButtonRelease-1>", update_window)

    search_planet_button['command'] = search_planet
    plot_button['command'] = plot
    exit_transit_simulator_button['command'] = exit_transit_simulator

    # setup window

    setup_window(root, [
        [],
        [[phot_filter_label_2, 3]],
        [[phot_filter_label, 2], [phot_filter_entry, 3]],
        [[metallicity_label, 2], [metallicity_entry, 3]],
        [[temperature_label, 2], [temperature_entry, 3]],
        [[logg_label, 2], [logg_entry, 3]],
        [[planet_label, 1]],
        [[planet_search_entry, 1], [period_label, 2], [period_entry, 3]],
        [[search_planet_button, 1]],
        [[planet_entry, 1], [rp_over_rs_label, 2], [rp_over_rs_entry, 3]],
        [[sma_over_rs_label, 2], [sma_over_rs_entry, 3]],
        [[inclination_label, 2], [inclination_entry, 3]],
        [[plot_button, 1], [eccentricity_label, 2], [eccentricity_entry, 3]],
        [[exit_transit_simulator_button, 1], [periastron_label, 2], [periastron_entry, 3]],
        [],
    ])

    # finalise and show  window

    finalise_window(root, 1)
    finalise_window(root2, 3)
    root.mainloop()