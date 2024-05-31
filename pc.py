from pylsl import StreamInfo, StreamOutlet
import websocket
import socket
import time
import datetime
import math

def calculate_bytes_per_second(data_size, elapsed_time):
    bytes_per_second = data_size / elapsed_time
    return bytes_per_second

def calculate_samples_per_second(sample_size, elapsed_time):
    samples_per_second = sample_size / elapsed_time
    return samples_per_second

strean_name = 'ORIC'
data = StreamInfo(strean_name, 'EEG', 8, 250, 'float32', 'uid007')
outlet = StreamOutlet(data)
ws = websocket.WebSocket()
print("Trying to connect")
ws.connect("ws://"+socket.gethostbyname("oric.local")+":81")
data_size = 0
sample_size = 0
start_time = time.time()
blockSize = 32
previousSampleNumber = -1
previousTimeStamp = -1
previousData = []

print(strean_name, "LSL Stream started!")

while(1):

    data = ws.recv()
    data_size += len(data)

    current_time = time.time()
    elapsed_time = current_time - start_time

    # if elapsed_time >= 1.0:
    #     bytes_per_second = calculate_bytes_per_second(data_size, elapsed_time)
    #     print(f"Bytes per second: {bytes_per_second} BPS")
    #     data_size = 0  # Reset data size
    #     start_time = current_time

    if elapsed_time >= 10.00:
        samples_per_second = calculate_samples_per_second(sample_size, elapsed_time)
        # Get the current local time
        local_time = datetime.datetime.now()

        # Extract hours, minutes, and seconds
        hours = local_time.hour
        minutes = local_time.minute
        seconds = local_time.second

        print(f"Local Time: {hours:02d}:{minutes:02d}:{seconds:02d} Samples per second: {math.ceil(samples_per_second)} SPS")
        sample_size = 0  # Reset data size
        start_time = current_time

    if data and (type(data) is list or type(data) is bytes):
        # print("Packet size: ", len(data), "Bytes")
        for blockLocation in range(0, len(data), blockSize):
            sample_size += 1
            block = data[blockLocation:blockLocation + blockSize]
            # data_hex = ":".join("{:02x}".format(c) for c in data)
            timestamp = int.from_bytes(block[0:4], byteorder='little')
            sample_number = int.from_bytes(block[4:8], byteorder='little')
            channel_data = []
            for channel in range(0, 8):
                channel_offset = 8 + (channel * 3)
                sample = int.from_bytes(block[channel_offset:channel_offset + 3], byteorder='big', signed=True)
                channel_data.append(sample)

            if previousSampleNumber == -1:
                previousSampleNumber = sample_number
                previousTimeStamp = timestamp
                previousData = channel_data
            else:
                if sample_number - previousSampleNumber > 1:
                    print("Sample Lost")
                    exit()
                elif sample_number == previousSampleNumber:
                    print("Duplicate sample")
                    exit()
                else:
                    # print(timestamp - previousTimeStamp)
                    previousTimeStamp = timestamp
                    previousSampleNumber = sample_number
                    previousData = channel_data

            # outlet.push_sample(channel_data)

            if(all(v == 0 for v in channel_data[:3]) and all(v > 0 for v in channel_data[4:])):
                print("Blank Data: ",timestamp, sample_number, channel_data[0], channel_data[1], channel_data[2], channel_data[3], channel_data[4], channel_data[5], channel_data[6], channel_data[7])
                exit()
            else:
                print("EEG Data: ",timestamp, sample_number, channel_data[0], channel_data[1], channel_data[2], channel_data[3], channel_data[4], channel_data[5], channel_data[6], channel_data[7])
                outlet.push_sample(channel_data)

