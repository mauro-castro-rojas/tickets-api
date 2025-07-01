def log(message: str):
    with open("logs.log", "a") as logfile:
        logfile.write(f"{message}\n")