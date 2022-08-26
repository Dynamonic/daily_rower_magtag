import ipaddress
import board
import displayio
import digitalio
import terminalio
import ssl
import wifi
import adafruit_requests
import alarm
import time
from adafruit_display_text.label import Label
from scraper import Scraper

#DEBUG
debug = False

#Display States
MAIN = 0
ALT = 1
SINGLE = False
WRAP = 46

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

#SETUP INTERRUPTS
startup_flag = True


#SETUP WIFI
#print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
#print("Connecting to %s"%secrets["ssid"])
if not debug:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
#print("Connected to %s!"%secrets["ssid"])
#print("My IP address is", wifi.radio.ipv4_address)

#time url NOT USED CURRENTLY
#TIME_URL = ""
#pool = socketpool.SocketPool(wifi.radio)
#requests = adafruit_requests.Session(self.pool, ssl.create_default_context())

workouts = Scraper()


#SLEEP ALARMS
time_alarm = alarm.time.TimeAlarm(monotonic_time=6*60*60) # every 6 hours
pin_alarm = alarm.pin.PinAlarm(pin=board.D15, value=False, pull=True)

#Button Setup
button_a = digitalio.DigitalInOut(board.D15)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.UP

button_b = digitalio.DigitalInOut(board.D14)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.UP

button_c = digitalio.DigitalInOut(board.D12)
button_c.direction = digitalio.Direction.INPUT
button_c.pull = digitalio.Pull.UP

button_d = digitalio.DigitalInOut(board.D11)
button_d.direction = digitalio.Direction.INPUT
button_d.pull = digitalio.Pull.UP


epd = board.DISPLAY
disp_h = 128
disp_w = 296
main_bmp = "/bmps/Main.bmp"
single_bmp = "/bmps/Individual.bmp"

