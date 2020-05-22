from lomond import WebSocket
from lomond.persist import persist
import json
import hmac
import base64
import time
from datetime import datetime
from pprint import pprint
import pathlib
import pickledb



confpath = pathlib.Path(__file__).parent.absolute()

### Prepare temp db ###
db = pickledb.load(str(confpath) + '/database.db', False)



with open(str(confpath) + '/config.json') as json_file:
    json_data = json.load(json_file)
    if json_data['test'] == 1:
        user = json_data['idtest']
        password = json_data['secrettest']
        server =  json_data['servertest']
        msgsec = 0.5
        rsec = 2
    else:
        user = json_data['id']
        password = json_data['secret']
        server =  json_data['server']
        msgsec = 0.2
        rsec = 5
    instruments =  json_data['instruments']
    botname =  json_data['botname']
    version =  json_data['version']
    log =  json_data['log']
    trade =  json_data['trade']
    nonce =  json_data['nonce']
    json_file.close()


print("T: " + str(int(round(time.time() * 1000))) + " - Configuration successfully read, starting strategy: " + botname + " " + version + "...")

websocket = WebSocket(server)

for event in persist(websocket, poll=msgsec):
    
    #### On Connect handler ####
    if event.name == "ready":
      
      print("T: " + str(int(round(time.time() * 1000))) + " - Bot Connecting....")
      datapool = {}
      websocket.send_json({"jsonrpc":"2.0","id":0,"method":"public/auth","params":{"grant_type":"client_credentials","client_id":user,"client_secret":password,"nonce": nonce}})
      websocket.send_json({"jsonrpc":"2.0","id":1,"method":"public/disable_heartbeat","params":{}})
      websocket.send_json({"jsonrpc":"2.0","id":2,"method":"public/hello","params":{"client_name":botname,"client_version":version}})
      websocket.send_json({"jsonrpc":"2.0","method":"public/subscribe","id":3,"params":{"channels": ["platform_state"]}})
      authend = time.time()
      poller = 0
      botready = 0
      logready = 0
      logheader = 0
      requestlimit = 0
  
   #### Message Stream Handler ####
    elif event.name == "text":
      if "id" in event.json:
        eventid = int(event.json["id"])
        if eventid == 0:
          print("T: " + str(int(round(time.time() * 1000))) + " - Auth/Reauth done...")
        elif eventid == 1:
          print("T: " + str(int(round(time.time() * 1000))) + " - Disabled Heartbeat...")
        elif eventid == 2:
          print("T: " + str(int(round(time.time() * 1000))) + " - Sent Bot ID to Deribit...")
        elif eventid == 3:
          print("T: " + str(int(round(time.time() * 1000))) + " - Subscribed Platform State...")
        elif (eventid // 10) == 1 or (eventid // 10) == 2:
          iname = event.json["result"]["instrument_name"]
          db.set(str(eventid) + "-" + iname +'-total_profit_loss', event.json["result"]["total_profit_loss"])
          db.set(str(eventid) + "-" + iname +'-size_currency', event.json["result"]["size_currency"])
          db.set(str(eventid) + "-" + iname +'-size', event.json["result"]["size"])
          db.set(str(eventid) + "-" + iname +'-settlement_price', event.json["result"]["settlement_price"])
          db.set(str(eventid) + "-" + iname +'-realized_profit_loss', event.json["result"]["realized_profit_loss"])
          db.set(str(eventid) + "-" + iname +'-open_orders_margin', event.json["result"]["open_orders_margin"])
          db.set(str(eventid) + "-" + iname +'-mark_price', event.json["result"]["mark_price"])
          db.set(str(eventid) + "-" + iname +'-maintenance_margin', event.json["result"]["maintenance_margin"])
          db.set(str(eventid) + "-" + iname +'-leverage', event.json["result"]["leverage"])
          db.set(str(eventid) + "-" + iname +'-initial_margin', event.json["result"]["initial_margin"])
          db.set(str(eventid) + "-" + iname +'-index_price', event.json["result"]["index_price"])
          db.set(str(eventid) + "-" + iname +'-floating_profit_loss', event.json["result"]["floating_profit_loss"])
          db.set(str(eventid) + "-" + iname +'-estimated_liquidation_price', event.json["result"]["estimated_liquidation_price"])
          db.set(str(eventid) + "-" + iname +'-delta', event.json["result"]["delta"])
          db.set(str(eventid) + "-" + iname +'-average_price', event.json["result"]["average_price"])
        elif (eventid // 10) == 3 or (eventid // 10) == 4:
          iname = event.json["result"]["instrument_name"]
          db.set(str(eventid) + "-" + iname +'-volume_usd', event.json["result"]["stats"]["volume_usd"])
          db.set(str(eventid) + "-" + iname +'-volume', event.json["result"]["stats"]["volume"])
          db.set(str(eventid) + "-" + iname +'-price_change', event.json["result"]["stats"]["price_change"])
          db.set(str(eventid) + "-" + iname +'-low', event.json["result"]["stats"]["low"])
          db.set(str(eventid) + "-" + iname +'-high', event.json["result"]["stats"]["high"])
          db.set(str(eventid) + "-" + iname +'-state', event.json["result"]["state"])
          db.set(str(eventid) + "-" + iname +'-settlement_price', event.json["result"]["settlement_price"])
          db.set(str(eventid) + "-" + iname +'-open_interest', event.json["result"]["open_interest"])
          db.set(str(eventid) + "-" + iname +'-min_price', event.json["result"]["min_price"])
          db.set(str(eventid) + "-" + iname +'-max_price', event.json["result"]["max_price"])
          db.set(str(eventid) + "-" + iname +'-mark_price', event.json["result"]["mark_price"])
          db.set(str(eventid) + "-" + iname +'-last_price', event.json["result"]["last_price"])
          db.set(str(eventid) + "-" + iname +'-index_price', event.json["result"]["index_price"])
          db.set(str(eventid) + "-" + iname +'-estimated_delivery_price', event.json["result"]["estimated_delivery_price"])
          db.set(str(eventid) + "-" + iname +'-best_bid_price', event.json["result"]["best_bid_price"])
          db.set(str(eventid) + "-" + iname +'-best_bid_amount', event.json["result"]["best_bid_amount"])
          db.set(str(eventid) + "-" + iname +'-best_ask_price', event.json["result"]["best_ask_price"])
          db.set(str(eventid) + "-" + iname +'-best_ask_amount', event.json["result"]["best_ask_amount"])
        elif eventid == 1000:
          print("T: " + str(int(round(time.time() * 1000))) + " - Did a buy...")
        elif eventid == 2000:
          print("T: " + str(int(round(time.time() * 1000))) + " - Did a sell...")
        else:
          #print("T: " + str(int(round(time.time() * 1000))) + " - Unknown Event ID - " + str(event.json))
          print(eventid)
          
        
      #### Capture here all params that are delivered to us via subsciprtion ####
      elif "method" in event.json:
        if event.json["method"] == "subscription":
          if event.json["params"]["channel"] == "platform_state":
            locked = event.json["params"]["data"]["locked"]
      else:
        print("T: " + str(int(round(time.time() * 1000))) + " - Probably uncaught Message...")









    #### Schuled Tasks #####
    elif event.name == "poll":
      ############# Work every 0.2s and on testnet every 0.5s #############
      poller += 1

      ### Get Data on our positions ###
      for n, i in enumerate(instruments):
        websocket.send_json({"jsonrpc":"2.0","id":n + 10,"method":"private/get_position","params":{"instrument_name":i + "-PERPETUAL"}})
        websocket.send_json({"jsonrpc":"2.0","id":n + 30,"method":"public/ticker","params":{"instrument_name":i + "-PERPETUAL"}})





      ############# Work every   1 seconds ############
      if poller % (rsec * 1) == 0:
        if locked == False and trade == 1:
          if botready == 1:
            if requestlimit < rsec:
              for n, i in enumerate(instruments):
                index = db.get(str(10) + "-" + i + "-PERPETUAL" +'-index_price')

                print(   "T: " + str(int(round(time.time() * 1000))) + \
                      " - Inst: " + i + \
                      " - Index Price: " + str(index) + \
                      " - B: " + botname + " " + str(version))
          else:
            print("T: " + str(int(round(time.time() * 1000))) + " - 5 Second warmup, waiting for bot...")
        else:  
          print("T: " + str(int(round(time.time() * 1000))) + " - Platform is currently locked or Trade disabled in config...")
        requestlimit = 0
      #################################################






      ############# Work every   5 seconds ############
      if poller % (rsec * 5) == 0:
        if botready == 0 and trade == 1:
          print("T: " + str(int(round(time.time() * 1000))) + " - Bot is ready starting to trade...")
        botready = 1
        if logready == 0 and log == 1:
          print("T: " + str(int(round(time.time() * 1000))) + " - Log is ready starting to trade...")
        logready = 1
      #################################################






      ############# Work every 180 seconds + Re-Read Config file + Reset Counter ############
      if poller % (rsec * 30) == 0:
        poller = 1
        ### Re-Authenticate Every 3 min ###
        websocket.send_json({"jsonrpc":"2.0","id":0,"method":"public/auth","params":{"grant_type":"client_credentials","client_id":user,"client_secret":password,"nonce": nonce}})

        ### Re-Apply Configuration ###
        with open(str(confpath) + '/config.json') as json_file:
          json_data = json.load(json_file)
          if json_data['test'] == 1:
            user = json_data['idtest']
            password = json_data['secrettest']
            server =  json_data['servertest']
            msgsec = 0.5
          else:
            user = json_data['id']
            password = json_data['secret']
            server =  json_data['server']
            msgsec = 0.2
          instruments =  json_data['instruments']
          botname =  json_data['botname']
          nonce =  json_data['nonce']
          json_file.close()
        print("T: " + str(int(round(time.time() * 1000))) + " - Read Config file...")
      #################################################
