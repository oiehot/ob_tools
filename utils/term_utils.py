import sys


def fix_term_utf8_problem() -> None:
    """터미널 stdout 에서 한글이 제대로 표시되지 않는 문제를 해결한다.
    """
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8")
