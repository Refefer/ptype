import sys
if sys.version_info.major == 2:
    from itertools import izip
else:
    izip = zip

