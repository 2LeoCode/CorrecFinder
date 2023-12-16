import requests
from typing import TypedDict, cast
import telegram_send
import asyncio
import sys
import re
import time

class Slot(TypedDict):
  ids: str
  start: str
  end: str
  id: int
  title: str

if __name__ == "__main__":
  if len(sys.argv) != 5:
    print(f"usage: {sys.argv[0]} <token> <project-name> <team-id> <day>")
    exit(1)
  token = sys.argv[1]
  project_name = sys.argv[2]
  team_id = sys.argv[3]
  day = sys.argv[4]
  end = day[:-1] + chr(ord(day[-1]) + 1)
  last_notif = cast(float | None, None)
  if not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
    print("day must be in YYYY-MM-DD format")
    exit(1)
  while True:
    try:
      res = requests.get(
        f"https://projects.intra.42.fr/projects/{project_name}/slots.json?team-id={team_id}&start={day}&end={end}",
        headers={ "Cookie": token },
      )
      if res.status_code != 200:
        print(f"error: {res.reason}")
        exit(1)
      res = cast(list[Slot], res.json())
      if len(res):
        print(f"found {len(res)} slots:")
        for slot in res:
          print(f"  - start: {slot['start']}, end: {slot['end']}")
        if last_notif is None or time.time() - last_notif > 60:
          asyncio.run(telegram_send.send(messages=[f"Corrections available !", *[
            f"start: {slot['start']}, end: {slot['end']}" for slot in res
          ]]))
          last_notif = time.time()
      time.sleep(1)
    except Exception as e:
      print(e)
      exit(1)
