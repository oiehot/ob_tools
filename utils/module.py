import imp
import sys


def reload_all_modules(prefix=None):
    """모든 모듈들을 Reload 한다.
    prefix가 앞쪽에 붙은 모듈명을 대상으로 한다.

    :param str prefix: 필터링 할 모듈의 prefix.

    사용 예:
        >>> reload_all_modules("oiehot")
    """

    mods = sys.modules
    # ! 파이썬 2.7에서 reload시 발생하는 상속 type문제를 해결하기 위해서 모듈의 reload 순서를 뒤집는다:
    # list(reversed(sorted(a.keys())))
    # for idx, mod in enumerate(reversed(mods)):
    for mod in list(reversed(sorted(mods.keys()))):
        if prefix:
            if mod.startswith(prefix):
                if sys.modules[mod]:
                    print("reload: %s" % mod)
                    # try:
                    # reload(sys.modules[mod]) # Python 2.7
                    imp.reload(sys.modules[mod])
                    # except Exception, e:
                    #     print('reload: %s => failed: %s' % (mod, str(e)) )
        else:
            if sys.modules[mod]:
                print("reload: %s" % mod)
                # try:
                # reload(sys.modules[mod]) # Python 2.7
                imp.reload(sys.modules[mod])
                # except Exception, e:
                #     print('reload: %s => failed: %s' % (mod, str(e)) )


#     print( [m for m in sys.modules if m.startswith('oiehot.')] )


def unload_all_modules(prefix=None):
    """모든 모듈들을 Unload 한다.
    prefix가 앞쪽에 붙은 모듈명을 대상으로 한다.

    :param str prefix: 필터링 할 모듈의 prefix.

    사용 예:
        >>> unload_all_modules("oiehot")
    """
    # ! 마야 파이썬 2.7 reload에서 상속문제가 발생하여
    # ! unload 하는 스크립트를 작성함.
    mods = sys.modules
    for mod in list(reversed(sorted(mods.keys()))):
        if prefix:
            if mod.startswith(prefix):
                if sys.modules[mod]:
                    print("unload: %s" % mod)
                    try:
                        del sys.modules[mod]
                    except Exception as e:
                        print("unload: %s => failed: %s" % (mod, str(e)))
        else:
            if sys.modules[mod]:
                print("unload: %s" % mod)
                try:
                    del sys.modules[mod]
                except Exception as e:
                    print("unload: %s => failed: %s" % (mod, str(e)))
