# smolOS by Krzysztof Krystian Jankowski
# pegasusOS by Tanishq Agarwal @047pegasus
# Homepage: http://github.com/047pegasus/pegasusOS
# Source version: 0.4.1d modified at 2023.07.16

import machine
import uos
import gc
import network
import usocket
import utime

class pegasusOS:
    def __init__(self):
        self.name="pegasusOS"
        self.version = "0.4.1d"
        self.turbo = False
        self.files = uos.listdir()
        self.protected_files = { "boot.py", "main.py" }
        self.user_commands = {
            "banner": self.banner,
            "help": self.help,
            "ls": self.ls,
            "cat": self.cat,
            "rm": self.rm,
            "cls": self.cls,
            "stats": self.stats,
            "mhz": self.set_cpu_mhz,
            "turbo": self.toggle_turbo,
            "ed": self.ed,
            "info": self.info,
            "py": self.py,
            "ifconfig" : self.ifconfig,
            "ping" : self.ping
        }

        self.boot()

    def boot(self):
        self.set_cpu_mhz(80)
        self.cls()
        self.welcome()
        while True:
            user_input = input("\npegasus $: ")
            parts = user_input.split()
            if len(parts) > 0:
                command = parts[0]
                if command in self.user_commands:
                    if len(parts) > 1:
                        arguments = parts[1:]
                        self.user_commands[command](*arguments)
                    else:
                        self.user_commands[command]()
                else:
                    self.unknown_function()

    def banner(self):
        print("_____________________________________________________")
        print('''                                        ____   _____ 
                                       / __ \ / ____|
  _ __   ___  __ _  __ _ ___ _   _ ___| |  | | (___  
 | '_ \ / _ \/ _` |/ _` / __| | | / __| |  | |\___ \ 
 | |_) |  __/ (_| | (_| \__ \ |_| \__ \ |__| |____) |
 | .__/ \___|\__, |\__,_|___/\__,_|___/\____/|_____/ 
 | |          __/ |                                  
 |_|         |___/                                   
        ''')
        print("=====================================================")

    def welcome(self):
        print("\n\n\n\n")
        self.banner()
        print("\n")
        self.stats()
        print("\n\n\n\n")
        self.print_msg("Type 'help' for the pegasus manual.")
        print("\n")

    def help(self):
        print(self.name+ " Version "+self.version+" user commands:\n")
        print("\t`ls` - list files\n\t`cat filename` - print file\n\t`info filename` - info about selected file\n\t`rm filename` - remove file\n\t`ed filename` - text editor\n\t`banner` - system banner\n\t`cls` - clear screen\n\t`mhz` 160 - set CPU speed (80-160) in MHz\n\t`stats` - hardware and software information")
        print("\nSystem modified by 047pegasus")
        print("Code available at Github 047pegasus/pegasusOS.")

    def print_err(self, error):
        print("\n\t<!>",error,"<!>")

    def print_msg(self, message):
        print("\n\t->",message)

    def unknown_function(self):
        self.print_err("unknown function. Try 'help'.")

    def set_cpu_mhz(self,freq="80"):
        freq = int(freq)
        if freq >= 80 and freq <= 160:
            machine.freq(freq * 1000000)
            self.print_msg("CPU frequency set to "+str(freq))
        else:
            self.print_err("wrong CPU frequency. Use between 80 and 160 MHz.")

    def toggle_turbo(self):
        if self.turbo:
            self.set_cpu_mhz("80")
        else:
            self.set_cpu_mhz("160")
        self.turbo = not self.turbo

    def stats(self):
        print("Board:",machine.unique_id())
        print("MicroPython:",uos.uname().release)
        print(self.name + ":",self.version,"(size:",uos.stat("main.py")[6],"bytes)")
        print("Firmware:",uos.uname().version)
        print("CPU Speed:",machine.freq()*0.000001,"MHz")
        print("Free/All memory:",gc.mem_free(),"bytes","/", uos.statvfs("/")[1] * uos.statvfs("/")[2], "bytes")
        print("Free space:",uos.statvfs("/")[0] * uos.statvfs("/")[2],"bytes")

    def cls(self):
         print("\033[2J")

    def ls(self):
        for file in uos.listdir():
            file_size = uos.stat(file)[6]
            additional = ""
            if file in self.protected_files: info = "protected system file"
            print(file,"\t", file_size, "bytes", "\t"+additional)

    def info(self,filename=""):
        if filename == "":
            self.print_err("No file")
            return
        additional = ""
        file_size = uos.stat(filename)[6]
        if filename in self.protected_files: additional = "protected system file"
        print(filename,"\t",file_size,"bytes","\t"+additional)


    def cat(self,filename=""):
        if filename == "":
            self.print_err("Failed to open the file.")
            return
        with open(filename,'r') as file:
            content = file.read()
            print(content)

    def rm(self,filename=""):
        if filename == "":
            self.print_err("Failed to remove the file.")
            return
        if filename in self.protected_files:
            self.print_err("Can not remove system file!")
        else:
            uos.remove(filename)
            self.print_msg("File '{}' removed successfully.".format(filename))

    def py(self,filename=""):
        if filename == "":
            self.print_err("Specify a file name to run.")
            return
        exec(open(filename).read())

    def ifconfig(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        def scan_wifi_stations():
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            scan_results = wlan.scan()
            return scan_results

        def connect_to_wifi_station(ssid, password):
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.disconnect()
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                pass
            return wlan.isconnected()
        
        while True:
            # Scan for available Wi-Fi stations
            scan_results = scan_wifi_stations()

            # Display the available stations
            print("Available Wi-Fi Stations:")
            for i, station in enumerate(scan_results):
                print(f"{i+1}. {station[0].decode()}")

            # Prompt the user to select a station
            selected_station = input("Enter the number of the station you want to connect to (or 'q' to quit): ")

            # Exit the loop if the user wants to quit
            if selected_station == 'q':
                break
            
            # Validate the user's selection
            if not selected_station.isdigit() or int(selected_station) < 1 or int(selected_station) > len(scan_results):
                print("Invalid selection. Please try again.")
                continue
            
            selected_station_ssid = scan_results[int(selected_station) - 1][0].decode()

            # Prompt the user to enter the password
            password = input("Enter the password for the selected station: ")

            # Connect to the selected station
            connection_status = connect_to_wifi_station(selected_station_ssid, password)

            # Check if the connection was successful
            if connection_status:
                print("Connection successful!")
                print("Network configuration:")
                print("IP address:", wlan.ifconfig()[0])
                print("Subnet mask:", wlan.ifconfig()[1])
                print("Gateway address:", wlan.ifconfig()[2])
                print("DNS server:", usocket.getaddrinfo("micropython.org", 80)[0][-1][0])

                break
            else:
                print("Connection failed. Please try again.")



    def ping(self, host, count=4, timeout=1):
        addr = usocket.getaddrinfo(host, 0)[0][-1][0]

        print(f"Pinging {host} [{addr}] with {count} packets:")

        for i in range(count):
            sock = usocket.socket()

            start_time = utime.ticks_ms()

            try:
                sock.connect((addr, 80))  # Attempt to establish a TCP connection to port 80
                end_time = utime.ticks_ms()
                elapsed_time = utime.ticks_diff(end_time, start_time)

                print(f"Reply from {addr}: bytes=0 time={elapsed_time}ms")
            except OSError:
                print("Request timed out.")

            sock.close()
    
    # txtEDitor
    # Minimum viable text editor
    def ed(self, filename=""):
        self.page_size = 10
        self.cls()
        print("Welcome to smolEDitor\nA smol text editor for smol operating system\n\nWrite h for help\nq to quit\n\n")
        try:
            with open(filename,'r+') as file:
                print("\nEditing "+filename+" file\n")
                lines = file.readlines()
                line_count = len(lines)
                start_index = 0
                message,error = "",""

                while True:
                    if start_index < line_count:
                        end_index = min(start_index + self.page_size,line_count)
                        print_lines = lines[start_index:end_index]

                        print("-> Page:",start_index % self.page_size,"Lines:",line_count)

                        for line_num,line in enumerate(print_lines,start=start_index + 1):
                            print("{}: {}".format(line_num,line.strip()))

                        if line_count > self.page_size:
                            message = "`b` back,`n` next page\n" + message

                    if not message == "":
                        print("-> ",message)
                    if not error == "":
                        self.print_err(error)
                    message,error = "",""
                    user_ed_input = input("\ned $: ")

                    if user_ed_input in ("q","quit"):
                        break

                    if user_ed_input in ("h","help"):
                        message = "txtEDitor minimum viable text editor\n\n`n` - next",self.page_size,"lines\n`b` - back",self.page_size,"lines\n`n text` - replacing n line with a text\n`a`,`add` - add new line\n`w`,`write`,'save' - write to file\n`h` - this help\n`q` - quit\n"

                    if user_ed_input in ("a","add"):
                        line_count += 1
                        lines.append("")

                    if user_ed_input == "n":
                        if start_index+self.page_size < line_count:
                            start_index += self.page_size
                        else:
                            error = "out of lines in this file."

                    if user_ed_input == "b":
                        if start_index-self.page_size >= 0:
                            start_index -= self.page_size
                        else:
                            error = "out of lines in this file."

                    if user_ed_input in ("w","write","save"):
                        error = "Saving implemented yet"

                    parts = user_ed_input.split(" ",1)
                    if len(parts) == 2:
                        line_number = int(parts[0])
                        new_content = parts[1]

                        if line_number > 0 and line_number < line_count:
                            lines[line_number - 1] = new_content + "\n"
                        else:
                            error = "Invalid line number."

        except OSError:
            if filename == "":
                self.print_err("Provide an existing file name after the `ed` command.")
            else:
                self.print_err("Failed to open the file.")

pegasus = pegasusOS()


