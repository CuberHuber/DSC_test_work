import logging


class LogFactory:

    DEFAULT_LOGGER_CONFIG: dict = {
            'log_to_screen': True,
            'log_to_file': False,
            'log_file_path': 'log.txt',
            'level': 'INFO',
            'log_formate': '%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s',
        }

    def __new__(cls, config: dict) -> logging.Logger:

        config = {
            **cls.DEFAULT_LOGGER_CONFIG,
            **config,
        }

        log = logging.getLogger(__name__)
        log.setLevel(getattr(logging, config['level']))

        logFormatter = logging.Formatter(config['log_formate'])

        if type(config['log_to_screen']) is bool and config['log_to_screen']:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            log.addHandler(consoleHandler)

        if type(config['log_to_file']) is bool and config['log_to_file']:
            fileHandler = logging.FileHandler(config['log_file_path'])
            fileHandler.setFormatter(logFormatter)
            log.addHandler(fileHandler)

        return log
