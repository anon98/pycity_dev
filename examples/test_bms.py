"""
The pycity_scheduling framework


Copyright (C) 2023,
Institute for Automation of Complex Power Systems (ACS),
E.ON Energy Research Center (E.ON ERC),
RWTH Aachen University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import numpy as np
import os
import http.server
import socketserver
import plotly.graph_objs as go
import plotly.io as pio
from plotly.subplots import make_subplots

import pycity_scheduling.util.factory as factory
from pycity_scheduling.classes import *
from pycity_scheduling.algorithms import *
from pycity_scheduling.solvers import *

# This is a simple power scheduling example to demonstrate the integration and interaction of a battery storage
# system using the central optimization algorithm.

def main(do_plot=False):
    print("\n\n------ Example 18: Scheduling Battery System ------\n\n")

    # Scheduling will be performed for one month:
    env = factory.generate_standard_environment(step_size=3600, op_horizon=24*31, mpc_horizon=None,
                                                mpc_step_width=None, initial_date=(2018, 3, 1), initial_time=(0, 0, 0))

    # Print energy prices
    print('\nEnergy Prices:')
    print(env.prices.da_prices)

    # City district / district operator objective is peak-shaving:
    cd = CityDistrict(environment=env, objective='peak-shaving')

      # Building equipped with an inflexible load and a PV+battery system / building objective is peak-shaving:
    bd = Building(environment=env, objective='none')
    cd.addEntity(entity=bd, position=[0, 0])
    ap = Apartment(environment=env)
    bd.addEntity(ap)
   
    fl = FixedLoad(environment=env, method=3, method_3_type='metal', annual_demand=35000000.0, profile_type="G2")
    ap.addEntity(fl)
    bes = BuildingEnergySystem(environment=env)
    bd.addEntity(bes)
    # pv = Photovoltaic(environment=env, method=0, area=25.0, beta=30.0, eta_noct=0.15)
    # bes.addDevice(pv)
    bat = Battery(environment=env, e_el_max=200.6, p_el_max_charge=100.0, p_el_max_discharge=100.6, soc_init=0.7, eta=1.0,
                  storage_end_equality=True)
    bes.addDevice(bat)
    
        
    bat2 = Battery(environment=env, e_el_max=300.6, p_el_max_charge=50.0, p_el_max_discharge=50.6, soc_init=0.7, eta=1.0,
                  storage_end_equality=True)
    bes.addDevice(bat2)


    # Perform the scheduling:
    opt = CentralOptimization(city_district=cd)
    results = opt.solve()
    cd.copy_schedule("central")

    # Print schedules and other info
    print('\nBuilding Electrical Schedule:')
    print(list(bd.p_el_schedule))
    
    print('\nFixed Load Schedule:')
    print(list(fl.p_el_schedule))
    
    print('\nBattery Power Schedule:')
    print(list(bat.p_el_schedule))
    
    print('\nBattery Energy Schedule:')
    print(list(bat.e_el_schedule))
    
    print('\nBattery 2 Power Schedule:')
    print(list(bat2.p_el_schedule))
    
    print('\nBattery 2 Energy Schedule:')
    print(list(bat2.e_el_schedule))

 # Gather the schedules
    schedules = {
        "building_power": bd.p_el_schedule,
        "fixed_load": fl.p_el_schedule,
        "battery1_power": bat.p_el_schedule,
        "battery1_energy": bat.e_el_schedule,
        "battery2_energy": bat2.e_el_schedule,
        "battery2_power": bat2.p_el_schedule
    }

    # Plot the schedules of interest:
    plot_time = list(range(env.timer.timesteps_used_horizon))

    if do_plot:
        fig = make_subplots(rows=6, cols=1, subplot_titles=("Energy Prices - Forecasted", "Grid Load - Forecasted", "Battery-1 Power", "Battery-1 Energy","Battery-2 Power","Battery-2 Energy"))

        fig.add_trace(go.Scatter(x=plot_time, y=env.prices.da_prices, mode='lines', name='Prices - Forecasted [€/MWh]'), row=1, col=1)
        fig.add_trace(go.Scatter(x=plot_time, y=schedules["building_power"], mode='lines', name='Grid Load - Forecasted'), row=2, col=1)
        # fig.add_trace(go.Scatter(x=plot_time, y=schedules["fixed_load"], mode='lines', name='Grid Load Forecasts [kW]'), row=3, col=1)
        fig.add_trace(go.Scatter(x=plot_time, y=schedules["battery1_power"], mode='lines', name='Battery 1 [kW]'), row=3, col=1)
        fig.add_trace(go.Scatter(x=plot_time, y=schedules["battery1_energy"], mode='lines', name='Battery 1 [kWh]'), row=4, col=1)
        fig.add_trace(go.Scatter(x=plot_time, y=schedules["battery2_power"], mode='lines', name='Battery 2[kW]'), row=5, col=1)
        fig.add_trace(go.Scatter(x=plot_time, y=schedules["battery2_energy"], mode='lines', name='Battery 2[kWh]'), row=6, col=1)

        fig.update_layout(
            height=1500,
            title_text="Schedules : Peak Shaving ",
            xaxis_title='Time',
            yaxis_title='Power/Energy'
        )

        html_file = 'plot_peak_shaving.html'
        try:
            pio.write_html(fig, file=html_file, auto_open=False)
            print("HTML file created successfully.")
        except Exception as e:
            print(f"Error creating HTML file: {e}")

        # Start a simple HTTP server to serve the HTML file
        try:
            port = 8000
            os.chdir(os.path.dirname(os.path.abspath(html_file)))
            handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", port), handler)
            print(f"Serving at port {port}")
            print(f"Open your browser and go to http://localhost:{port}/{html_file}")
            httpd.serve_forever()
        except Exception as e:
            print(f"Error starting HTTP server: {e}")

    return

# Conclusions:
# To satisfy the desired peak-shaving objectives of the local building and the city district, it becomes evident that
# the battery storage unit is scheduled in a way that power is charged during times of low demand and discharged during
# times of high demand. Moreover, the battery storage unit is used to better cope with the fluctuating power consumption
# inside the building.

if __name__ == '__main__':
    # Run example:
    main(do_plot=True)
