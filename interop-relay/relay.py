#!/usr/bin/env python3
# CLI for interacting with interop server.

from __future__ import print_function
import argparse
import getpass
import logging
import sys
import time
import threading
from pymavlink import mavutil
from auvsi_suas.client.client import AsyncClient
from auvsi_suas.proto.interop_api_pb2 import Telemetry




class MavlinkProxy(object):
    """Proxies mavlink packets to the interop server.

    Uses an asynchronous client to enable multiple telemetry to be concurrently
    forwarded so throughput is limited by RTT of the request. Prints request
    rate.
    """
    def __init__(self, client, MavProxy):
        """Receives telemetry over the device and forwards via the client.

        Args:
            device: A pymavlink device name to forward.
            client: Interop Client with which to send telemetry packets.
        """
        self.client = client
        # Create mavlink connection.
        self.mav = mavutil.mavlink_connection('udpin:' + MavProxy, autoreconnect=True)
        self.mav.wait_heartbeat()
        # Protects concurrent access to state.
        self.state_lock = threading.Lock()
        # Track rate of requests.
        self.sent_since_print = 0
        self.last_print = time.time()
        self.healthy = True
        # Periodically print rates.
        self.print_thread = threading.Thread(target=self._print_state)
        self.print_thread.start()

    def proxy(self):
        """Continuously proxy telemetry until an error."""
        while True:
            # Check healthiness.
            with self.state_lock:
                if not self.healthy:
                    return
            # Get packet.
            msg = self.mav.recv_match(type='GLOBAL_POSITION_INT',
                                      blocking=True,
                                      timeout=10.0)
            if msg is None:
                logging.critical(
                    'Did not receive MAVLink packet for over 10 seconds.')
                return
            # Convert to telemetry.
            telemetry = Telemetry()
            telemetry.latitude = self._mavlink_latlon(msg.lat)
            telemetry.longitude = self._mavlink_latlon(msg.lon)
            telemetry.altitude = self._mavlink_alt(msg.alt)
            telemetry.heading = self._mavlink_heading(msg.hdg)
            # Forward via client.
            self.client.post_telemetry(telemetry).add_done_callback(
                self._send_done)

    def _send_done(self, future):
        """Callback executed after telemetry post done."""
        try:
            future.result()
            with self.state_lock:
                self.sent_since_print += 1
        except:
            logging.exception('Failed to post telemetry to interop.')
            with self.state_lock:
                self.healthy = False

    def _print_state(self):
        while True:
            # Check healthiness.
            with self.state_lock:
                if not self.healthy:
                    return

            # Periodic print.
            now = time.time()
            with self.state_lock:
                since_print = now - self.last_print
                logging.info('Telemetry rate: %f',
                            self.sent_since_print / since_print)
                self.sent_since_print = 0
                self.last_print = now
            time.sleep(2.0)

    @classmethod
    def _mavlink_latlon(cls, degrees):
        """Converts a MAVLink packet lat/lon degree format to decimal degrees."""
        return float(degrees) / 1e7

    @classmethod
    def _mavlink_alt(cls, dist):
        """Converts a MAVLink packet millimeter format to decimal feet."""
        return dist * 0.00328084

    @classmethod
    def _mavlink_heading(cls, heading):
        """Converts a MAVLink packet heading format to decimal degrees."""
        return heading / 100.0


def mavlink(client, MavProxy):
    proxy = MavlinkProxy(client, MavProxy)
    proxy.proxy()





if __name__ == '__main__':
    logging.basicConfig(filename= 'AIclient.log', filemode= 'a',format='%(asctime)s-%(levelname)s-%(message)s')
    # Parse command line args.
    parser = argparse.ArgumentParser(description='AUVSI SUAS Interop CLI.')
    parser.add_argument('--url',
                        required=True,
                        help='URL for interoperability.')
    
    parser.add_argument('--password', help='Password for interoperability.')
    
    parser.add_argument('--username',
                        required=True,
                        help='Username for interoperability.')
    
    parser.add_argument('--MavProxy',
                        required=True,
                        help='MavProxy Entry Point')

    # Parse args, get password if not provided.
    args = parser.parse_args()
    if args.password:
        password = args.password
    else:
        password = getpass.getpass('Interoperability Password: ')

    # Create client and dispatch subcommand.
    client = AsyncClient(args.url, args.username, password)
    mavlink(client, args.MavProxy)
