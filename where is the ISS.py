import requests
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from time import sleep
import threading
import PySimpleGUI as sg
import os

got_position = False
main_program_open = True
window_size = (680,502)
new_window_size = False
iss_position = None

class back_end(threading.Thread):
    def __init___(self):
        threading.Thread.__init__(self)

    def get_iss_position(self):
        global iss_position
        try:
            answer = requests.get('http://api.open-notify.org/iss-now.json')
            if answer.status_code == 200:
                data = answer.json()
                iss_position = data['iss_position']
                return iss_position
            else:
                return None
        except requests.exceptions.ConnectionError:
            print('check your internet connection')

    def iss_map(self, path):
        global got_position, window_size
        if iss_position:
            if window_size[0] < window_size[1]:
                plt.figure(figsize=(int(window_size[0]*.01), int(window_size[0]*.01)))
            elif window_size[0] > window_size[1]:
                plt.figure(figsize=(int(window_size[1]*.01), int(window_size[1]*.01)))
            
            lon = float(iss_position['longitude'])
            lat = float(iss_position['latitude'])
            
            map = Basemap(projection='ortho', lat_0=lat, lon_0=lon, resolution=None)
            map.bluemarble()

            x, y = map(lon, lat)
            map.plot(x, y, 'ro', markersize=5)

            try:
                plt.savefig(fname=path+'\img.png', transparent=True)
                got_position = True

            except FileNotFoundError:
                os.makedirs(path)
                plt.savefig(fname=path+'\img.png', transparent=True)
                got_position = True
            except SystemError:
                print('an error ocurred')
        else:
            print('something went wrong!')

    def run(self):
        global main_program_open, got_position, new_window_size
        path = os.getcwd() + r'\image_where_is_the_iss'
        while main_program_open:
            if got_position == False:
                self.get_iss_position()
                self.iss_map(path)
            if new_window_size:
                new_window_size = False
                self.iss_map(path)
            sleep(1)


class gui(threading.Thread):
    def __init__(self):
       threading.Thread.__init__(self)

    def make_window(self, path):
        layout = [
            [sg.Column([[sg.Image(path+'\img.png', enable_events=True, key='position_img')]], justification='centre')]
        ]

        window = sg.Window('Current ISS position', layout, resizable=True, finalize=True)
        return window

    def run(self):
        global main_program_open, got_position, window_size, new_window_size
        path = os.getcwd() + r'\image_where_is_the_iss'
        main_window = self.make_window(path)
        while main_program_open:
            event, values = main_window.read(timeout=10)
            if event == sg.WINDOW_CLOSED:
                main_program_open = False
                main_window.close()
                break
            if got_position:
                main_window['position_img'].update(path+'\img.png')
                got_position = False
            if window_size != main_window.size:
                window_size = main_window.size
                new_window_size = True


if __name__ == '__main__':
    t1 = gui()
    t2 = back_end()
    t1.start()
    t2.start()