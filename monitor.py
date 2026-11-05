import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

MAPS = [
    {"name": "Mount Blossom Peak", "place_id": 89188079951257, "url": "https://www.roblox.com/games/89188079951257"},
    {"name": "Sekolah Malam Club", "place_id": 117969282373364, "url": "https://www.roblox.com/games/117969282373364"},
    {"name": "Our Flower Garden", "place_id": 132699740251419, "url": "https://www.roblox.com/games/132699740251419"},
]

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
MESSAGE_FILE = "message_id.txt"
WIB = ZoneInfo("Asia/Jakarta")
UPDATE_INTERVAL_MINUTES = 5

session = requests.Session()
session.headers.update({"User-Agent": "B2F-MAP-LIVE/1.3"})


def get_experience_players(place_id):
    try:
        r = session.get(
            f"https://apis.roblox.com/universes/v1/places/{place_id}/universe",
            timeout=25,
        )
        r.raise_for_status()
        universe_id = r.json()["universeId"]
        r = session.get(
            "https://games.roblox.com/v1/games",
            params={"universeIds": universe_id},
            timeout=25,
        )
        r.raise_for_status()
        games = r.json().get("data", [])
        if games and games[0].get("playing") is not None:
            return int(games[0]["playing"])
    except (requests.RequestException, KeyError, ValueError, TypeError) as exc:
        print(f"Experience player API failed for {place_id}: {exc}")
    return None


def get_public_servers(place_id):
    cursor = None
    seen = set()
    listed_players = 0
    server_count = 0
    pages = 0

    while pages < 20:
        params = {"sortOrder": "Asc", "limit": 100}
        if cursor:
            params["cursor"] = cursor
        r = session.get(
            f"https://games.roblox.com/v1/games/{place_id}/servers/Public",
            params=params,
            timeout=25,
        )
        r.raise_for_status()
        payload = r.json()

        for server in payload.get("data", []):
            server_id = server.get("id")
            if server_id and server_id not in seen:
                seen.add(server_id)
                server_count += 1
                listed_players += int(server.get("playing") or 0)

        cursor = payload.get("nextPageCursor")
        pages += 1
        if not cursor:
            break
        time.sleep(0.15)

    experience_players = get_experience_players(place_id)
    players = listed_players if experience_players is None else max(experience_players, listed_players)

    print(
        f"Place {place_id}: experience={experience_players}, "
        f"listed={listed_players}, selected={players}, servers={server_count}"
    )
    return players, server_count, bool(cursor)


def get_update_times():
    """Return current WIB time and next approximate 5-minute schedule slot."""
    now = datetime.now(WIB).replace(second=0, microsecond=0)
    minutes_to_next = UPDATE_INTERVAL_MINUTES - (now.minute % UPDATE_INTERVAL_MINUTES)
    next_update = now + timedelta(minutes=minutes_to_next)
    return now, next_update


def make_payload(results):
    total_players = sum(item["players"] for item in results)
    total_servers = sum(item["servers"] for item in results)

    updated_at, next_update = get_update_times()
    updated_text = updated_at.strftime("%d %b %Y • %H:%M WIB")
    next_text = next_update.strftime("%d %b %Y • %H:%M WIB")

    sections = []
    for item in results:
        warning = " *(hasil pemindaian server dibatasi API)*" if item["capped"] else ""
        sections.append(
            f"**[{item['name']}]({item['url']})**\n"
            f"👥 Pemain online: **{item['players']}**\n"
            f"🖥️ Server publik terpantau: **{item['servers']}**{warning}"
        )

    description = "\n\n".join(sections)
    description += (
        f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **TOTAL PEMAIN: {total_players}**\n"
        f"🖥️ **TOTAL SERVER TERPANTAU: {total_servers}**"
    )

    return {
        "username": "B2F MAP LIVE",
        "embeds": [{
            "title": "🗺️ B2F MAP LIVE — ROBLOX LIVE MONITOR",
            "description": description,
            "color": 0xF48FB1,
            "footer": {
                "text": (
                    f"Update terakhir • {updated_text}\n"
                    f"Update selanjutnya • sekitar {next_text}"
                )
            },
        }],
        "allowed_mentions": {"parse": []},
    }


def post_or_edit(payload):
    message_id = None
    if Path(MESSAGE_FILE).exists():
        message_id = Path(MESSAGE_FILE).read_text(encoding="utf-8").strip() or None

    if message_id:
        r = session.patch(f"{WEBHOOK}/messages/{message_id}", json=payload, timeout=25)
        if r.status_code != 404:
            r.raise_for_status()
            print(f"Updated Discord message {message_id}")
            return

    r = session.post(WEBHOOK + "?wait=true", json=payload, timeout=25)
    r.raise_for_status()
    new_id = r.json()["id"]
    Path(MESSAGE_FILE).write_text(new_id, encoding="utf-8")
    print(f"Created Discord message {new_id}")


def main():
    results = []
    for game in MAPS:
        print(f"Checking {game['name']}...")
        players, servers, capped = get_public_servers(game["place_id"])
        results.append({
            **game,
            "players": players,
            "servers": servers,
            "capped": capped,
        })
    post_or_edit(make_payload(results))


if __name__ == "__main__":
    main()
