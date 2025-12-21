from network import WLAN, STA_IF, AP_IF
from time import sleep_ms
import secrets
import machine
import utime
import time
import ntptime
import network

skip_wifi = False
ssid = ""


def sync_ntp(woff=1, soff=2):
    trials = 10
    while trials > 0:
        try:
            ntptime.settime()
            break
        except Exception as e:
            print(".", end="")
            utime.sleep(1)
            trials -= 1

            if trials == 0:
                print(str(e))
                return

    t = utime.time()
    tm = list(utime.localtime(t))
    tm = (
        tm[0:3]
        + [
            0,
        ]
        + tm[3:6]
        + [
            0,
        ]
    )
    year = tm[0]

    # Time of March change for the current year
    t1 = utime.mktime((year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0))
    # Time of October change for the current year
    t2 = utime.mktime((year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0))

    if t >= t1 and t < t2:
        tm[4] += soff  # UTC + 1H for BST
    else:
        tm[4] += woff  # UTC + 0H otherwise

    machine.RTC().datetime(tm)
    return utime.localtime()


def try_connection(timeout=12):
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        sleep_ms(500)
        timeout = timeout - 1
    return wlan.isconnected()


print("Starting Wifi...")
WLAN(AP_IF).active(False)
wlan = WLAN(STA_IF)
# Only for deep sleep ?
# print('connecting to last AP', end='')
# print(try_connection(3))
if not wlan.isconnected() and not skip_wifi:
    wlan = WLAN(STA_IF)
    wlan.active(True)
    network.WLAN(network.STA_IF).config(
        txpower=5
    )  # FIX BUG With WIFI (prior value was 20)
    ap_list = wlan.scan()
    ## sort APs by signal strength
    ap_list.sort(key=lambda ap: ap[3], reverse=True)
    ## filter only trusted APs
    ap_list = list(
        filter(lambda ap: ap[0].decode("UTF-8") in secrets.wifi.aps.keys(), ap_list)
    )
    for ap in ap_list:
        essid = ap[0].decode("UTF-8")
        if not wlan.isconnected():
            print("connecting to", essid, end="")
            ssid = essid
            wlan.connect(essid, secrets.wifi.aps[essid])
            print(try_connection())

if not skip_wifi:
    print("Setting time...")
    # Update the time
    time.sleep(1)
    (year, month, day, hour, minute, second, xx, yy) = sync_ntp()
    print(f"It's {hour}:{minute:02d}")
    print("gc.collect()")
    import gc

    gc.collect()

    print(wlan.ifconfig()[0])
    #import webrepl

    #webrepl.start()

# TODO: is this better?
# if tmo > 0:
#     print("WiFi started")
#     utime.sleep_ms(500)
#
#     rtc = machine.RTC()
#     print("Synchronize time from NTP server ...")
#     rtc.ntp_sync(server="hr.pool.ntp.org")
#     tmo = 100
#     while not rtc.synced():
#         utime.sleep_ms(100)
#         tmo -= 1
#         if tmo == 0:
#             break
#
#     if tmo > 0:
#         print("Time set")
#         utime.sleep_ms(500)
#         t = rtc.now()
#         utime.strftime("%c")
#         print("")
