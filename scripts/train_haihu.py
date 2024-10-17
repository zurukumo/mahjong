import questionary

from core.haihu_trainer import HaihuTrainer
from core.mode import Mode

if __name__ == '__main__':
    mode = questionary.select('Mode?', choices=[mode.value for mode in Mode]).ask()

    HaihuTrainer(mode=Mode(mode))
