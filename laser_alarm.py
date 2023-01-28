from machine import Pin,ADC,Timer
from time import sleep
from lib import blynklib,blynktimer
import network

class var:
    def __init__(self):
        self.val = 0
s,blys,p,res = var(),var(),var(),var()
#https://community.blynk.cc/t/micropython-and-blynk-2-0-libary/53861
# https://github.com/lemariva/uPyBlynk/blob/master/BlynkLibWiPy.py

auth_token = ""#Blynk auth-token

ssid = "" # Wifi name
password = "" # password
wlan = network.WLAN(network.STA_IF)
timer = blynktimer.BlynkTimer()
wlan.active(False)
led = Pin(2,Pin.OUT)
led.value(0)
wlan.active(True)
wlan.connect(ssid,password)#Enter wifi name and password

while not wlan.isconnected():
    print('connecting...')
    sleep(1)
blynk = blynklib.Blynk(auth_token)

def my_write_handler(value):
    print('Current V0 value: {}'.format(value))
    x = value[0]
    blys.val = int(x)+1
    blynk.virtual_write(1,x)
def my_write_handler2(value):
    print('Current V2 value: {}'.format(value))
    res.val = 1
    
def initial():
    blynk.sync_virtual(0)
blynk.on('connected',initial)
blynk.on('V0',my_write_handler)
blynk.on('V2',my_write_handler2)
print(wlan.isconnected())


g,b,r = Pin(13,Pin.OUT),Pin(14,Pin.OUT),Pin(27,Pin.OUT)
r.value(1),g.value(1),b.value(1);
s.val = 1
r.value(0),g.value(1),b.value(1)
buzz = Pin(22,Pin.OUT)

li = ADC(Pin(34))
reset = Pin(23,Pin.IN)

def tim(t):
    buzz.value(not buzz.value())
t = Timer(1)
def alarm():
    if blys.val ==1 :
        s.val = 1
        t.deinit()
        p.val = 0
        try:
            blynk.virtual_write(3,'Clear')
        except:
            pass
        buzz.value(0)
        r.value(0),g.value(1),b.value(1)
    elif res.val ==1:
        res.val =0
        if s.val ==1:
            return
        t.deinit()
        buzz.value(0)
        p.val = 0
        try:
            blynk.virtual_write(3,'Clear')
        except:
            pass
        r.value(0),g.value(1),b.value(0)
        sleep(0.1)
        if s.val==2:
            r.value(1),g.value(0),b.value(1)
    elif blys.val ==2:
        s.val = 2
        r.value(1),g.value(0),b.value(1)
    d=li.read()
    if d<3000 and s.val==2:
        try:
            if p.val==0:
                blynk.virtual_write(3,'Tripped')
                http_get('')#Enter ifttt webhook link
                p.val = 1
        except:
            pass
        
        t.init(freq = 10, mode = Timer.PERIODIC, callback = tim)
    
    if reset.value()==1:
        t.deinit()
        p.val =0
        buzz.value(0)
        while reset.value()==1:
            pass

timer.set_interval(100,alarm)


def http_get(url):
    import socket
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

while True:
    if wlan.isconnected():
        blynk.run()
        timer.run()
    
    sleep(0.1)