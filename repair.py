# -*- coding: utf-8 -*-
"""CathayRepair 引擎 —— PDF 损伤修复（逐页复制、跳过坏页，绝不改动原件）

用法（命令行）:
    python repair.py <PDF或目录> [更多路径...] [--out 后缀] [--overwrite]
无参数时扫描当前目录。
"""
import csv
import os
import re
import sys
import time

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

APP_NAME = 'CathayRepair'
APP_TITLE = 'CathayRepair · PDF 损伤修复工具'
APP_VERSION = 'v1.0.0'
DEFAULT_SUFFIX = '_repaired'
LOG_NAME = '修复日志.txt'


# ---------------------------------------------------------------- 路径
def app_dir():
    """程序所在目录（打包成 exe 时为 exe 目录）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def res_dir():
    """随包只读资源目录（打包时指向 _MEIPASS）"""
    return getattr(sys, '_MEIPASS', None) or app_dir()


def icon_path():
    """app.ico 的位置（免安装便携版 / 打包版都能找到）"""
    cands = []
    if getattr(sys, '_MEIPASS', None):
        cands.append(os.path.join(sys._MEIPASS, 'app.ico'))
    cands += [os.path.join(app_dir(), 'app.ico'), os.path.join(res_dir(), 'app.ico')]
    for p in cands:
        if os.path.exists(p):
            return p
    return ''


# ---------------------------------------------------------------- 工具
def human(n):
    for u, k in (('GB', 1 << 30), ('MB', 1 << 20), ('KB', 1 << 10)):
        if n >= k:
            return '%.2f %s' % (n / k, u)
    return '%d B' % n


def split_suffix(name):
    """拆出主名与已带的后缀，便于识别「已是产物」"""
    base, ext = os.path.splitext(name)
    m = re.search(r'(_repaired|_fixed|_修复|_已修复)$', base)
    return (base[:m.start()], m.group(1), ext) if m else (base, '', ext)


def _walk(paths):
    """递归展开文件与目录（修好老工具的递归毛病）"""
    seen, files = set(), []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isdir(p):
            for dp, dns, fns in os.walk(p):
                dns[:] = [d for d in dns if not d.startswith('~$')]
                for fn in sorted(fns):
                    f = os.path.join(dp, fn)
                    if f.lower().endswith('.pdf') and f not in seen:
                        seen.add(f)
                        files.append(f)
        elif os.path.isfile(p) and p.lower().endswith('.pdf') and p not in seen:
            seen.add(p)
            files.append(p)
    return files


def page_count(path):
    """页数；打不开返回 None"""
    if fitz is None:
        return None
    try:
        with fitz.open(path) as d:
            pages = len(d)
            if pages <= 0:
                return None
            return pages
    except Exception:
        return None


# ---------------------------------------------------------------- 扫描
def scan(paths, suffix=DEFAULT_SUFFIX, skip_done=True):
    """扫描 PDF，返回记录列表（只读，不改任何东西）"""
    recs = []
    for f in _walk(paths):
        base, ext = os.path.splitext(os.path.basename(f))
        stem, old_sfx, _ = split_suffix(os.path.basename(f))
        rec = {
            'dir': os.path.dirname(f),
            'base': os.path.basename(f),
            'stem': stem,
            'path': f,
            'size': os.path.getsize(f),
            'suffix': suffix,
            'out': os.path.join(os.path.dirname(f), stem + suffix + '.pdf'),
            'no_need': False,
            'why': '',
            'status': '',
            'pages': None,
            'ok_pages': None,
            'bad_pages': None,
        }
        if old_sfx and skip_done:
            rec.update(no_need=True, why='已是修复产物', status='无需处理')
        elif suffix and base.endswith(suffix):
            rec.update(no_need=True, why='已是修复产物', status='无需处理')
        else:
            n = page_count(f)
            if n is None:
                rec.update(no_need=True, why='打不开（可能已损坏到无法解析）', status='需人工')
            else:
                rec['pages'] = n
                rec['status'] = '待修复'
        recs.append(rec)
    return recs


# ---------------------------------------------------------------- 修复
def repair_pdf(src, dst, log=None, progress=None):
    """逐页复制，跳过坏页。返回 (成功页数, 失败页号列表, 总页数)"""
    say = log if log else (lambda m: None)
    if fitz is None:
        raise RuntimeError('PyMuPDF 未安装（pip install pymupdf）')
    t0 = time.time()
    doc = fitz.open(src)
    total = len(doc)
    say('  源文件 %s，共 %d 页' % (os.path.basename(src), total))
    new = fitz.open()
    ok, bad = 0, []
    for i in range(total):
        try:
            new.insert_pdf(doc, from_page=i, to_page=i)
            ok += 1
        except Exception as e:
            bad.append(i + 1)
            say('  ✗ 第 %d 页复制失败：%s' % (i + 1, str(e)[:120]))
        if progress and (i % 10 == 0 or i == total - 1):
            progress(i + 1, total)
    if ok == 0:
        say('  ⚠ 没有任何页面复制成功，输出文件可能是空的')
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    new.save(dst, garbage=4, deflate=True, clean=True)
    new.close()
    doc.close()
    say('  ✓ 输出 %s：成功 %d 页%s，用时 %.1fs' % (
        os.path.basename(dst), ok,
        ('，失败 %d 页（%s）' % (len(bad), '、'.join(map(str, bad[:20])))) if bad else '', time.time() - t0))
    return ok, bad, total


def repair_apply(recs, overwrite=False, log_path=None, progress=None, log=None):
    """批量修复。返回 (明细行列表, 错误列表, 跳过列表)"""
    rows, errors, skipped = [], [], []
    lines = []
    for idx, r in enumerate(recs, 1):
        if r.get('no_need'):
            skipped.append(r['base'])
            continue
        try:
            if os.path.exists(r['out']) and not overwrite:
                skipped.append(r['base'])
                lines.append('[%d] %s → 目标已存在，跳过' % (idx, r['base']))
                continue
            own = []
            ok, bad, total = repair_pdf(r['path'], r['out'], log=own.append, progress=progress)
            lines += ['[%d] %s' % (idx, r['base'])] + own
            rows.append({
                '序号': idx, '所在文件夹': r['dir'], '原文件名': r['base'],
                '页数': total, '成功页': ok, '失败页': '、'.join(map(str, bad)) or '无',
                '输出文件': os.path.basename(r['out']), '状态': '完成' if not bad else '完成（含坏页）',
            })
        except Exception as e:
            errors.append('%s：%s' % (r['base'], e))
            lines.append('[%d] %s → 出错：%s' % (idx, r['base'], str(e)[:200]))
            rows.append({'序号': idx, '所在文件夹': r['dir'], '原文件名': r['base'],
                         '页数': '', '成功页': 0, '失败页': '', '输出文件': '',
                         '状态': '出错：%s' % str(e)[:80]})
    if log_path:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    if log and callable(log):
        log('\n'.join(lines))
    return rows, errors, skipped


def export_report(rows, path):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['序号', '所在文件夹', '原文件名', '页数', '成功页',
                                          '失败页', '输出文件', '状态'])
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- 自检 / CLI
def selftest():
    out = ['%s %s' % (APP_TITLE, APP_VERSION), 'frozen=%s' % getattr(sys, 'frozen', False),
           'app_dir=%s' % app_dir(), 'pymupdf=%s' % (getattr(fitz, '__version__', '缺失') if fitz else '缺失')]
    try:
        import tkinter
        out.append('tkinter=OK')
    except Exception as e:
        out.append('tkinter=缺失(%s)' % e)
    try:
        import tkinterdnd2  # noqa
        out.append('tkinterdnd2=OK')
    except Exception:
        out.append('tkinterdnd2=缺失(拖放不可用)')
    # 真跑一遍：造一个 3 页 PDF → 修复 → 校验页数
    if fitz:
        import tempfile
        d = tempfile.mkdtemp(prefix='catrepair_')
        src = os.path.join(d, '自检_原始.pdf')
        dst = os.path.join(d, '自检_repaired.pdf')
        doc = fitz.open()
        for i in range(3):
            p = doc.new_page()
            p.insert_text((72, 720), 'CathayRepair selftest page %d' % (i + 1), fontsize=14)
        doc.save(src)
        doc.close()
        ok, bad, total = repair_pdf(src, dst)
        out.append('测试修复：%d/%d 页成功，坏页 %s' % (ok, total, bad or '无'))
        out.append('输出存在=%s 页数=%s' % (os.path.exists(dst), page_count(dst)))
        out.append('icon=%s' % (icon_path() or '缺失'))
        out.append('result=%s' % ('OK' if ok == total == 3 and page_count(dst) == 3 else 'FAIL'))
    else:
        out.append('result=FAIL（没有 PyMuPDF）')
    txt = '\n'.join(out)
    try:
        with open(os.path.join(app_dir(), '_selftest.txt'), 'w', encoding='utf-8') as f:
            f.write(txt + '\n')
    except Exception:
        pass
    return txt


def main():
    args = [a for a in sys.argv[1:]]
    if '--selftest' in args:
        print(selftest())
        return
    suffix, overwrite, paths = DEFAULT_SUFFIX, False, []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ('--out', '-o') and i + 1 < len(args):
            suffix, i = args[i + 1], i + 2
            continue
        if a == '--overwrite':
            overwrite, i = True, i + 1
            continue
        paths.append(a)
        i += 1
    paths = paths or ['.']
    recs = [r for r in scan(paths, suffix) if not r['no_need']]
    if not recs:
        print('没有找到需要修复的 PDF。')
        return
    print('找到 %d 个 PDF，开始修复……' % len(recs))
    rows, errors, skipped = repair_apply(recs, overwrite=overwrite,
                                         log_path=LOG_NAME, log=print)
    print('\n完成：成功 %d，出错 %d，跳过 %d；明细见 %s' % (
        len([r for r in rows if r['状态'].startswith('完成')]), len(errors), len(skipped), LOG_NAME))


if __name__ == '__main__':
    main()
