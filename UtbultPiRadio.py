# from gpiozero import LED
# from RPi import GPIO
from time import sleep, time
from os import system

CLK = 17
DT = 18
ROTATIONAMOUNT = 4

# leds = [LED(5), LED(6), LED(13), LED(19), LED(26)]
lastTime = None


def main():
    global lastTime

    data = {'counter': 0, 'clkLastState': 0, 'currentSite': sites[0]}

    data['currentSite']['open'](data['currentSite']['url'])

    lastTime = time()

    init()

    while True:
        lastCounter = data['counter']
        data = set_site(clock_up(data))

        if lastCounter != data['counter']:
            print(data['counter'])


def init():
    try:
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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

    return {'counter': 0, 'clkLastState': 0}


def set_site(data):
    global sites

    index = None

    if data['counter'] >= ROTATIONAMOUNT:

        data['counter'] = max(data['counter'] - ROTATIONAMOUNT, 0)

        data['currentSite']['close']()

        index = sites.index(data['currentSite']) + 1
        data['currentSite'] = sites[index % len(sites)]

        data['currentSite']['open'](data['currentSite']['url'])


    elif data['counter'] <= -1 * ROTATIONAMOUNT:

        data['counter'] = min(data['counter'] - ROTATIONAMOUNT, 0)

        data['currentSite']['close']()

        index = sites.index(data['currentSite']) - 1
        data['currentSite'] = sites[index % len(sites)]

        data['currentSite']['open'](data['currentSite']['url'])

    return data


def open_youtube(url):
    print('open youtube with url ' + url)


def close_youtube():
    print('close youtube')


def open_spotify(url):
    print('open spotify with url ' + url)


def close_spotify():
    print('close spotify')


sites = [

    {'name': 'Calm Piano',
     'open': open_youtube,
     'close': close_youtube,
     'url': 'https://www.youtube.com/watch?v=rLMHGjoxJdQ'
     },

    {'name': 'Rainy Jazz',
     'open': open_youtube,
     'close': close_youtube,
     'url': 'https://www.youtube.com/watch?v=2ccaHpy5Ewo'
     },

    {'name': 'Spotify',
     'open': open_spotify,
     'close': close_spotify,
     'url': 'https://open.spotify.com'
     }

]

if __name__ == '__main__': main()
