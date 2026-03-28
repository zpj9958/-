import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def select_doc_a():
    filepath = filedialog.askopenfilename(title="选择【文档A】",
                                          filetypes=[("Text files", "*.txt *.log *.csv"), ("All files", "*.*")])
    if filepath:
        entry_doc_a.delete(0, tk.END)
        entry_doc_a.insert(0, filepath)


def select_doc_b():
    filepath = filedialog.askopenfilename(title="选择【文档B】",
                                          filetypes=[("Text files", "*.txt *.log *.csv"), ("All files", "*.*")])
    if filepath:
        entry_doc_b.delete(0, tk.END)
        entry_doc_b.insert(0, filepath)


def safe_read_file(filepath):
    encodings = ['utf-8', 'gbk', 'utf-8-sig']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise Exception(f"无法读取文件 {filepath}，请检查文件编码！")


def safe_read_lines(filepath):
    encodings = ['utf-8', 'gbk', 'utf-8-sig']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue
    raise Exception(f"无法读取文件 {filepath}，请检查文件编码！")


def update_ui(event=None):
    mode = combo_mode.get()
    if "单关键词" in mode:
        frame_double.pack_forget()
        frame_single.pack(fill=tk.X, pady=5)
    else:
        frame_single.pack_forget()
        frame_double.pack(fill=tk.X, pady=5)


