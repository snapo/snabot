# SnaBot is a sample bot for deribit

Most probably the simplest bot for beginners to start with and extend...

only 2 additional packages required:
pip install lomond
pip install pickledb


PickleDB is just a KV store to temporary store values and yes i am not using a dict here.
Lomond is a special crafted websocket connector that is pretty fault tollerant. In case the connection is disrupted, the ip changes, bot gets a disconnect from the server, network is disrupted, too much packet loss... then the bot automatically reconnects without a Interrupt.
