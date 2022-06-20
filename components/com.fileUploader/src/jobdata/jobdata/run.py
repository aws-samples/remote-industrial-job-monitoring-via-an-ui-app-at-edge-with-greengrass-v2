"""
Run jobdata's backend flask instance.
"""

import os

from jobdata import __version__
from jobdata import app
from jobdata import config as cfg
from jobdata.utils import ANSIRequestHandler
from jobdata.utils import basicConfig
from jobdata.utils import initialize
from argparse import ArgumentParser

if os.name == "nt":
    os.system("color")

logger = basicConfig(filename=cfg.LOG)

# See https://stackoverflow.com/a/13318415/14316408 for route mapping.
routes = lambda: {idx.rule: idx.endpoint for idx in app.url_map.iter_rules()}


def main() -> int:
    """Main entry point."""
    logger.info(
        f"Starting backend service v{__version__} session on "
        f"{cfg.HOSTNAME} ({cfg.SESSION})"
    )
    initialize(cfg.DEBUG)
    ANSIRequestHandler.routes = routes()  # type: ignore
    #########################import s3 bucket value############################
    parser = ArgumentParser()
    parser.add_argument('-b', '--bucket_name',
                       type=str,
                       help='S3 bucket name', default='sagemaker-us-west-2-593512547852')
    args = parser.parse_args()

    app.config['s3bucket'] = args.bucket_name
    print('Passed item: ', app.config['s3bucket'])

    app.run(request_handler=ANSIRequestHandler,host='0.0.0.0',port='8081')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
