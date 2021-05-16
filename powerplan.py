# Author; Elijah

from pystray import Icon, Menu as menu, MenuItem as item
import threading
import configparser
import time, datetime
from os import path
import sys # for path and exit
import subprocess # for 'call'
import psutil # for list of processes
import powerplan_image as ppi
import winsound


class CFG: pass
CFG = CFG()
config = configparser.RawConfigParser()
config.optionxform=str
config.read(sys.path[0] + '\powerplan.cfg') #
try:
  confgeneral = config['General']
  CFG.timestep = int(confgeneral['timestep_sec'])
  if CFG.timestep < 1:
    raise BaseException("Timestep must be greatequal 1s")
  try:
    CFG.powercfg_output_decoder = confgeneral['powercfg_output_decoder']
    if len(CFG.powercfg_output_decoder) < 2 or CFG.powercfg_output_decoder == 'None':
      CFG.powercfg_output_decoder = None
  except BaseException as be:
    CFG.powercfg_output_decoder = None
  CFG.index_autoplan = int(confgeneral['index_autoplan'])
  CFG.caption_autoplan = confgeneral['caption_autoplan']
  CFG.caption_ignoreplans = confgeneral['caption_ignoreplans']
  CFG.caption_signal = confgeneral['caption_signal']
  CFG.caption_apps = confgeneral['caption_apps']
  CFG.caption_plans = confgeneral['caption_plans']
  CFG.caption_poweroff = confgeneral['caption_poweroff']
  CFG.caption_now = confgeneral['caption_now']
  CFG.caption_minutes = confgeneral['caption_minutes']

  try:
    CFG.warntime = (int(confgeneral['warning_hour']), int(confgeneral['warning_minute']))
    CFG.warnbeepfile = sys.path[0] + '\\' + confgeneral['warning_wavfile']
    if not path.isfile(CFG.warnbeepfile):
      print('warning_wavfile not found')
      raise BaseException()
  except BaseException as be:
    CFG.warntime, CFG.warnbeepfile = None, None

  try:
    CFG.nighttime = (int(confgeneral['night_hour']), int(confgeneral['night_minute']))
    CFG.nightbeepfile = sys.path[0] + '\\' + confgeneral['night_wavfile']
    if not path.isfile(CFG.nightbeepfile):
      print('night_wavfile not found')
      raise BaseException()
  except BaseException as be:
    CFG.nighttime, CFG.nightbeepfile = None, None

  CFG.plans = []
  for kk in config['Plans']:
    CFG.plans.append((kk, config['Plans'][kk]))
  plansCount = len(CFG.plans)

  try:
    confbeep = config['Beep']
    CFG.beepinterval = int(confbeep['interval_sec'])
    CFG.beepwav = sys.path[0] + '\\' + confbeep['wavfile']
    if CFG.beepwav == '' or not path.isfile(CFG.beepwav):
      print('BEEP wavfile not found')
      raise BaseException()
    try:
      CFG.caption_beep = confgeneral['caption_beep']
    except BaseException as be:
      CFG.caption_beep = None
  except BaseException as be:
    CFG.beepinterval = 10000000
    CFG.beepwav = None
    CFG.caption_beep = None

  try:
    CFG.caption_exit = confgeneral['caption_exit']
  except BaseException as be:
    CFG.caption_exit = None

  CFG.corrapps = []
  CFG.corrplans = []
  for aa in config['Applications']:
    plan = int(config['Applications'][aa])
    if plan > plansCount:
      raise BaseException("Plan level out of range")
    CFG.corrapps.append(aa)
    CFG.corrplans.append(plan)
except BaseException as be:
  print ('Wrong config: ' + str(be))
  sys.exit(1)

def check_process(proclist):
  ln = len(proclist)
  for process in psutil.process_iter():
    for x in range(ln):
      if proclist[x] == process.name():
        return x
  return -1


def getclock():
  return int(time.time())

def getclockturn(hour, minute):
  dtm = datetime.datetime.fromtimestamp(time.time())
  if dtm.hour > hour or (dtm.hour == hour and dtm.minute > minute):
    dtm = dtm + datetime.timedelta(days=1)
  dtm_off = datetime.datetime(dtm.year, dtm.month, dtm.day, hour, minute, 00)
  print ('GCT   ' + str(dtm_off))
  ts_stop = dtm_off.timestamp()
  # print('Seconds left = ' + str(ts_stop - ts_start))
  return int(ts_stop)


