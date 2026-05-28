"""Shared runtime settings for Recap viewer automation."""

from urllib.parse import urlparse

VIEWER_URL = (
    "https://cdn.recap-staging.autodesk.com/viewer/current/index.html?"
    "file=https://rs-asrd-nas.ads.autodesk.com/datasets/rctp_v1.0/"
    "AutodeskReCapSampleProject_realview/AutodeskReCapSampleProject.rcp"
    "&env=local&src=local"
)

_parsed_viewer_url = urlparse(VIEWER_URL)
VIEWER_ORIGIN = f"{_parsed_viewer_url.scheme}://{_parsed_viewer_url.netloc}"
LOCAL_NETWORK_ACCESS_PERMISSION = "local-network-access"

DEFAULT_TIMEOUT_MS = 120_000
SEARCH_FILTER_DELAY_MS = 800
STACK_PROCESS_DELAY_MS = 500
