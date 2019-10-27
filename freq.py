import collections
import subprocess

from code2sym import KEYCODE_TO_KEYSYM

PRESS = 'press'
RELEASE = 'release'


def code_to_sym(keycode):
    if keycode in KEYCODE_TO_KEYSYM:
        return KEYCODE_TO_KEYSYM[keycode]
    return 'keycode%d' % (keycode,)


def handle_key(line):
    parts = line.strip().split()
    assert parts[0] == 'key'
    return parts[1], code_to_sym(int(parts[-1]))


def print_stats(single, combo):
    total = sum(single.values())
    print
    print('=' * 80)
    print(f'Single press stats total {total} events:')
    for sym, times in single.most_common():
        print(f'{sym} {times} {100*times/total:.02f}')
    print()
    total = sum(combo.values())
    print(f'Combo press stats, total {total} events:')
    for sym, times in combo.most_common():
        sym = '+'.join(sym)
        print(f'{sym} {times} {100*times/total:.02f}')
    print('=' * 80)
    print()


def main():
    total_events = 0

    freqs_single = collections.Counter()
    freqs_combo = collections.Counter()
    pressed = ()

    try:
        with subprocess.Popen(
                ['xinput', 'test', '11'],
                stdout=subprocess.PIPE, encoding='ascii') as xinput:
            for line in xinput.stdout:
                event, keysym = handle_key(line)
                if event == PRESS:
                    pressed = tuple(sorted(pressed + (keysym,)))
                elif event == RELEASE:
                    pressed = tuple(
                        k for k in pressed if k != keysym
                    )
                if event == PRESS:
                    freqs_single[keysym] += 1
                    if len(pressed) > 1:
                        freqs_combo[pressed] += 1

                    total_events += 1
                    if total_events > 200:
                        print_stats(freqs_single, freqs_combo)
                        total_events = 0
    except KeyboardInterrupt:
        print_stats(freqs_single, freqs_combo)


if __name__ == '__main__':
    main()
