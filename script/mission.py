import os
import csv
import time
import requests

import rospy
import mavros

from mavros_msgs.msg import Waypoint, WaypointList, CommandCode
from mavros_msgs.srv import WaypointPull, WaypointPush, WaypointClear, WaypointSetCurrent


FRAMES = {
    Waypoint.FRAME_GLOBAL: 'GAA',
    Waypoint.FRAME_GLOBAL_REL_ALT: 'GRA',
    Waypoint.FRAME_LOCAL_ENU: 'LOC-ENU',
    Waypoint.FRAME_LOCAL_NED: 'LOC-NED',
    Waypoint.FRAME_MISSION: 'MIS'
}

NAV_CMDS = {
    CommandCode.NAV_LAND: 'LAND',
    CommandCode.NAV_LOITER_TIME: 'LOITER-TIME',
    CommandCode.NAV_LOITER_TURNS: 'LOITER-TURNS',
    CommandCode.NAV_LOITER_UNLIM: 'LOITER-UNLIM',
    CommandCode.NAV_RETURN_TO_LAUNCH: 'RTL',
    CommandCode.NAV_TAKEOFF: 'TAKEOFF',
    CommandCode.NAV_WAYPOINT: 'WAYPOINT',
    # Maybe later i will add this enum to message
    112: 'COND-DELAY',
    113: 'COND-CHANGE-ALT',
    114: 'COND-DISTANCE',
    115: 'COND-YAW',
    177: 'DO-JUMP',
    178: 'DO-CHANGE-SPEED',
    181: 'DO-SET-RELAY',
    182: 'DO-REPEAT-RELAY',
    183: 'DO-SET-SERVO',
    184: 'DO-REPEAT-SERVO',
    201: 'DO-SET-ROI',
}


class WaypointFile(object):
    """Base class for waypoint file parsers"""
    def read(self, file_):
        """Returns a iterable of waypoints"""
        raise NotImplementedError

    def write(self, file_, waypoints):
        """Writes waypoints to file"""
        raise NotImplementedError


class QGroundControlWP(WaypointFile):
    """Parse QGC waypoint file"""

    file_header = 'QGC WPL 120'
    known_versions = (110, 120)

    class CSVDialect(csv.Dialect):
        delimiter = '\t'
        doublequote = False
        skipinitialspace = True
        lineterminator = '\r\n'
        quoting = csv.QUOTE_NONE

    def read(self, file_):
        got_header = False
        for data in csv.reader(file_, self.CSVDialect):
            print(data[0],data)
            if data[0].startswith('#'):
                continue; # skip comments (i think in next format version they add this)

            if not got_header:
                qgc, wpl, ver = data[0].split(' ', 3)
                ver = int(ver)
                if qgc == 'QGC' and wpl == 'WPL' and ver in self.known_versions:
                    got_header = True

            else:
                yield Waypoint(
                    is_current = bool(int(data[1])),
                    frame = int(data[2]),
                    command = int(data[3]),
                    param1 = float(data[4]),
                    param2 = float(data[5]),
                    param3 = float(data[6]),
                    param4 = float(data[7]),
                    x_lat = float(data[8]),
                    y_long = float(data[9]),
                    z_alt = float(data[10]),
                    autocontinue = bool(int(data[11]))
                )

    def write(self, file_, waypoints):
        writer = csv.writer(file_, self.CSVDialect)
        writer.writerow((self.file_header ,))
        for seq, w in enumerate(waypoints):
            writer.writerow((
                seq,
                int(w.is_current),
                w.frame,
                w.command,
                w.param1,
                w.param2,
                w.param3,
                w.param4,
                w.x_lat,
                w.y_long,
                w.z_alt,
                int(w.autocontinue)
            ))

def execute_mission(drone, mission_name='teste'):
    print(f"getting {mission_name}")
    wpreader = QGroundControlWP()
    r = requests.get(f'http://127.0.0.1:8000/api/v1/missions/missions/?missionName={mission_name}', headers={'Authorization': 'Api-Key {}'.format(os.getenv(key='API_URL'))})    
    if len(r.json()):
        mission = r.json()[0]
        missionFile = requests.get(mission['missionFile'], headers={'Authorization': 'Api-Key hOgtypH7.eQM8nQbEUNyQY5gPUQg0IG1WbuopENfz'}).text
        with open('/tmp/missionFile.txt','w') as file:
            file.write(missionFile)
    else:
        print("Mission file not found!")
        return "Mission file not found!"

    dl_missionFile = wpreader.read(open('/tmp/missionFile.txt', 'r'))
    wl = [wp for wp in dl_missionFile]

    print(wl)
    return drone.import_mission(wl)

def exec_mission(drone): 
    return lambda mission_name: execute_mission(drone, mission_name)