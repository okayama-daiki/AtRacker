# -*- coding: utf-8 -*-


import os
import platform
import re
from time import sleep
from datetime import datetime

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from atcoder_awarder.libs.msg import HELP_MESSAGE
from atcoder_awarder.libs.visualizer import (
    visualize_ranking,
    display_member,
    display_result,
    AWARD_FORMAT,
    USER_WITH_HYPERLINK,
)
from atcoder_awarder.libs.contestant import Contestant

load_dotenv()


BOT_ID = "U03L1DZ1BAT"


app = App(token=os.environ["SLACK_BOT_TOKEN"])


running = False
not_sleep = True


@app.message(f"<@{BOT_ID}> activate")
def _(message, say):
    global running, not_sleep
    not_sleep = True
    if running:
        say("already activated :dash:")
        return
    running = True
    say("start to monitor the rating fluctuation")
    while running and not_sleep:
        print("periodic execution: ", datetime.now())
        if (
            no := Contestant.identify_latest_abc_holding_number()
        ) != Contestant.latest_abc_holding_number:
            Contestant.latest_abc_holding_number = no
            Contestant.update()
            results = Contestant.generate_specific_contest_result(no)
            changed = Contestant.detect_color_change(results)
            say(f"results for <https://atcoder.jp/contests/abc{no}|abc{no}>")
            say(display_result(results))
            if changed:
                say("<!channel> Congratulations! :tada:")
                for change in changed:
                    say(AWARD_FORMAT.format(*change))
        sleep(1800)


@app.message(f"<@{BOT_ID}> deactivate")
def _(message, say):
    global running, not_sleep
    if not_sleep:
        say("stop to monitor the rating fluctuation")
        not_sleep = False
        running = False
    else:
        say("the system to monitor the rating fluctuation is not running :zzz:")


@app.message(f"<@{BOT_ID}> status")
def _(message, say):
    say("running ::dash" if running else "sleeping :zzz:")


@app.message(f"<@{BOT_ID}> member")
def member(message, say):
    say(display_member(Contestant.member))


@app.message(f"<@{BOT_ID}> result")
def _(message, say):
    no = re.findall(r"result .*", message["text"])[0][7:]
    results = Contestant.generate_specific_contest_result(no)
    say(f"results for <https://atcoder.jp/contests/abc{no}|abc{no}>")
    say(display_result(results))


@app.message(f"<@{BOT_ID}> ranking -h")
def _(message, say):
    say(
        ":unamused: Highest rate ranking:\n"
        + visualize_ranking(Contestant.rank_contestants_by_highest_rating())
    )


@app.message(f"<@{BOT_ID}> ranking")
def _(message, say):
    say(
        "Current rate ranking :face_with_monocle:\n"
        + visualize_ranking(Contestant.rank_contestants_by_current_rating())
    )


@app.message(f"<@{BOT_ID}> add")
def _(message, say):
    for new in re.findall(r"add .*", message["text"])[0][4:].split():
        try:
            Contestant(new)
            say(f"Welcome {USER_WITH_HYPERLINK.format(new)}! :thumbsup:")
        except Exception as e:
            say(str(e))


@app.message(f"<@{BOT_ID}> del")
def _(message, say):
    for delete in re.findall(r"del .*", message["text"])[0][4:].split():
        try:
            Contestant.del_contestant(delete)
            say(f"Bye {delete} :wave:")
        except ValueError as e:
            say(str(e))


@app.message(f"<@{BOT_ID}> help")
def _(message, say):
    say("What do you want me to do?")
    say(HELP_MESSAGE)


@app.message(f"<@{BOT_ID}> platform")
def _(message, say):
    say(platform.platform())


@app.message(f"<@{BOT_ID}> save")
def _(message, say):
    print(Contestant.member.keys())
    say("Output the list of members to the console, check the administrator's console")


@app.message(f"<@{BOT_ID}> quit")
def _(message, say):
    say("Bye")
    os._exit(0)


@app.message(rf"<@{BOT_ID}> .*")
def _(message, say):
    say("Invalid command, please type help")


@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