class PowerPlan:
  def __init__(self, printGuids=True):
    len_guid = 36
    output = subprocess.check_output(["powercfg", "-list"])
    if CFG.powercfg_output_decoder is not None:
      output = output.decode(CFG.powercfg_output_decoder)
    lines = str(output).split('\n')

    self.guid_active = None
    self.gglist = [None for _p in CFG.plans]

    for l in lines:
      ldl = l.split(': ')   # Thats main delimiter for parsing 'powercfg -list' output. 'GUID' in left part, GUID in right
      if len(ldl) != 2:
        continue
      if ldl[0].count('GUID') == 0:
        continue
      guid = ldl[1][:len_guid]
      lost = ldl[1][len_guid + 3:]
      # print ('Guid: %s; lost: %s' % (guid, lost))
      ctr = 0
      for p in CFG.plans:
        if lost.startswith(p[0]):
          self.gglist[ctr] = ((guid, p[1]))
          if '*' in lost:
            self.guid_active = ctr
          break
        ctr += 1

    self.ready = None not in self.gglist
    if self.guid_active is None:
      self.guid_active = 0 if len(self.gglist) < 2 else 1
    self.guid_auto = CFG.index_autoplan
    self.ggcount = len(self.gglist)

    if printGuids:
      print ('READY: ' + str(self.ready))
      for i in range(self.ggcount):
        print (self.gglist[i][0] + ': ' + self.gglist[i][1] + ('\t*ACTIVE*' if self.guid_active == i else ''))

  def inited(self):
    return self.ready

  def setActive(self, guid):
    if self.guid_active == guid:
      return False
    # print("changing plan!")
    subprocess.call("powercfg -setactive " + self.gglist[guid][0])
    self.guid_active = guid
    return True

  def __str__(self):
    if self.ready:
      return 'Active: ' + str(self.gglist[self.guid_active])
    else:
      return '-- not inited --'


pp = PowerPlan()

plancolors =  [(200, 200, 247), (120, 255, 120), (255, 165, 000), (255, 000, 000) ] +\
              [(255, 0, 255), (255, 0, 170), (255, 0, 50), (200, 255, 100)]
plancolors = plancolors[:len(CFG.plans)]

guid_images_auto = [ [ ppi.image_up(pc, warn) for pc in plancolors ] for warn in [False, True] ]

clr_acid = (255,255,255)
guid_images_manual = [ [ ppi.image_down(pc, warn) for pc in plancolors ] for warn in [False, True] ]

guid_images_disabled = [ ppi.image_disabled(warn) for warn in [False, True] ]

guid_images_poweroff_unsorted = [ ppi.image_timers(pc) for pc in plancolors ]
guid_images_poweroff = [list(i) for i in zip(*guid_images_poweroff_unsorted)]

time_current = getclock()
print('Tick start: ' + str(time_current))
time_warn = None if CFG.warntime is None else getclockturn(CFG.warntime[0], CFG.warntime[1])
time_night = None if CFG.nighttime is None else getclockturn(CFG.nighttime[0], CFG.nighttime[1])
print('Tick-Beep-Warn): ' + str(time_warn) + '; Tick-Beep-Night: ' + str(time_night))

time2finish = False
PG_NONE, PG_AUTO, PG_DISABLED = None, -2, -1
pick_guid = PG_AUTO

PP_NONE, PP_OFF = -2, -1
pick_poweroff = PP_NONE
poweroff_list = [ 0, 5, 10, 15, 20, 25, 30, 45, 60, 90, 120 ]
PB_MANUAL, PB_NONE = -2, -1
pick_beep = PB_MANUAL
beeps_list = [0, 1, 5, 10, 15, 30, 60, 90, 120]

