# -*- coding: utf-8 -*-


USER_WITH_HYPERLINK = "<https://atcoder.jp/users/{0}|{0}>"


USER_WITH_CONTEST_RESULT_HYEPER_LINK = (
    "atcoder.jp/contests/abc{no}/standings?watching={name}:{name}>"
)


MEMBER_FORMAT = """\
--- member ---
{}
-----------------\
"""


RANKING_FORMAT = """\
1st: :crown:<https://atcoder.jp/users/{0}|{0}>:crown: ({1} point)
2nd: <https://atcoder.jp/users/{0}|{0}> ({1} point)
3rd: <https://atcoder.jp/users/{0}|{0}> ({1} point)
4th: <https://atcoder.jp/users/{0}|{0}> ({1} point)
5th: <https://atcoder.jp/users/{0}|{0}> ({1} point)
6th: <https://atcoder.jp/users/{0}|{0}> ({1} point)
7th: <https://atcoder.jp/users/{0}|{0}> ({1} point)
8th: <https://atcoder.jp/users/{0}|{0}> ({1} point)
9th: <https://atcoder.jp/users/{0}|{0}> ({1} point)
10th: <https://atcoder.jp/users/{0}|{0}> ({1} point)
""".split(
    "\n"
)


CONTEST_RESULT_FORMAT = f"""\
|{'name':^24} | {'rate':^35} | {'perf':^10} |
"""


CONTEST_USER_RESULT_FORMAT = "{} {} {:^10}\n"


AWARD_FORMAT = ":confetti_ball: {} became a {} coder. :clap:"


def visualize_ranking(ranking: list[tuple], order_limit=3) -> str:
    if ranking:
        return "\n".join(
            fmt.format(*rank)
            for rank, fmt in zip(ranking[:order_limit], RANKING_FORMAT)
        )
    else:
        return "No one is here... :sweat_smile:"


def display_member(member: list) -> str:
    return MEMBER_FORMAT.format(
        "\n".join(USER_WITH_HYPERLINK.format(user) for user in member)
    )


def display_archiver(name: str, contest_no: int | str) -> str:
    return (
        f"<https://atcoder.jp/contests/{contest_no}/standings?watching={name}|{name}>"
    )


def whole_space(string: str, length: int) -> int:
    from math import ceil, floor

    if length <= len(string):
        return string
    else:
        space = (length - len(string)) / 2
        return " " * ceil(space) * 2 + string + " " * floor(space) * 2


def display_result(results) -> str:
    if results:
        return CONTEST_RESULT_FORMAT + "".join(
            CONTEST_USER_RESULT_FORMAT.format(
                whole_space(name, 15),
                whole_space(f"{old} -> {new} ({new-old:+})", 21),
                perf,
            )
            for name, old, new, perf in results
        )
    else:
        return "No one participated... :cry:"
