from gpiozero import LED
from RPi import GPIO
from time import sleep
from os import system
from sys import argv
from pyvirtualdisplay import Display

# from pyautogui import hotkey, press, keyUp, keyDown

CLK = 17
DT = 27
BUTTON = 22
ROTATIONAMOUNT = 10
DISPLAYSTATE = None
BROWSERNAME = None

# leds = [LED(5), LED(6), LED(13), LED(19), LED(26)]
display = None


def main():
    global lastTime
    global display
    global DISPLAYSTATE
    global BROWSERNAME

    DISPLAYSTATE = True
    BROWSERNAME = 'Chromium'

    for instance in range(0, len(argv)):
        try:

            if argv[instance] == '-display':

                if argv[instance + 1] in ['false', 'FALSE', 'False']:
                    DISPLAYSTATE = False
                    print("Using the native display")
                else:
                    print("Generating a virtul display")

            if argv[instance] == '-browser':

                if argv[instance + 1] in ['chromium', 'Chromium']:

                    BROWSERNAME = 'Chromium'
                    print("Seting browser to Chromium")

                elif argv[instance + 1] in ['firefox', 'Firefox']:

                    BROWSERNAME = 'Firefox'
                    print("Seting browser to Firefox")


        except IndexError:

            pass

    try:

        if DISPLAYSTATE:
            display = Display(visible=0, size=(800, 600))
            display.start()

        while True:
            try:
                from pyautogui import hotkey, press, keyUp, keyDown
                print("Imported pyautogui!")
                break

            except:
                print("Could not open pyautogui")
                sleep(2)

        init()

        data = {'counter': 0, 'clkLastState': GPIO.input(CLK), 'currentSite': sites[0]}

        data = set_site(data)
        close_site()

        while True:
            lastCounter = data['counter']

            data = read_encoder(data)

            if lastCounter != data['counter']:
                print(data['counter'])
                data = set_site(data)

            data = set_site(data)

    finally:
        print('Terminating process')

        system('pkill -f chromium-browser')

        GPIO.cleanup()

        if DISPLAYSTATE:
            display.stop()


def init():
    try:

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    except NameError:
        print("GPIO is not defined. Uncomment the import if you are using a Raspberry")


def read_encoder(data):
    global CLK
    global DT

    try:

        clkState = GPIO.input(CLK)
        dtState = GPIO.input(DT)

        if clkState != data['clkLastState']:

            if dtState != clkState:

                data['counter'] += 1
            else:

                data['counter'] -= 1

            print(data['counter'])

        data['clkLastState'] = clkState

        # print(data)

        sleep(0.01)
        return data

    except ValueError as e:
        print("Tried to run read_encoder with an incorrect input list. \n" + e)

        return {'counter': 0, 'clkLastState': 0, 'currentSite': sites[0]}


def set_site(data):
    global sites

    index = None

    if data['counter'] >= ROTATIONAMOUNT:

        data['counter'] = max(data['counter'] - ROTATIONAMOUNT, 0)

        close_site()

        index = sites.index(data['currentSite']) + 1
        data['currentSite'] = sites[index % len(sites)]

        data['currentSite']['open'](data['currentSite']['url'])
        print('Changing site to %d' % sites.index(data['currentSite']))

    elif data['counter'] <= -1 * ROTATIONAMOUNT:

        data['counter'] = min(data['counter'] + ROTATIONAMOUNT, 0)

        close_site()

        index = sites.index(data['currentSite']) - 1
        data['currentSite'] = sites[index % len(sites)]

        data['currentSite']['open'](data['currentSite']['url'])
        print('Changing site to %d' % sites.index(data['currentSite']))

    return data


def open_youtube(url):
    global BROWSERNAME

    print('open youtube with url ' + url)

    if BROWSERNAME == 'Chromium':
        system('chromium-browser %s &' % url)
    elif BROWSERNAME == 'Firefox':
        system('firefox %s &' % url)

    else:
        print("There are no browser named " + BROWSERNAME)


def open_spotify(url):
    global BROWSERNAME

    system('sudo systemctl start raspotify.service')


def close_site():
    from pyautogui import hotkey, press, keyUp, keyDown

    print('close site')

    keyDown('w')
    keyDown('ctrl')
    sleep(1)

    keyUp('w')
    keyUp('ctrl')

    if BROWSERNAME == 'Chromium':
        system('pkill -f chromium-browser')

    elif BROWSERNAME == 'Firefox':
        system('pkill -f firefox')

    else:
        print("There are no browser named " + BROWSERNAME)

    system('sudo systemctl stop raspotify.service')


sites = [

    {'name': 'Calm Piano',
     'open': open_youtube,
     'url': 'https://www.youtube.com/watch?v=rLMHGjoxJdQ'
     },

    {'name': 'Rainy Jazz',
     'open': open_youtube,
     'url': 'https://www.youtube.com/watch?v=2ccaHpy5Ewo'
     },

    {'name': 'Spotify',
     'open': open_spotify,
     'url': 'https://open.spotify.com'
     }

]

if __name__ == '__main__': main()
