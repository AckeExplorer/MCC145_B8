# Copyright (c) Acconeer AB, 2022
# All rights reserved

import os
import sys
import datetime
import asyncio
import winsdk.windows.devices.geolocation as wdg

import acconeer.exptool as et


def main():
    interrupt_handler = et.utils.ExampleInterruptHandler()
    args = et.a111.ExampleArgumentParser().parse_args()
    et.utils.config_logging(args)

    filename = "data.h5"
    # if os.path.exists(filename):
    #     print("File '{}' already exists, won't overwrite".format(filename))
    #     sys.exit(1)

    client = et.a111.Client(**et.a111.get_client_args(args))

    config = et.a111.EnvelopeServiceConfig()
    config.sensor = args.sensors
    config.update_rate = 120

    session_info = client.setup_session(config)

    recorder = et.a111.recording.Recorder(sensor_config=config, session_info=session_info)

    client.start_session()
    # with open("test.csv","w") as f:
    #     f.write("date,location\n")

    async def getCoords():
        locator = wdg.Geolocator()
        pos = await locator.get_geoposition_async()
        return [pos.coordinate.latitude, pos.coordinate.longitude]


    def getLoc():
        try:
            return asyncio.run(getCoords())
        except PermissionError:
            print("ERROR: You need to allow applications to access you location in Windows settings")
    n = 10000
    i = 0
    while not interrupt_handler.got_signal or i == n:
        data_info, data = client.get_next()
        recorder.sample(data_info, data)
        #with open("test.csv","a") as f:
         #   f.write("{},{}\n".format(datetime.datetime.utcnow(),getLoc()))
        print("Sampled {:>4}/{}".format(i + 1, n), end="\r", flush=True)
        i +=1


    client.disconnect()

    record = recorder.close()
    print(filename)
    #os.makedirs(os.path.dirname(filename), exist_ok=True)

    et.a111.recording.save(filename, record)
    print("Saved to '{}'".format(filename))


if __name__ == "__main__":
    main()
