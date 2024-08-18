import serial
ser = serial.Serial("/dev/ttyACM0", 115200)

counter = 0
counter_max=1000
while counter<counter_max:
    cc=str(ser.readline().decode("utf-8").strip())
    print(cc)
    with open("out.txt", "a") as myfile:
        myfile.write(cc+"\n")     
    counter=counter+1