#INITIAL SCREEN
splash_screen = Label(terminalio.FONT, text = 'Workout of the Day')
splash_screen.anchor_point = (0.5,0.5)
splash_screen.anchored_position = (disp_w//2, disp_h//2)


bitmap_main = displayio.OnDiskBitmap(main_bmp)
main_group = displayio.Group()
bg = displayio.TileGrid(bitmap_main, pixel_shader=bitmap_main.pixel_shader)
main_group.append(bg)
label = Label(terminalio.FONT, text = "Workouts")
label.anchor_point = (0.5,0.5)
label.anchored_position = (disp_w//2, disp_h//10)
main_group.append(label)

single_group = displayio.Group()
bitmap_s = displayio.OnDiskBitmap(single_bmp)
single_back = displayio.TileGrid(bitmap_s,pixel_shader=bitmap_s.pixel_shader)
single_group.append(single_back)


txt_color = 0xffffff
#These labels and positions relate to the positions on the BMPs that the text should be added to
#SINGLE
title_label = Label(terminalio.FONT,text = '', color = txt_color)
title_label.anchor_point = (0,0.5)
title_label.anchored_position = (10, disp_h//10)
body_label = Label(terminalio.FONT,text = '', color = txt_color)
body_label.anchor_point = (0,0)
body_label.anchored_position = (10, 3+(disp_h//5))
body_label.line_spacing = 1
button_label = Label(terminalio.FONT,text = '', color = txt_color)
button_label.anchor_point = (0,0.5)
button_label.anchored_position = (10, 10+7*(disp_h//10))
single_group.append(title_label)
single_group.append(body_label)
single_group.append(button_label)
#SINGLE BUTTONS
a_single = Label(terminalio.FONT,text = 'ALT/Wake', color = txt_color)
a_single.anchor_point = (0.5,0.5)
a_single.anchored_position = (disp_w//8,disp_h-10)
b_single = Label(terminalio.FONT,text = 'Short', color = txt_color)
b_single.anchor_point = (0.5,0.5)
b_single.anchored_position = (3*(disp_w//8),disp_h-10)
c_single = Label(terminalio.FONT,text = 'Medium', color = txt_color)
c_single.anchor_point = (0.5,0.5)
c_single.anchored_position = (5*disp_w//8,disp_h-10)
d_single = Label(terminalio.FONT,text = 'Long', color = txt_color)
d_single.anchor_point = (0.5,0.5)
d_single.anchored_position = (7*disp_w//8,disp_h-10)
single_group.append(a_single)
single_group.append(b_single)
single_group.append(c_single)
single_group.append(d_single)

#MAIN
short_title = Label(terminalio.FONT,text = '', color = txt_color)
short_title.anchor_point = (0,0.5)
short_title.anchored_position = (10, 3*(disp_h//10))
med_title = Label(terminalio.FONT,text = '', color = txt_color)
med_title.anchor_point = (0,0.5)
med_title.anchored_position = (10, 5*(disp_h//10)+5)
long_title = Label(terminalio.FONT,text = '', color = txt_color)
long_title.anchor_point = (0,0.5)
long_title.anchored_position = (10, 7*(disp_h//10)+10)
main_group.append(short_title)
main_group.append(med_title)
main_group.append(long_title)
#MAIN BUTTONS
a_main = Label(terminalio.FONT,text = 'ALT/Wake', color = txt_color)
a_main.anchor_point = (0.5,0.5)
a_main.anchored_position = (disp_w//8,disp_h-10)
b_main = Label(terminalio.FONT,text = 'Short', color = txt_color)
b_main.anchor_point = (0.5,0.5)
b_main.anchored_position = (3*(disp_w//8),disp_h-10)
c_main = Label(terminalio.FONT,text = 'Medium', color = txt_color)
c_main.anchor_point = (0.5,0.5)
c_main.anchored_position = (5*disp_w//8,disp_h-10)
d_main = Label(terminalio.FONT,text = 'Long', color = txt_color)
d_main.anchor_point = (0.5,0.5)
d_main.anchored_position = (7*disp_w//8,disp_h-10)
main_group.append(a_main)
main_group.append(b_main)
main_group.append(c_main)
main_group.append(d_main)

#INIT SPLASH SCREEN
epd.show(splash_screen)
time.sleep(epd.time_to_refresh + 0.01)
epd.refresh()
while epd.busy:
     pass

#Used for debug without wifi access
if not debug:
    # Get workout info
    work_dict = workouts.scrape_no_re()
else:
    # Used for debugging/offline programming and testing
    work_dict = workouts.debug()

# DISPLAY FUNCTIONS:

def display_main(work_dict):
    short_txt = workouts.get_workout('short')[1]['title']
    med_txt = workouts.get_workout('medium')[1]['title']
    long_txt = workouts.get_workout('long')[1]['title']
    # CircuitPython 7+ compatible
    bg = displayio.TileGrid(bitmap_main, pixel_shader=bitmap_main.pixel_shader)
    label.text = "Workouts"
    short_title.text = "SHORT: "+short_txt
    med_title.text = "MEDIUM: "+med_txt
    long_title.text = "LONG: "+long_txt
    a_main.text = 'ALT/Wake'
    #group.append(bg)
    epd.show(main_group)
    time.sleep(epd.time_to_refresh + 0.01)
    epd.refresh()
    while epd.busy:
         pass
    return

def display_alts(work_dict):
    alt_s_txt = workouts.get_workout('alt_short')[1]['title']
    alt_m_txt = workouts.get_workout('alt_medium')[1]['title']
    alt_l_txt = workouts.get_workout('alt_long')[1]['title']
    bg = displayio.TileGrid(bitmap_main, pixel_shader=bitmap_main.pixel_shader)
    label.text = "Alt-Workouts"
    short_title.text = "SHORT: " + alt_s_txt
    med_title.text = "MEDIUM: " + alt_m_txt
    long_title.text = "LONG: " + alt_l_txt
    a_main.text = "REG/Wake"
    epd.show(main_group)
    time.sleep(epd.time_to_refresh + 0.01)
    epd.refresh()
    while epd.busy:
         pass
    return

def display_single(work_dict, length, alt=False):
    if alt:
        workout = workouts.get_workout("alt_"+length)[1]
        a_single.text = 'ALT/Wake'
    else: 
        workout = workouts.get_workout(length)[1]
        a_single.text = 'REG/Wake'
    title = get_flag()+workout['title']
    body = body_wrapping(workout['body'],WRAP)
    buttons = workout['pm5']
    title_label.text = title
    body_label.text = body
    button_label.text = buttons
    epd.show(single_group)
    time.sleep(epd.time_to_refresh + 0.01)
    epd.refresh()
    while epd.busy:
        pass
    return

#Helper Functions
def sleep_delay_ref():
    return time.monotonic()+240 #4 mins of inactivity timer

#DISPLAY STATES
s_flag = False
m_flag = False
l_flag = False

def single_disp():
    if s_flag or m_flag or l_flag:
        return True
    else: return False

#HELPER FOR TRACKING STATES
def set_flags(length):
    global s_flag, m_flag, l_flag
    if length == 'short':
        s_flag = True
        m_flag = False
        l_flag = False
    elif length == 'medium':
        s_flag = False
        m_flag = True
        l_flag = False
    elif length == 'long':
        s_flag = False
        m_flag = False
        l_flag = True
    else: #used for main
        s_flag = False
        m_flag = False
        l_flag = False

#HELPER FOR TITLE TEXT
def get_flag():
    if disp_state: #ALT
        if s_flag:
            return "ALT-SHORT: "
        elif m_flag:
            return "ALT-MEDIUM: "
        else:
            return "ALT-LONG: "
    else:
        if s_flag:
            return "SHORT: "
        elif m_flag:
            return "MEDIUM: "
        else:
            return "LONG: "

#HELPER FOR TEXT WRAPPING
def body_wrapping(body, length):
    wrapped = body
    if len(body)>length:
        wrapped = ''
        for i in range((len(body)//length)+1):
            if i<(len(body)//length):
                wrapped = wrapped + body[i*length:(i*length)+length] + '\n'
            else:
                wrapped = wrapped + body[i*length:]
    return wrapped

sleepy_time = sleep_delay_ref()
disp_state = MAIN

# MAIN LOOP: #Button issues
while True:
    #Init Display if Waking up
    if startup_flag:
        display_main(work_dict)
        set_flags('main')
        startup_flag = False
    #Button press logic
    if not button_a.value:
        if disp_state == MAIN and not single_disp():
            disp_state = ALT
            set_flags('main')
            display_alts(work_dict)
        else:
            disp_state = MAIN
            set_flags('main')
            display_main(work_dict)
    elif not button_b.value:
        if not s_flag:
            set_flags('short')
            display_single(work_dict, 'short', disp_state)
    elif not button_c.value:
        if not m_flag:
            set_flags('medium')
            display_single(work_dict, 'medium', disp_state)
    elif not button_d.value:
        if not l_flag:
            set_flags('long')
            display_single(work_dict, 'long', disp_state)
    #SLEEP AFTER CERTAIN TIME
    now = time.monotonic()
    if now >= sleepy_time:
        #Display main screen
        display_main(work_dict)
        #disconnect Wifi
        wifi.radio.enabled = False
        #Set alarms and sleep
        alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)