import collections
import os.path
import subprocess
import sys
import time

import jinja2

from code2sym import KEYCODE_TO_KEYSYM

PRESS = 'press'
RELEASE = 'release'

MODIFIERS = {
    'Control_L',
    'Control_R',
    'Alt_L',
    'Alt_R',
    'Shift_L',
    'Shift_R',
    'Super_L',
    'Super_R',
}
FLUSH_DELTA = 120
FLUSH_EVENTS = 200


def code_to_sym(keycode):
    if keycode in KEYCODE_TO_KEYSYM:
        return KEYCODE_TO_KEYSYM[keycode]
    return 'keycode%d' % (keycode,)


def handle_key(line):
    parts = line.strip().split()
    assert parts[0] == 'key'
    return parts[1], code_to_sym(int(parts[-1]))


def print_stats_html(output, template, single, combo):
    data = template.render(
        total_events=sum(single.values()),
        total_combo_events=sum(combo.values()),
        single=single,
        combo=combo,
    )
    with open(output, 'w') as fp:
        fp.write(data)
    print(f'Statistics file written {output}')


def main():
    total_events = 0

    freqs_single = collections.Counter()
    freqs_combo = collections.Counter()
    pressed = ()

    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <xinput-id>', file=sys.stderr)
        sys.exit(1)

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__)))
    template = jinja_env.get_template('templates/stats.html')

    last_timestamp = time.time()
    xinput_id = sys.argv[1]
    output = 'stats.html'
    try:
        with subprocess.Popen(
                ['xinput', 'test', xinput_id],
                stdout=subprocess.PIPE, encoding='ascii') as xinput:
            for line in xinput.stdout:
                event, keysym = handle_key(line)
                if event == PRESS:
                    pressed = tuple(sorted(pressed + (keysym,), key=_comb_key))
                elif event == RELEASE:
                    pressed = tuple(
                        k for k in pressed if k != keysym
                    )
                if event == PRESS:
                    freqs_single[keysym] += 1
                    if len(pressed) > 1 and not MODIFIERS.isdisjoint(pressed):
                        freqs_combo[pressed] += 1

                    total_events += 1
                    if (total_events > FLUSH_EVENTS or
                        (time.time() - last_timestamp) > FLUSH_DELTA
                    ):
                        print_stats_html(
                            output, template, freqs_single, freqs_combo)
                        total_events = 0
                        last_timestamp = time.time()
    except KeyboardInterrupt:
        print_stats_html(freqs_single, freqs_combo)


def _comb_key(keysym):
    if keysym in MODIFIERS:
        return (0, keysym)
    return (1, keysym)


if __name__ == '__main__':
    main()
