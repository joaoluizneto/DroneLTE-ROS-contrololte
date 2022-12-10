#! /usr/bin/env python
# Import ROS.
import rospy
from ccsclient import ccsWebsocketReceiver
from mission import exec_mission
import os

# Import the API.
from iq_gnc.py_gnc_functions import *
# To print colours (optional).
from iq_gnc.PrintColours import *

#arm = getattr(drone, "arm")

def main():
    # Initializing ROS node.
    rospy.init_node("drone_control_over_network")

    # Create an object for the API.
    drone = gnc_api()

    # Wait for FCU connection.
    drone.wait4connect()
    # Wait for the mode to be switched.
    #drone.wait4start()

    # Create local reference frame.
    drone.initialize_local_frame()

    ccscli = ccsWebsocketClient(
        api_url="ws://{api_url}/ws/robot/{drone_name}/".format(
			api_url=os.getenv(key='API_URL'),
			drone_name=os.getenv(key='DRONE_NAME')
		),
        headers={'X-DroneApiKey':os.getenv(key='DRONE_API_KEY')},
        )
    rospy.loginfo(CGREEN2 + "Begin to receive commands." + CEND)
    ccscli.start_receiver(
        handlers = {
            'arm'            : drone.arm, 
            'takeoff'        : drone.takeoff,
            'set_mode'       : drone.set_mode,
            'set_destination': drone.set_destination,
            'set_heading'    : drone.set_heading,
            'land'           : drone.land,
            'set_speed'      : drone.set_speed,
            'exec_mission'   : exec_mission(drone)
        }
    )
if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Crtl-C getting out...")
        except ConnectionRefusedError:
            print("Connection Refused at server, retrying in 3 seconds...")
            rospy.sleep(3)
            continue
        except BrokenPipeError:
            print("Broken Pipe, retying...")
            rospy.sleep(0.5)
            continue

