from cx_Freeze import setup, Executable
 
setup(
    name = "keithnum_client",
    version = "0.1",
    description = "distributed computing client used to search for Keith Numbers",
    executables = [Executable("client_repfibdigit.py")]
    )
