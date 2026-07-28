#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公開前にバージョンを刻む。
- 各HTMLの const BUILD='...' を「vNN (MM-DD HH:MM)」に書き換える
- index.html のリンクに ?v=NN を付ける（キャッシュで古い版が開かれるのを防ぐ）
使い方: python stamp.py  ->  git add -A && git commit && git push
"""
import io, os, re, subprocess, datetime, glob

HERE = os.path.dirname(os.path.abspath(__file__))

def next_version():
    try:
        n = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'],
                                    cwd=HERE, stderr=subprocess.DEVNULL)
        return int(n.decode().strip()) + 1      # これから作るコミットの番号
    except Exception:
        return 0

def main():
    ver = next_version()
    # JST（このPCのローカル時刻をそのまま使う）
    stamp = datetime.datetime.now().strftime('%m-%d %H:%M')
    label = 'v%d (%s)' % (ver, stamp)

    changed = []
    for path in sorted(glob.glob(os.path.join(HERE, '*.html'))) + \
                sorted(glob.glob(os.path.join(HERE, 'versions', '*.html'))):
        s = io.open(path, encoding='utf-8').read()
        orig = s
        # ① BUILD 定数
        s = re.sub(r"const BUILD='[^']*';", "const BUILD='%s';" % label, s)
        # ② index.html のリンクにバージョンを付ける
        if os.path.basename(path) == 'index.html':
            s = re.sub(r'href="(feel-[a-z-]+\.html)(\?v=\d+)?"',
                       lambda m: 'href="%s?v=%d"' % (m.group(1), ver), s)
            s = s.replace('<!--VER-->', label)
            s = re.sub(r'(<(?:span|div) id="ver">)[^<]*(</(?:span|div)>)',
                       lambda m: m.group(1) + label + m.group(2), s)
        if s != orig:
            io.open(path, 'w', encoding='utf-8', newline='').write(s)
            changed.append(os.path.basename(path))

    print('刻んだバージョン: %s' % label)
    print('更新したファイル: %s' % (', '.join(changed) if changed else 'なし'))

if __name__ == '__main__':
    main()