def start_process():
    doc_a = entry_doc_a.get()
    doc_b = entry_doc_b.get()
    mode = combo_mode.get()

    if not doc_a or not doc_b:
        messagebox.showwarning("提示", "请确保填写了文档A和文档B的路径！")
        return

    try:
        lines_before = int(entry_lines_before.get())
        lines_after = int(entry_lines_after.get())
        if lines_before < 0 or lines_after < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("错误", "文档B提取的行数必须是大于等于0的整数！")
        return

    try:
        # ================= 第一步：从文档A提取内容 =================
        content_a = safe_read_file(doc_a)
        extracted_terms = []
        search_idx = 0

        if "单关键词" in mode:
            keyword = entry_keyword.get()
            direction = combo_direction.get()
            if not keyword:
                messagebox.showwarning("提示", "请输入固定关键词！")
                return
            try:
                char_count = int(entry_chars.get())
                if char_count <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("错误", "提取的字符数必须大于0！")
                return

            while True:
                idx = content_a.find(keyword, search_idx)
                if idx == -1: break

                if direction == "关键词后面":
                    ext_start = idx + len(keyword)
                    ext_end = ext_start + char_count
                else:
                    ext_start = max(0, idx - char_count)
                    ext_end = idx

                term = content_a[ext_start:ext_end].strip()
                if term and term not in extracted_terms:
                    extracted_terms.append(term)
                search_idx = idx + len(keyword)

        else:
            kw_start = entry_kw_start.get()
            kw_end = entry_kw_end.get()
            if not kw_start or not kw_end:
                messagebox.showwarning("提示", "请输入起始和结束关键词！")
                return

            while True:
                start_idx = content_a.find(kw_start, search_idx)
                if start_idx == -1: break

                content_start = start_idx + len(kw_start)
                end_idx = content_a.find(kw_end, content_start)
                if end_idx == -1: break

                term = content_a[content_start:end_idx].strip()
                if term and term not in extracted_terms:
                    extracted_terms.append(term)
                search_idx = end_idx + len(kw_end)

        if not extracted_terms:
            messagebox.showinfo("提示", "在【文档A】中没有根据当前规则提取到任何内容。")
            return

        # ================= 第二步：去文档B检索 =================
        output_file = filedialog.asksaveasfilename(title="另存为新文档", defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not output_file: return

        lines_b = safe_read_lines(doc_b)
        final_results = []

        for term in extracted_terms:
            for i, line in enumerate(lines_b):
                if term in line:
                    start_line = max(0, i - lines_before)
                    end_line = min(len(lines_b), i + lines_after + 1)

                    # 纯净版：只把目标行塞进结果里，没有任何多余字符
                    for j in range(start_line, end_line):
                        final_results.append(lines_b[j])

        # ================= 第三步：保存文件 =================
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(final_results)

        messagebox.showinfo("大功告成！",
                            f"处理完毕！\n共提取了 {len(extracted_terms)} 个搜索词，并已完成文档B的检索与保存（纯净版）。")

    except Exception as e:
        messagebox.showerror("错误", f"处理过程中发生错误：\n{str(e)}")


# ================= 界面设计 =================
root = tk.Tk()
root.title("全能双文档联动提取神器")
root.geometry("520x520")
root.resizable(False, False)

frame_a = tk.LabelFrame(root, text="第一步：文档A设置 (生成动态搜索词)", padx=10, pady=10)
frame_a.pack(fill=tk.BOTH, padx=15, pady=10)

f1 = tk.Frame(frame_a)
f1.pack(fill=tk.X, pady=2)
tk.Label(f1, text="选择文档A:").pack(side=tk.LEFT)
entry_doc_a = tk.Entry(f1, width=38)
entry_doc_a.pack(side=tk.LEFT, padx=5)
tk.Button(f1, text="浏览...", command=select_doc_a).pack(side=tk.LEFT)

f_mode = tk.Frame(frame_a)
f_mode.pack(fill=tk.X, pady=(10, 5))
tk.Label(f_mode, text="提取模式:").pack(side=tk.LEFT)
combo_mode = ttk.Combobox(f_mode, values=["1. 单关键词提取 (指定前后字符数)", "2. 双关键词(夹心)提取"], width=30,
                          state="readonly")
combo_mode.current(0)
combo_mode.pack(side=tk.LEFT, padx=5)
combo_mode.bind("<<ComboboxSelected>>", update_ui)

frame_dynamic = tk.Frame(frame_a)
frame_dynamic.pack(fill=tk.X)

frame_single = tk.Frame(frame_dynamic)
tk.Label(frame_single, text="固定关键词:").pack(side=tk.LEFT)
entry_keyword = tk.Entry(frame_single, width=12)
entry_keyword.pack(side=tk.LEFT, padx=5)
tk.Label(frame_single, text="提取").pack(side=tk.LEFT)
combo_direction = ttk.Combobox(frame_single, values=["关键词后面", "关键词前面"], width=8, state="readonly")
combo_direction.current(0)
combo_direction.pack(side=tk.LEFT, padx=2)
entry_chars = tk.Entry(frame_single, width=4)
entry_chars.insert(0, "5")
entry_chars.pack(side=tk.LEFT, padx=2)
tk.Label(frame_single, text="个字符").pack(side=tk.LEFT)

frame_double = tk.Frame(frame_dynamic)
tk.Label(frame_double, text="起始关键词:").pack(side=tk.LEFT)
entry_kw_start = tk.Entry(frame_double, width=12)
entry_kw_start.pack(side=tk.LEFT, padx=5)
tk.Label(frame_double, text="结束关键词:").pack(side=tk.LEFT, padx=(10, 0))
entry_kw_end = tk.Entry(frame_double, width=12)
entry_kw_end.pack(side=tk.LEFT, padx=5)

update_ui()

frame_b = tk.LabelFrame(root, text="第二步：文档B设置 (检索目标并保存上下文)", padx=10, pady=10)
frame_b.pack(fill=tk.BOTH, padx=15, pady=5)

f3 = tk.Frame(frame_b)
f3.pack(fill=tk.X, pady=2)
tk.Label(f3, text="选择文档B:").pack(side=tk.LEFT)
entry_doc_b = tk.Entry(f3, width=38)
entry_doc_b.pack(side=tk.LEFT, padx=5)
tk.Button(f3, text="浏览...", command=select_doc_b).pack(side=tk.LEFT)

f4 = tk.Frame(frame_b)
f4.pack(fill=tk.X, pady=(10, 2))
tk.Label(f4, text="检索到目标后，保存其 前").pack(side=tk.LEFT)
entry_lines_before = tk.Entry(f4, width=4)
entry_lines_before.insert(0, "2")
entry_lines_before.pack(side=tk.LEFT, padx=2)
tk.Label(f4, text="行，和 后").pack(side=tk.LEFT)
entry_lines_after = tk.Entry(f4, width=4)
entry_lines_after.insert(0, "2")
entry_lines_after.pack(side=tk.LEFT, padx=2)
tk.Label(f4, text="行").pack(side=tk.LEFT)

tk.Button(root, text="🚀 一键联动提取并另存为", bg="#4CAF50", fg="black", font=("Arial", 11, "bold"),
          command=start_process).pack(pady=20)

root.mainloop()