def exec_func():
  time.sleep(0.5)
  global time_current, time_warn, time_night, time2finish
  global pick_poweroff, pick_guid, pick_beep
  global night_check
  poweroff_timer, poweroff_change, poweroff_doit = None, 0, False
  beepcounter = int(0)
  beepinterval = CFG.beepinterval
  maxpif = len(guid_images_poweroff)-1

  combo = (0, None, False, pp.guid_active)  # overtime, poweroff_time, MODE (disabled/auto/manual), guid
  comboprev = None

  while not time2finish:

    if pick_poweroff is not PP_NONE:
      if pick_poweroff == PP_OFF:
        combo = (combo[0], None, combo[2], combo[3])
        poweroff_timer = -1
      else:
        poweroff_timer = 0 if pick_poweroff == 0 else poweroff_list[pick_poweroff]*60
      pick_poweroff = PP_NONE
      time_warn = None
      time_night = None

    if pick_beep >= 0:
      beepcounter = 0
      beepinterval = beeps_list[pick_beep] * 60
      pick_beep = PB_NONE

    if poweroff_timer is not None:
      if poweroff_timer <= 0:
        poweroff_doit = True
        break
      combo = (combo[0], min(int(poweroff_timer/60), maxpif), combo[2], combo[3])
      poweroff_timer -= CFG.timestep

    if pick_guid == PG_AUTO:
      appidx = check_process(CFG.corrapps)
      combo = (combo[0], combo[1], True, CFG.corrplans[appidx] if appidx != -1 else pp.guid_auto)
    elif pick_guid is not PG_NONE:
      if pick_guid == PG_DISABLED:
        combo = (combo[0], combo[1], None, combo[3])
      else:
        combo = (combo[0], combo[1], False, pick_guid)
      pick_guid = PG_NONE

    if time_warn is not None and time_current > time_warn:
      combo = (1, combo[1], combo[2], combo[3])
      time_warn = None
      winsound.PlaySound(CFG.warnbeepfile, winsound.SND_FILENAME)
    if time_night is not None and time_current > time_night:
      time_night = None
      winsound.PlaySound(CFG.nightbeepfile, winsound.SND_FILENAME)

    # print(combo)
    if combo != comboprev:
      # print('Change!')
      if combo[1] is not None:
        icon.icon = guid_images_poweroff[combo[1]][combo[3]]
      else:
        icon.icon = guid_images_disabled[combo[0]] if combo[2] is None else \
              (guid_images_auto[combo[0]][combo[3]] if combo[2] is True else guid_images_manual[combo[0]][combo[3]])
      pp.setActive(combo[3])
      comboprev = combo

    time.sleep(CFG.timestep)
    time_current += CFG.timestep

    beepcounter += CFG.timestep
    if beepcounter >= beepinterval:
      if poweroff_timer is None:
        winsound.PlaySound(CFG.beepwav, winsound.SND_FILENAME)
      beepcounter = 0

  if poweroff_doit:
    subprocess.call("shutdown -s -t 00")


def set_poweroffpick(tm):
  def func(icon, item):
    global pick_poweroff
    pick_poweroff = -1 if pick_poweroff == tm else tm
  return func
def get_poweroffpick(v):
  def func(item):
    return pick_poweroff == v
  return func

def set_beep(tm):
  def func(icon, item):
    global pick_beep
    pick_beep = -1 if pick_beep == tm else tm
  return func
def get_beep(v):
  def func(item):
    return pick_beep == v
  return func

def changeplan(guid):
  def func():
    global pick_guid
    pick_guid = guid
  return func

def set_appplan(idx, nf):
  def func(icon, item):
    CFG.corrplans[idx] = nf
  return func
def get_appplan(idx, df):
  def func(item):
    return CFG.corrplans[idx] == df
  return func

icon = Icon('PowerPlan')
icon.icon = ppi.image_unknown(False)

item_apps =       item(CFG.caption_apps, menu(
                      *(item(CFG.corrapps[a],
                        menu( *(item(CFG.plans[i][1], set_appplan(a, i), checked=get_appplan(a, i), radio=True) \
                                for i in range(len(CFG.plans))))) for a in range(len(CFG.corrapps)))
                        ))

item_plans =      item(CFG.caption_plans, menu(
                        item(CFG.caption_ignoreplans, changeplan(PG_DISABLED)),
                        *(item(pp.gglist[i][1], changeplan(i)) for i in range(pp.ggcount)),
                        item(CFG.caption_autoplan, changeplan(PG_AUTO))
                      ))

item_poweroff =   item(CFG.caption_poweroff, menu(
                      item(CFG.caption_now, set_poweroffpick(PP_OFF), checked=get_poweroffpick(0), radio=True),
                      *(item(str(poweroff_list[i]) + ' ' + CFG.caption_minutes, set_poweroffpick(i),
                             checked=get_poweroffpick(i), radio=True) for i in range(1, len(poweroff_list)))
                  ))

item_beep = None if CFG.caption_beep is None else item(CFG.caption_beep, menu(
                      *(item(str(beeps_list[i]) + ' ' + CFG.caption_minutes, set_beep(i),
                             checked=get_beep(i), radio=True) for i in range(1, len(beeps_list)))
                  ))

item_exit = None if CFG.caption_exit is None else item(CFG.caption_exit, lambda: icon.stop())

itemlist = [item_apps, item_plans, item_poweroff]
if item_beep is not None:
  itemlist.append(item_beep)
if item_exit is not None:
  itemlist.append(item_exit)

icon.menu = menu(*itemlist)

exec_thread = threading.Thread(target=exec_func, args=())
exec_thread.start()
icon.run()

print ('Terminating... waiting for exec_thread finish')
time2finish = True
exec_thread.join(CFG.timestep + 1)
print ('Terminated. Good Bye!')

# import wmi
# def check_process(proclist):
# c = wmi.WMI()
# for process in c.Win32_Process():
#   if process.Name in proclist:
#     return True
# return False


# def check_process(proclist):
#   for process in psutil.process_iter():
#     if process.name() in proclist:
#       return True
#   return False