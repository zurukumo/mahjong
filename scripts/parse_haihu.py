import questionary

from core.haihu_parser import HaihuParser
from core.mode import Mode

if __name__ == '__main__':
    mode = questionary.select('mode?', choices=[mode.value for mode in Mode]).ask()
    max_case = int(questionary.text('max_case?', default='150000').ask())

    HaihuParser(mode=Mode(mode), max_case=max_case, debug=False)
