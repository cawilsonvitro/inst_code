#region imports
from instutil import inst_util as iu
import socket
#endregion


test_server = iu.tcp_multiserver("config.json","10.40.0.155",5051,None)
test_server.SQL_startup()
test_server.server()
