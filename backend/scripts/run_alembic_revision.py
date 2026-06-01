import os
import sys
from alembic.config import Config
from alembic import command

HERE = os.path.dirname(os.path.abspath(__file__))
ALEMBIC_INI = os.path.join(HERE, '..', 'alembic.ini')

def main():
    cfg = Config(ALEMBIC_INI)
    # Ensure script_location is explicit
    migrations_dir = os.path.join(HERE, '..', 'migrations')
    cfg.set_main_option('script_location', migrations_dir)

    # Create an autogenerate revision
    command.revision(cfg, message='production_initial', autogenerate=True)

if __name__ == '__main__':
    main()
