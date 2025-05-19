# specifications

## message types

- `REQ::PUB_KEY` : zmq.REQ
- `REP::PUB_KEY`

## messages

```json
{
  "TYPE" : "REQ::PUB_KEY",
  "TO" : "{DEVICE_ID}",     // or IDs [ "{DEV_ID-0}", "{DEV_ID-1}", ...]
  "FROM" : "{HOST_ID}",
  "HOSTNAME" : "{HOSTNAME}",
  "USERNAME": "{USERNAME}",
  "PUB_KEY": "ecdsa AvX...JmK lab@192...2" // HOST_PUB KEY
}
```
<!-- 
```json
{
    "TYPE" : "CONNECTION::REQ",
    "TO" : "192.168.1.2",
    "FROM" : "{ADDR}",
    "ID" : "JtbmInJmK",
    "PUB_KEY": "ecdsa AvXNoAgJtbmInJmK lab@192.168.1.2" // gerektiğinde
}
```

```json
{
    "REQ" : {
        "PUB_KEY" : {
            "TYPE" : "ecdsa",
            "KEY" : "aklsjflasdj",
            "HOST_NAME" : "user@host"
        },

        "CONNECTION" : {
            "ADDR" : "192.168.1.21"
        }
    }
}
```
-->

## config

```json
{ 
  "ID" : "9876AD",
  "knownDevices":
  {
      "{ID-0}": 
    {
      "ADDR": "192.168.1.24",
      "PUB_KEY": "ecdsa AXb34 lab@192.168.1.24",
      "SHARED":
      {
        "{HASH-0}": "{NAME-0}",
        "{HASH-1}": "{NAME-1}"
      }
    },
      "{ID-1}": 
    {
      "ADDR": "192.168.1.21",
      "PUB_KEY": "ecdsa AIjL= lab@192.168.1.21",
      "SHARED": 
      [
        {"{HASH-0}": "{NAME-0}"},
        {"{HASH-1}": "{NAME-1}"}
      ]
    }
  }
}
```
<!--
```json
{
  "{HOST_ID}": {  <---- değişecek
      "knownDevices": {
      "{ID-0}": {
        "ADDR": "192.168.1.24",
        "PUB_KEY": "ecdsa AXb34 lab@192.168.1.24",
        "SHARED": {
          "{HASH-0}": "{NAME-0}",
          "{HASH-1}": "{NAME-1}"
        }
      },
      "{ID-1}": {
        "ADDR": "192.168.1.21",
        "PUB_KEY": "ecdsa AIjL= lab@192.168.1.21",
        "SHARED": [
          {"{HASH-0}": "{NAME-0}"},
          {"{HASH-1}": "{NAME-1}"}
        ]
      }
    }
  }
}
```

## Ğ

```json
{
  "{MSG_TYPE}": {
    "{ADDR}": "192.168.1.24",
    "{ID}" : "ItbmlzdH"
  },
  "CONNECTION::REQ" : {
    "ADDR": "192.168.1.24",
    "ID" : "ItbmlzdH"
  },
  "CONNECTION::OK": {
    "ADDR": "192.168.1.24",
    "ID" : "ItbmlzdH"
  },
  "REQ::PUB_KEY": {
    "ADDR": "192.168.1.24",
    "ID" : "ItbmlzdH"
  },
  "REP::PUB_KEY": {
    "ADDR": "192.168.1.2",
    "ID" : "JtbmInJmK",
    "PUB_KEY": "ecdsa AvXNoAgJtbmInJmK lab@192.168.1.2"
  }
}
```

```json
{
  "MSG": {
    "TYPE" :"as",
    "{ADDR}": "192.168.1.24",
    "{ID}" : "ItbmlzdH"
  },
  "MSG" : {
    "TYPE" : "CONNECTION::REQ" 
    "ADDR": "192.168.1.24",
    "ID" : "ItbmlzdH"
  },
  "CONNECTION::OK": {
    "TYPE" : "CONNECTION::OK"
    "ADDR": "192.168.1.24",
    "ID" : "ItbmlzdH"
  },
  "MSG" : {
    "TYPE" : "REQ::PUB_KEY"
    "ADDR": "192.168.1.24",
    "ID" : "ItbmlzdH"
  },
    "MSG": {
    "TYPE" : "REP::PUB_KEY": 
    "ADDR": "192.168.1.2",
    "ID" : "JtbmInJmK",
    "PUB_KEY": "ecdsa AvXNoAgJtbmInJmK lab@192.168.1.2"
  },
  "MSG" : {
    "TYPE" : "CONNECTION::REQ",
    "ADDR": "192.168.1.2",
    "ID" : "JtbmInJmK",
    "PUB_KEY": "ecdsa AvXNoAgJtbmInJmK lab@192.168.1.2"
  }
}
```
-->
