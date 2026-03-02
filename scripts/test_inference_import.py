import sys
import traceback

sys.path.insert(0, r'c:\Workspace\RakshNetra')

try:
    import ai.inference as inf
    print('IMPORT_OK', inf.__name__)
except Exception as e:
    traceback.print_exc()
    print('IMPORT_ERR', e)
