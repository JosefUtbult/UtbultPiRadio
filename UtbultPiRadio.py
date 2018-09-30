from gpiozero import LED
from RPi import GPIO
from time import sleep, time
from os import system
from pyvirtualdisplay import Display
# from pyautogui import hotkey, press, keyUp, keyDown

CLK = 17
DT = 27
BUTTON = 22
ROTATIONAMOUNT = 20

# leds = [LED(5), LED(6), LED(13), LED(19), LED(26)]
lastTime = None
display = None

def main(sleep1=sleep(2)):
    global lastTime
    global display

    try:

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

        data = {'counter': 0, 'clkLastState': 0, 'currentSite': sites[0]}

        data['currentSite']['open'](data['currentSite']['url'])

        lastTime = time()

        init()

        while True:
            lastCounter = data['counter']

            data = read_encoder(data)
            if lastCounter != data['counter']:
                print(data['counter'])

            data = set_site(data)

    finally:
        print('Terminating process')
        
        system('pkill -f chromium-browser')

        GPIO.cleanup()
        display.stop()

    
def init():
    try:
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    except NameError:
        print("GPIO is not defined. Uncomment the import if you are using a Raspberry")


def clock_up(data):
    global lastTime
    if time() - lastTime >= 4:
        lastTime = time()
        data['counter'] += 1

    return data


def read_encoder(data):
    data = dict(data)

    try:

        clk_state = GPIO.input(CLK)
        dt_state = GPIO.input(DT)

        if clk_state != data['clkLastState']:

            if dt_state != clk_state:

                data['counter'] += 1

            else:

                data['counter'] -= 1

        data['clkLastState'] = clk_state

        return data

    except ValueError as e:
        print("Tried to run read_encoder with an incorrect input list. \n" + e)

        return {'counter': 0, 'clkLastState': 0, 'currentSite': data['currentSite']}


def set_site(data):
    global sites

    index = None

    if data['counter'] >= ROTATIONAMOUNT:

        data['counter'] = max(data['counter'] - ROTATIONAMOUNT, 0)

        close_site()

        index = sites.index(data['currentSite']) + 1
        data['currentSite'] = sites[index % len(sites)]

        data['currentSite']['open'](data['currentSite']['url'])
        print('Changing site to %d' % sites.index(data['currentSite']['url']))

    elif data['counter'] <= -1 * ROTATIONAMOUNT:

        data['counter'] = min(data['counter'] + ROTATIONAMOUNT, 0)

        close_site()

        index = sites.index(data['currentSite']) - 1
        data['currentSite'] = sites[index % len(sites)]

        data['currentSite']['open'](data['currentSite']['url'])
        print('Changing site to %d' % sites.index(data['currentSite']['url']))

    return data


def open_youtube(url):
    print('open youtube with url ' + url)

    system('chromium-browser %s &' % url)
    system('ovs-vsctl del-br ovs-minion >/dev/null 2>&1')


def open_spotify(url):
    print('open spotify with url ' + url)

    system('chromium-browser %s &' % url)


def close_site():
    print('close site')
    
    keyDown('w')
    keyDown('ctrl')
    sleep(1)

    keyUp('w')
    keyUp('ctrl')

    system('pkill -f chromium-browser')
    system('ovs-vsctl del-br ovs-minion >/dev/null 2>&1')

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
