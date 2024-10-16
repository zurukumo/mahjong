import questionary

from core.paihu_parser import Mode, PaihuParser

if __name__ == '__main__':
    mode = questionary.select('Mode?', choices=[mode.value for mode in Mode]).ask()
    max_case = int(questionary.text('Max Case?', default='150000').ask())

    PaihuParser(mode=Mode(mode), max_case=max_case, debug=False)
