# python 3.10
import sys, nidaqmx, time, csv
import datetime as dt
from nidaqmx.constants import (ThermocoupleType)
import nidaqmx.system
import matplotlib.pyplot as plt
#import matplotlib.animation as animation

# check NI devices connected to system


State = [False, True, False]

def System_config(task1, State):
    if State == "System_off":
        Sys_State = [False, False, False]
    elif State == "System_heat":
        Sys_State = [True, False, False]
    elif State == "System_Bias_On":
        Sys_State = [True, True, False]
    elif State == "System_cool":
        Sys_State = [False, False, True]
    elif State == "System_off":
        Sys_State = [False, False, False]
    task1.write(Sys_State)
    time.sleep(2)
    return(f"System is in the {State} state")

def input_sample_description():
    sample_name = input("input sample name: ")
    sample_description = input("input sample description: ")
    fn = input("input the base filename: ")
    if fn == "":
        fn = filename = "RDT_time_current_temp"
    test_date = str(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    test_date_fn = str(dt.datetime.now().strftime('%Y-%m-%d'))
    filename = fn + "_" + test_date_fn + ".csv"
    figname = input("input the base  figure name: ")
    if figname == "":
        figname = fn
    fig_name = figname + "_" + test_date_fn + ".jpg"
    header = ["elapsed time (s)", "current (A)", "Temperature hot plate (C)", "Temperature glass proxy (C)"]
    return(sample_name, sample_description, test_date, filename, fig_name, header)

def Define_tasks():
    local_system = nidaqmx.system.System.local()
    device_list = []

    for device in local_system.devices:
        print("Device name: {}, Product Category: {}, Product Type: {},".format(device.name, device.product_category, device.product_type))
        device_list.append([device.product_type, device.name])

    # on RDT hardware use USB9211 set appropriate min_val, max_val
    min_val_USB9211 = -0.05
    max_val_USB9211 = 0.05
    # for testing with AIO USB6009 or USB6008, use the USB6009 set appropriate min_val, max_val
    #min_val_USB6009 = -0.5
    #max_val_USB6009 = 0.5
    task = USB9211(device_list, min_val_USB9211, max_val_USB9211)
    #task = USB6009(device_list, min_val_USB6009, max_val_USB6009)
    task1 = USB6525(device_list)

    return(task, task1)


def USB6009(device_list, min_val_USB6009, max_val_USB6009):

    try:
        # NI 6008 / 6009 analog in
        task = nidaqmx.Task("task")
        if device_list[0][0] in ("USB-6009", "USB-6008"):
            device_num_600n = device_list[0][1]
        if device_list[1][0] in ("USB-6009", "USB-6008"):
            device_num_600n = device_list[1][1]
        task.ai_channels.add_ai_voltage_chan(device_num_600n + "/ai0", min_val = min_val_USB6009, max_val = max_val_USB6009)
        task.ai_channels.add_ai_voltage_chan(device_num_600n + "/ai1", min_val = min_val_USB6009, max_val = max_val_USB6009)
        task.ai_channels.add_ai_voltage_chan(device_num_600n + "/ai2", min_val = min_val_USB6009, max_val = max_val_USB6009)
        task.start()
        print("USB6008 / USB6009 task started")
        return(task)
    except nidaqmx.DaqError as e:
        print(f"USB6009 AIO device error occurred: \{e}")
    #value = task.read()
    #print(value)

def USB6525(device_list):
    try:
        # NI 6525 relay controller    
        task1 = nidaqmx.Task("task1")
        if device_list[0][0] == "USB-6525":
            device_num_6525 = device_list[0][1]
        if device_list[1][0] == "USB-6525":
            device_num_6525 = device_list[1][1]
        task1.do_channels.add_do_chan(device_num_6525 + "/port0/line0")
        task1.do_channels.add_do_chan(device_num_6525 + "/port0/line1")
        task1.do_channels.add_do_chan(device_num_6525 + "/port0/line2")
        task1. start()
        print("USB6525 task started")
        return(task1)
    except nidaqmx.DaqError as e:
        print(f"USB6525 relay controller device error occurred: \{e}")

def USB9211(device_list, min_val_USB9211, max_val_USB9211):
    try:
        # NI 9211 current and TC
        task = nidaqmx.Task("task")
        if device_list[0][0] == "USB-9211A":
            device_num_9211 = device_list[0][1]
        if device_list[1][0] == "USB-9211A":
            device_num_9211 = device_list[1][1]
        task.ai_channels.add_ai_voltage_chan(device_num_9211 + "/ai0", min_val=min_val_USB9211, max_val=max_val_USB9211)
        task.ai_channels.add_ai_thrmcpl_chan(device_num_9211 + "/ai1", name_to_assign_to_channel="T_HotPlate", thermocouple_type=ThermocoupleType.K)
        task.ai_channels.add_ai_thrmcpl_chan(device_num_9211 + "/ai2", name_to_assign_to_channel="T_HotPlate2", thermocouple_type=ThermocoupleType.K)
        task.start()
        print("USB9211 task started")
        return(task)
    except nidaqmx.DaqError as e:
        print(f"USB9211 current and TC read device error occurred: \{e}")

def initialize(T_bias_on, T_bias_flag):
    # initializing system setting all power and heat and fan off        
        task1.write([False, False, False])
        # check measured analog inputs with all power and heat off
        I_0_0, T_0_0, T_0_1 = task.read()
        print("Check of initial current and temperature with all power and heat off:\n", I_0_0, T_0_0, T_0_1, "\n")

        if T_0_0 > T_bias_on:
            T_bias_flag = 1
            return(T_bias_flag, T_0_0)
        else:
            T_bias_flag = 0
            return(T_bias_flag, T_0_0)


def save_data_to_file(filename, sample_name, sample_description, test_date, header, data_out_list):
    with open(filename, 'w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(["sample:", sample_name])
        csvwriter.writerow(["sample description:", sample_description])
        csvwriter.writerow(["date and time of test:", test_date])
        csvwriter.writerow(header)
        csvwriter.writerows(data_out_list)
    return()

def heat_sample(task, task1, T_bias_on):
    System_config(task1, "System_heat")
    output_value = task.read()[1]
    if output_value < T_bias_on:
            output_value = task.read()[1]
            #print("aio out = ", output_value)
            time.sleep(1)
    return(f"Temperature at or above {T_bias_on} with T = {output_value}")

def bias_on(task1):
    State = "System_Bias_On"
    Sys_State = System_config(task1, State)
    return(Sys_State)

def DAQ(data_out_list, t_run, t_delay):
    N_meas = int(t_run*60/t_delay) # number of DAQs based on
    print(N_meas)
    for t_index in range(N_meas):
            TIME = t_index*t_delay
            x.append(TIME/60)
            Data_read = task.read()
            y.append(Data_read[0])
            #if len(x) > maxlen:
            #    del x[0]
            #    del y[0]
            ax.clear()
            ax.plot(x,y, color = 'b')
            ax.set_xlim(left=0, right = int(N_meas*t_delay/60))
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.005)
            #print(TIME, Data_read[0], Data_read[1], Data_read[2])
            data_out = [str(TIME), str(Data_read[0]), str(Data_read[1]), str(Data_read[2])]
            data_out_list.append(data_out)
            time.sleep(t_delay)
    plt.savefig(fig_name)
    return(data_out_list)

def Cooldown(task, task1, T_cool, fan_delay):
    Cool_intervals = 1000
    t_cool_sleep = fan_delay / Cool_intervals
    State = "System_cool"
    Sys_State = System_config(task1, State)
    print("cooldown initial sys_state: ", Sys_State)
    for t_cool_interval in range(Cool_intervals):
        output_value = task.read()[1]
        print(f"Cooling: t = {(t_cool_interval-1)*t_cool_sleep}, T = {output_value}, T_cool = {T_cool}")
        time.sleep(t_cool_sleep)
        t_cool = t_cool_interval * t_cool_sleep
        if (t_cool > fan_delay) or (output_value < T_cool):
            return(Sys_State, t_cool)
    return(Sys_State, t_cool)

def end_and_exit():
    task1.write([False, False, False])
    task1.stop()
    task.stop()
    task1.close()
    task.close()
    sys.exit()

if __name__ == "__main__":
    
    # Define and set parameters
    T_bias_on = 150.0 # T_bias_on is temperature sample is heated to before turning on the bias voltage - typ. 240C setpoint
    T_bias_flag = 0 # flag = 0 if T < T_bias_on, flag = 1 if T > T_bias_on
    t_run = 1 # total run time from T>T_bias_on in minutes
    t_delay = 1 # time between DAQs in seconds
    data_out_list = [] # saved data initialization

    fan_delay = 30 # maximum time in minutes to run the fan during cooldown
    T_cool = 130 # T_cool is the temperature to stop cooling 
    
    # SAMPLE AND TEST INFORMATION SECTION
    # input information for saving the data and figure
    sample_name, sample_description, test_date, filename, fig_name, header= input_sample_description() #this will all be handled by frontend

    # INITIALIZE NI UNITS SECTION
    # load devices and set tasks
    task, task1 = Define_tasks() #done

    # PLOT FIGURE INITIALIZATION SECTION
    # set up figure for RT plotting
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x, y = [], []
    #maxlen = 10000
    
    try: 
        # initialize all relays to open, check T and compare with T_bias_on
        T_bias_flag, T_0_0 = initialize(T_bias_on, T_bias_flag)

        if T_bias_flag == 1:
            # system temperature is > T_bias_on, turn on heaters but skip to DAQ step
            System_config(task1, "System_heat")
            print(f"Temperature T_0 already at or above {T_bias_on} with T = {T_0_0}, moving to bias on state")
        else:
            # start heating and read temperature during heat up stage until T>T_bias_on [typ. 240C] setpoint
            print(f"Temperature T_0 is below {T_bias_on} with T = {T_0_0}, initiate heating and heat until T_0 > {T_bias_on}")
            Heated = heat_sample(task, task1, T_bias_on)
            print(Heated, "\n")

        # TURN ON BIAS VOLTAGE SECTION
        # when T>T_bias_on, turn on bias voltage
        Sys_State = bias_on(task1)
        print(Sys_State)
        
        # DAQ SECTION
        # DAQ read T and I every t_delay second for N_meas intervals
        # alternative to try ? is exit for loop if I < 5% of I(0)
        data_out_list = DAQ(data_out_list, t_run, t_delay)
        
        # SYSTEM SHUTDOWN SECTION
        #turn off power turn on fan on for fan_delay seconds [typ 3-5minutes, need routine to cool to T_cool temperature??]
        Sys_State, t_cool = Cooldown(task, task1, T_cool, fan_delay)
        print(Sys_State)
        print("time required to cool: ", t_cool)
        
        
        # after fan_delay time, turn off fan 
        State = "System_off"
        Sys_State = System_config(task1, State)
        print(Sys_State)

    except KeyboardInterrupt:
        print("\nStopped by user")
        end_and_exit()

    # save data to csv file
    save_data_to_file(filename, sample_name, sample_description, test_date, header, data_out_list)

    # stop and close tasks
    end_and_exit()