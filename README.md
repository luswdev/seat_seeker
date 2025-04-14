# Seat Seeker

## Live Demo
join the channel: [Seat Seeker](https://t.me/qwer_tks)

## install guide
0. setup python environment (see requirements.txt)
1. setup d-bus policy for `com.luswdev.seatseeker`
2. start main.py
3. send d-bus command for configs setting

## usage
- config template (please goto [ticketplus](https://ticketplus.com.tw/) to craw more information)
```yaml
event:
  name: "Event Name"
  time: [ "event time" ]
  arena: "event arena"
  url: "https://ticketplus.com.tw/activity/{event_id}"

api_url:
  event_url: "https://apis.ticketplus.com.tw/config/api/v1/getS3?path=event/{event_id}/event.json"
  session_url: "https://apis.ticketplus.com.tw/config/api/v1/getS3?path=event/{event_id}/sessions.json"
  area_url: "https://apis.ticketplus.com.tw/config/api/v1/get?ticketAreaId={ticketAreaId}&productId={productId}&&_={}"
```

- add config
```bash
dbus-send --system --dest=com.luswdev.seatseeker --print-reply /com/luswdev/seatseeker com.luswdev.seatseeker.addConfig string:"/path/to/config" string:"config_tag" string:"send_to_channel_id" boolean:{need_send_header?}
```

- delete config
```bash
dbus-send --system --dest=com.luswdev.seatseeker --print-reply /com/luswdev/seatseeker com.luswdev.seatseeker.delConfig string:"config_tag"
```
