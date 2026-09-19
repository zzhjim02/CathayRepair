# -*- coding: utf-8 -*-
"""CathayRepair · PDF 损伤修复工具 —— 图形界面（tkinter）

规则：只读源 PDF，输出「原名_repaired.pdf」，绝不覆盖原件。
"""
import os
import queue
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repair as R  # noqa: E402

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:
    DND_FILES, TkinterDnD, HAS_DND = None, None, False

COLS = [('no', '序号', 46), ('folder', '所在文件夹', 240), ('name', '文件名', 300),
        ('pages', '页数', 60), ('size', '大小', 80), ('status', '状态', 150),
        ('out', '输出文件', 260)]
FIELDS = ['no', 'folder', 'name', 'pages', 'size', 'status', 'out']


def tk_splitlist(data):
    """解析拖放串（支持 {带 空格 的路径}）"""
    out, cur, brace = [], '', False
    for ch in data or '':
        if ch == '{':
            brace, cur = True, ''
        elif ch == '}':
            brace = False
            if cur:
                out.append(cur)
            cur = ''
        elif ch == ' ' and not brace:
            if cur:
                out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


class App(object):
    def __init__(self, root):
        self.root = root
        root.title('%s  %s' % (R.APP_TITLE, R.APP_VERSION))
        root.geometry('1180x760')
        root.minsize(900, 600)
        self.paths = []
        self.records = []
        self.rowmap = {}
        self.excluded = set()
        self.working = False
        self.q = queue.Queue()
        self._icon()
        self._build()
        self._pump()

    # ------------------------------------------------------------ 界面
    def _icon(self):
        p = R.icon_path()
        try:
            if p:
                self.root.iconbitmap(p)
        except Exception:
            pass

    def _build(self):
        pad = dict(padx=8, pady=6)
        top = ttk.Frame(self.root)
        top.pack(fill='x', **pad)

        self.dz = tk.Label(top, text='把 PDF 文件或文件夹拖进来（也可以点下面的按钮选择）',
                           relief='groove', bd=2, height=2, bg='#f3f6fb', fg='#33475b')
        self.dz.pack(fill='x')
        if HAS_DND:
            for w in (self.dz, self.root):
                try:
                    w.drop_target_register(DND_FILES)
                    w.dnd_bind('<<Drop>>', self.on_drop)
                except Exception:
                    pass

        r1 = ttk.Frame(self.root)
        r1.pack(fill='x', **pad)
        ttk.Button(r1, text='选择文件夹', command=self.pick_dir).pack(side='left')
        ttk.Button(r1, text='选择 PDF 文件', command=self.pick_files).pack(side='left', padx=6)
        ttk.Button(r1, text='清空列表', command=self.clear).pack(side='left')
        ttk.Label(r1, text='　输出后缀:').pack(side='left', padx=(16, 2))
        self.v_suffix = tk.StringVar(value=R.DEFAULT_SUFFIX)
        ttk.Entry(r1, textvariable=self.v_suffix, width=14).pack(side='left')
        self.v_over = tk.BooleanVar(value=False)
        ttk.Checkbutton(r1, text='覆盖已存在的产物', variable=self.v_over).pack(side='left', padx=8)
        ttk.Label(r1, text='并行:').pack(side='left', padx=(12, 2))
        self.v_jobs = tk.IntVar(value=min(4, os.cpu_count() or 4))
        ttk.Spinbox(r1, from_=1, to=16, width=4, textvariable=self.v_jobs).pack(side='left')

        r2 = ttk.Frame(self.root)
        r2.pack(fill='x', **pad)
        ttk.Button(r2, text='扫描', command=self.do_scan).pack(side='left')
        ttk.Button(r2, text='全选', command=lambda: self.select(True)).pack(side='left', padx=6)
        ttk.Button(r2, text='全不选', command=lambda: self.select(False)).pack(side='left')
        ttk.Button(r2, text='移出列表', command=self.remove_sel).pack(side='left', padx=6)
        self.pb = ttk.Progressbar(r2, mode='determinate', length=260)
        self.pb.pack(side='left', padx=12)
        self.status = tk.StringVar(value='就绪')
        ttk.Label(r2, textvariable=self.status).pack(side='left')

        mid = ttk.Frame(self.root)
        mid.pack(fill='both', expand=True, **pad)
        self.tree = ttk.Treeview(mid, columns=[c[0] for c in COLS], show='headings', selectmode='extended')
        for key, title, w in COLS:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=w, anchor='w', stretch=(key in ('folder', 'name', 'out')))
        vs = ttk.Scrollbar(mid, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vs.pack(side='left', fill='y')
        self.tree.tag_configure('dim', foreground='#a3a3a3')
        self.tree.tag_configure('warn', background='#fff4cc')
        self.tree.tag_configure('manual', background='#ffd9d9')
        self.tree.bind('<Double-1>', self.open_row_dir)

        r3 = ttk.Frame(self.root)
        r3.pack(fill='x', **pad)
        self.btn_run = ttk.Button(r3, text='开始修复（选中项；未选=全部）', command=self.do_run)
        self.btn_run.pack(side='left')
        ttk.Button(r3, text='打开输出目录', command=self.open_out).pack(side='left', padx=6)
        self.v_exp = tk.BooleanVar(value=False)
        ttk.Checkbutton(r3, text='修复后导出报告 CSV', variable=self.v_exp).pack(side='left', padx=8)

        lf = ttk.LabelFrame(self.root, text='日志')
        lf.pack(fill='both', expand=True, **pad)
        self.log = tk.Text(lf, height=9, wrap='none')
        ls = ttk.Scrollbar(lf, orient='vertical', command=self.log.yview)
        self.log.configure(yscrollcommand=ls.set)
        self.log.pack(side='left', fill='both', expand=True)
        ls.pack(side='left', fill='y')

    # ------------------------------------------------------------ 交互
    def on_drop(self, event):
        paths = tk_splitlist(event.data)
        if paths:
            self.add_paths(paths)

    def pick_dir(self):
        p = filedialog.askdirectory(title='选择包含 PDF 的文件夹')
        if p:
            self.add_paths([p])

    def pick_files(self):
        ps = filedialog.askopenfilenames(title='选择 PDF', filetypes=[('PDF', '*.pdf')])
        if ps:
            self.add_paths(list(ps))

    def add_paths(self, paths):
        for p in paths:
            p = os.path.abspath(p)
            if p not in self.paths:
                self.paths.append(p)
        self.write('已加入来源 %d 项：%s' % (len(paths), '、'.join(os.path.basename(p) for p in paths[:6])))
        self.do_scan()

    def clear(self):
        self.paths, self.records, self.excluded = [], [], set()
        self.fill()
        self.status.set('已清空')

    def select(self, flag):
        self.tree.selection_set(self.tree.get_children() if flag else [])

    def remove_sel(self):
        n = 0
        for iid in self.tree.selection():
            r = self.rowmap.get(iid)
            if r:
                self.excluded.add(r['path'])
                n += 1
        self.fill()
        self.write('已移出列表 %d 项（重新扫描也不会再出现）' % n)

    def open_row_dir(self, _ev=None):
        sel = self.tree.selection()
        if sel:
            r = self.rowmap.get(sel[0])
            if r:
                try:
                    os.startfile(r['dir'])
                except Exception as e:
                    self.write('打开目录失败：%s' % e)

    def open_out(self):
        dirs = []
        for r in self.records:
            if not r.get('no_need') and r['dir'] not in dirs:
                dirs.append(r['dir'])
        for d in dirs[:8]:
            try:
                os.startfile(d)
            except Exception:
                pass

    # ------------------------------------------------------------ 扫描
    def do_scan(self):
        if self.working:
            return
        if not self.paths:
            self.status.set('请先拖入 PDF 或文件夹')
            return
        self.status.set('扫描中……')
        suffix = self.v_suffix.get().strip() or R.DEFAULT_SUFFIX
        threading.Thread(target=self._scan, args=(suffix,), daemon=True).start()

    def _scan(self, suffix):
        try:
            recs = R.scan(self.paths, suffix=suffix)
        except Exception as e:
            self.q.put(('log', '扫描出错：%s' % e))
            recs = []
        recs = [r for r in recs if r['path'] not in self.excluded]
        self.q.put(('records', recs))

    # ------------------------------------------------------------ 修复
    def do_run(self):
        if self.working:
            return
        sel = [self.rowmap[i] for i in self.tree.selection() if i in self.rowmap]
        todo = [r for r in (sel or self.records) if not r.get('no_need')]
        if not todo:
            messagebox.showinfo('提示', '没有需要修复的文件（选中的都无需处理）。')
            return
        if not sel:
            if not messagebox.askyesno('确认', '未选中任何行 → 将处理全部 %d 个文件，继续？' % len(todo)):
                return
        if not messagebox.askyesno('确认', '将修复 %d 个文件。\n源文件不会被改动，输出到同目录 <%s>。' % (
                len(todo), R.DEFAULT_SUFFIX if not self.v_suffix.get().strip() else self.v_suffix.get().strip())):
            return
        self.working = True
        self.btn_run.state(['disabled'])
        self.pb.configure(maximum=len(todo), value=0)
        self.status.set('修复中……')
        threading.Thread(target=self._run, args=(todo,), daemon=True).start()

    def _run(self, todo):
        suffix = self.v_suffix.get().strip() or R.DEFAULT_SUFFIX
        overs = self.v_over.get()
        jobs = max(1, int(self.v_jobs.get() or 1))

        def work(r):
            r['suffix'] = suffix
            r['out'] = os.path.join(r['dir'], r['stem'] + suffix + '.pdf')
            if os.path.exists(r['out']) and not overs:
                return r, '目标已存在，跳过'
            try:
                ok, bad, total = R.repair_pdf(r['path'], r['out'], log=lambda m: self.q.put(('log', m)))
                r.update(ok_pages=ok, bad_pages=bad, pages=total or r['pages'])
                return r, '第 %s 个完成' % ok
            except Exception as e:
                r['status'] = '出错：%s' % str(e)[:60]
                return r, '出错：%s' % e

        rows, errors, done = [], [], 0
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            for r, msg in ex.map(work, todo):
                done += 1
                if msg.startswith('出错'):
                    errors.append(msg)
                    r['status'] = msg
                elif '跳过' in msg:
                    r['status'] = '已跳过'
                else:
                    r['status'] = '完成' if not r.get('bad_pages') else '完成（含坏页）'
                rows.append(r)
                self.q.put(('progress', (done, '修复中…… %d/%d' % (done, len(todo)))))
                self.q.put(('log', '  %s → %s' % (r['base'], r['status'])))
        report = []
        for i, r in enumerate(rows, 1):
            report.append({'序号': i, '所在文件夹': r['dir'], '原文件名': r['base'], '页数': r.get('pages') or '',
                           '成功页': r.get('ok_pages'), '失败页': '、'.join(map(str, r.get('bad_pages') or [])) or '无',
                           '输出文件': os.path.basename(r['out']) if r.get('ok_pages') is not None else '',
                           '状态': r['status']})
        path = None
        if self.v_exp.get():
            path = os.path.join(R.app_dir(), '_修复报告.csv')
            R.export_report(report, path)
        self.q.put(('done', (len(rows), errors, path)))

    # ------------------------------------------------------------ 队列泵
    def _pump(self):
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == 'log':
                    self.write(payload)
                elif kind == 'records':
                    self.records = payload
                    self.fill()
                    n = len([r for r in payload if not r.get('no_need')])
                    m = len(payload) - n
                    self.status.set('扫描完成：待修复 %d 个%s' % (n, ('，另有 %d 个无需处理' % m) if m else ''))
                elif kind == 'progress':
                    done, txt = payload
                    self.pb.configure(value=done)
                    self.status.set(txt)
                elif kind == 'done':
                    total, errors, path = payload
                    self.working = False
                    self.btn_run.state(['!disabled'])
                    self.status.set('完成 %d 个，出错 %d 个%s' % (total, len(errors), ('，报告：%s' % path) if path else ''))
                else:
                    pass
        except queue.Empty:
            pass
        self.root.after(120, self._pump)

    def fill(self):
        self.tree.delete(*self.tree.get_children())
        self.rowmap = {}
        for i, r in enumerate(self.records, 1):
            tags = ()
            if r.get('no_need'):
                tags = ('manual',) if r.get('status') == '需人工' else ('dim',)
            elif i % 2 == 0:
                tags = ()
            vals = [i, r['dir'], r['base'], r.get('pages') or '-', R.human(r['size']),
                    r.get('status', ''), os.path.basename(r['out'])]
            iid = self.tree.insert('', 'end', values=vals, tags=tags)
            self.rowmap[iid] = r

    def write(self, msg):
        self.log.insert('end', msg + '\n')
        self.log.see('end')


def main():
    if '--selftest' in sys.argv:
        txt = R.selftest()
        extra = ['']
        try:
            root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
            root.withdraw()
            app = App(root)
            root.update()
            extra.append('gui=OK 列=%d 拖放=%s' % (len(COLS), HAS_DND))
            extra.append('默认后缀=%s' % app.v_suffix.get())
            root.destroy()
        except Exception as e:
            extra.append('gui=FAIL %s' % e)
        try:
            with open(os.path.join(R.app_dir(), '_selftest.txt'), 'a', encoding='utf-8') as f:
                f.write('\n'.join(extra) + '\n')
        except Exception:
            pass
        print(txt + '\n'.join(extra))
        return
    root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
    try:
        root.tk.call('tk', 'scaling', 1.2)
    except Exception:
        pass
    App(root)
    if not HAS_DND:
        print('提示：未安装 tkinterdnd2，拖放不可用（可用按钮选择文件）。')
    root.mainloop()


if __name__ == '__main__':
    main()
