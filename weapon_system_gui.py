import tkinter as tk
from tkinter import ttk, messagebox
from weapon_system import *

class WeaponSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("枪械管理系统")
        self.weapons = load_weapons()
        load_attachments_data()
        
        # 初始化字典 - 确保在使用前已创建
        self.weapon_entries = {}
        self.soldier_class_vars = {}  # 也初始化这个字典
        
        # 设置最小窗口大小
        self.root.minsize(800, 600)
        
        # 配置根窗口的网格
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 创建主框架
        self.main_frame = ttk.Notebook(root)
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # 创建各个标签页
        self.create_weapon_management_tab()
        self.create_attachment_management_tab()
        self.create_weapon_config_tab()
        self.create_btk_calculator_tab()
        
    def create_scrollable_frame(self, parent):
        """创建一个可滚动���框架，只在需要时显示滚动条"""
        # 创建主容器框架
        container = ttk.Frame(parent)
        container.pack(fill='both', expand=True)
        
        # 创建画布和滚动条
        canvas = tk.Canvas(container, highlightthickness=0)  # 移除边框
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # 配置画布
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self._update_scroll_region(canvas, scrollbar)
        )
        canvas.bind(
            "<Configure>",
            lambda e: self._update_scroll_region(canvas, scrollbar)
        )
        
        # 创建画布窗口
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮支持
        def _on_mousewheel(event):
            if scrollbar.winfo_ismapped():  # 只在滚动条显示时响应滚轮
                if event.delta > 0:
                    canvas.yview_scroll(-1, "units")
                else:
                    canvas.yview_scroll(1, "units")
        
        # 绑定鼠标滚轮事件
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # 当鼠标进入/离开时绑定/解绑滚轮事件
        def _bind_mousewheel(event):
            if scrollbar.winfo_ismapped():
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        scrollable_frame.bind("<Enter>", _bind_mousewheel)
        scrollable_frame.bind("<Leave>", _unbind_mousewheel)
        
        # 布局
        canvas.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)  # 添加内边距
        scrollbar.pack(side="right", fill="y", pady=5)  # 添加内边距
        
        # 配置画布大小调整
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 更新内部框架宽度以匹配画布
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        canvas.bind('<Configure>', _on_frame_configure)
        
        return scrollable_frame
    
    def _update_scroll_region(self, canvas, scrollbar):
        """更新滚动区域，根据需要显示或���藏滚动条"""
        canvas.update_idletasks()
        
        # 获取画布和其内容的尺寸
        canvas_height = canvas.winfo_height()
        frame_height = canvas.bbox("all")[3] if canvas.bbox("all") else 0
        
        # 设置滚动区域
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # 根据内容高度决定是否显示滚动条
        if frame_height > canvas_height:
            if not scrollbar.winfo_ismapped():
                scrollbar.pack(side="right", fill="y", pady=5)
        else:
            if scrollbar.winfo_ismapped():
                scrollbar.pack_forget()
    
    def create_weapon_management_tab(self):
        """创建枪械管理标签页"""
        weapon_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(weapon_frame, text='枪械管理')
        
        # 配置网格
        weapon_frame.grid_rowconfigure(0, weight=1)
        weapon_frame.grid_columnconfigure(1, weight=1)  # 右侧区域可扩展
        
        # 左侧武器列表
        list_frame = ttk.Frame(weapon_frame)
        list_frame.grid(row=0, column=0, sticky='ns', padx=5, pady=5)
        
        ttk.Label(list_frame, text="已保存的枪械:").pack(fill='x')
        
        # 列表框和滚动条
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True)
        
        self.weapon_listbox = tk.Listbox(list_container, width=30)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.weapon_listbox.yview)
        self.weapon_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.weapon_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 右侧信息区域
        info_frame = ttk.Frame(weapon_frame)
        info_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # 配置信息区域的网格
        info_frame.grid_rowconfigure(2, weight=1)  # 让性能参数区域可扩展
        info_frame.grid_columnconfigure(0, weight=1)
        
        # 基本信息区域
        basic_frame = ttk.LabelFrame(info_frame, text="基本信息")
        basic_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # 配置基本信息框架的网格
        for i in range(4):  # 假设有4列
            basic_frame.grid_columnconfigure(i, weight=1)
        
        # 基本信息输入区域
        basic_fields = [
            ('name', '枪械名称'),
            ('base_damage', '胸部基础伤害'),
            ('stomach_damage', '腹部伤害'),
            ('limb_damage', '手部伤害'),
            ('foot_damage', '脚部伤害'),
            ('range_meters', '射程(米)'),
            ('fire_rate', '射速(发/分钟)')
        ]
        
        for i, (field, label) in enumerate(basic_fields):
            ttk.Label(basic_frame, text=label).grid(row=i//2, column=i%2*2, padx=5, pady=2)
            entry = ttk.Entry(basic_frame)
            entry.grid(row=i//2, column=i%2*2+1, padx=5, pady=2)
            self.weapon_entries[field] = entry
        
        # 在基本信息框架中添加枪械类型选择
        type_frame = ttk.LabelFrame(basic_frame, text="枪械类型")
        type_frame.grid(row=len(basic_fields)//2 + 1, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        
        self.weapon_type_var = tk.StringVar()
        for i, wtype in enumerate(Weapon.WEAPON_TYPES):
            ttk.Radiobutton(
                type_frame,
                text=wtype,
                variable=self.weapon_type_var,
                value=wtype
            ).grid(row=i//3, column=i%3, padx=5, pady=2)
        
        # 添加适用兵种选择
        class_frame = ttk.LabelFrame(basic_frame, text="适用兵种")
        class_frame.grid(row=len(basic_fields)//2 + 2, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        
        self.soldier_class_vars = {}
        for i, sclass in enumerate(Weapon.SOLDIER_CLASSES):
            var = tk.BooleanVar()
            self.soldier_class_vars[sclass] = var
            ttk.Checkbutton(
                class_frame,
                text=sclass,
                variable=var
            ).grid(row=0, column=i, padx=5, pady=2)
        
        # 性能参数输入区域
        stats_frame = ttk.LabelFrame(info_frame, text="性能参数")
        stats_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        stats_fields = [
            ('recoil_control', '后坐力控制'),
            ('handling_speed', '操控速度'),
            ('ads_stability', '据枪稳定性'),
            ('hip_fire_accuracy', '腰际射击精度')
        ]
        
        for i, (field, label) in enumerate(stats_fields):
            ttk.Label(stats_frame, text=label).grid(row=i//2, column=i%2*2, padx=5, pady=2)
            entry = ttk.Entry(stats_frame)
            entry.grid(row=i//2, column=i%2*2+1, padx=5, pady=2)
            self.weapon_entries[field] = entry
        
        # 按钮区域
        button_frame = ttk.Frame(info_frame)
        button_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Button(button_frame, text="添加新枪械", command=self.add_weapon).pack(side='left', padx=5)
        ttk.Button(button_frame, text="保存修改", command=self.save_weapon).pack(side='left', padx=5)
        ttk.Button(button_frame, text="删除枪械", command=self.delete_weapon).pack(side='left', padx=5)
        
    def create_attachment_management_tab(self):
        """创建配件管理标签页"""
        attachment_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(attachment_frame, text='配件管理')
        
        # 配置网格
        attachment_frame.grid_rowconfigure(0, weight=1)
        attachment_frame.grid_columnconfigure(1, weight=1)
        
        # 左侧选择区域
        select_frame = ttk.Frame(attachment_frame)
        select_frame.grid(row=0, column=0, sticky='ns', padx=5, pady=5)
        
        # 为各个列表框添加滚动条
        row = 0
        for combo_name, label_text in [
            ('soldier_class_combo', "选择兵种:"),
            ('weapon_type_combo', "枪械类型:"),
            ('weapon_name_combo', "枪械名称:")
        ]:
            ttk.Label(select_frame, text=label_text).grid(row=row, pady=(0,5))
            combo = ttk.Combobox(select_frame, width=27, state='readonly')
            setattr(self, combo_name, combo)
            combo.grid(row=row+1, pady=(0,10))
            row += 2
        
        # 右侧信息显示区域
        info_frame = ttk.Frame(attachment_frame)
        info_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # 配件操作按钮
        button_frame = ttk.Frame(info_frame)
        button_frame.grid(row=0, column=0, sticky='ew', pady=5)
        ttk.Button(button_frame, text="添加新配件", command=self.add_new_attachment).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="修改配件", command=self.edit_attachment).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="删除配件", command=self.delete_attachment).grid(row=0, column=2, padx=5)
        
        # 配件列表
        list_frame = ttk.LabelFrame(info_frame, text="配件列表")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        info_frame.grid_rowconfigure(1, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # 创建树形视图来显示配件
        self.attachment_tree = ttk.Treeview(list_frame, columns=('类型', '名称', '属性修改'), show='headings')
        self.attachment_tree.heading('类型', text='配件类型')
        self.attachment_tree.heading('名称', text='配件名称')
        self.attachment_tree.heading('属性修改', text='属性修改')
        self.attachment_tree.grid(row=0, column=0, sticky='nsew')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.soldier_class_combo.bind('<<ComboboxSelected>>', self.on_soldier_class_select)
        self.weapon_type_combo.bind('<<ComboboxSelected>>', self.on_weapon_type_select)
        self.weapon_name_combo.bind('<<ComboboxSelected>>', self.on_attachment_weapon_select)
    
    def add_new_attachment(self):
        """添加新配件"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新配件")
        dialog.geometry("400x500")
        
        # 基本信息
        ttk.Label(dialog, text="配件类型:").pack(pady=5)
        type_combo = ttk.Combobox(dialog, values=list(Attachment.TYPES.values()), state='readonly')
        type_combo.pack(fill='x', padx=5)
        
        ttk.Label(dialog, text="配件名称:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(fill='x', padx=5)
        
        # 属性修改值
        mods_frame = ttk.LabelFrame(dialog, text="属性修改")
        mods_frame.pack(fill='x', padx=5, pady=5)
        
        mod_entries = {}
        for field, label in [
            ('recoil_mod', '后坐力修改'),
            ('handling_mod', '操控速度修改'),
            ('stability_mod', '据枪稳定性修改'),
            ('hip_fire_mod', '腰际射击精度修改')
        ]:
            frame = ttk.Frame(mods_frame)
            frame.pack(fill='x', pady=2)
            ttk.Label(frame, text=label).pack(side='left')
            entry = ttk.Entry(frame, width=10)
            entry.pack(side='right')
            mod_entries[field] = entry
        
        # 特殊属性
        special_frame = ttk.LabelFrame(dialog, text="特殊属性")
        special_frame.pack(fill='x', padx=5, pady=5)
        
        # 创建但不立即显示可安装握把座选项
        can_mount_grip_var = tk.BooleanVar()
        grip_check = ttk.Checkbutton(
            special_frame, 
            text="可安装握把座", 
            variable=can_mount_grip_var
        )
        
        def on_type_select(event):
            """当选择配件类型时"""
            selected_type = type_combo.get()
            # 只有选择后握把时才显示"可安装握把座"选项
            if selected_type == '后握把':
                grip_check.pack()
            else:
                grip_check.pack_forget()
                can_mount_grip_var.set(False)
        
        type_combo.bind('<<ComboboxSelected>>', on_type_select)
        
        # 配件适用范围
        scope_frame = ttk.LabelFrame(dialog, text="适用范围")
        scope_frame.pack(fill='x', padx=5, pady=5)
        
        is_specific_var = tk.BooleanVar()
        weapon_entry = ttk.Entry(scope_frame)
        
        def toggle_weapon_entry():
            if is_specific_var.get():
                weapon_entry.config(state='normal')
                # 获取当前选中的枪械名称
                weapon_name = self.weapon_name_combo.get()
                if weapon_name:
                    weapon_entry.delete(0, tk.END)
                    weapon_entry.insert(0, weapon_name)
            else:
                weapon_entry.delete(0, tk.END)
                weapon_entry.insert(0, "适用武器名称")
                weapon_entry.config(state='disabled')
        
        specific_check = ttk.Checkbutton(
            scope_frame, 
            text="特定武器专用", 
            variable=is_specific_var,
            command=toggle_weapon_entry
        )
        specific_check.pack()
        
        weapon_entry.pack(fill='x', padx=5, pady=5)
        weapon_entry.insert(0, "适用武器名称")
        weapon_entry.config(state='disabled')
        
        # 如果当前已选择了枪械，默认勾选"特定武器专用"并填入枪械名称
        weapon_name = self.weapon_name_combo.get()
        if weapon_name:
            is_specific_var.set(True)
            weapon_entry.config(state='normal')
            weapon_entry.delete(0, tk.END)
            weapon_entry.insert(0, weapon_name)
        
        def save_attachment():
            try:
                # 收集数据
                attachment_data = {
                    'name': name_entry.get(),
                    'attachment_type': type_combo.get(),
                    'recoil_mod': float(mod_entries['recoil_mod'].get() or 0),
                    'handling_mod': float(mod_entries['handling_mod'].get() or 0),
                    'stability_mod': float(mod_entries['stability_mod'].get() or 0),
                    'hip_fire_mod': float(mod_entries['hip_fire_mod'].get() or 0),
                    'can_mount_grip': can_mount_grip_var.get()
                }
                
                # 保存配件数据
                if is_specific_var.get():
                    weapon_name = weapon_entry.get().strip()
                    if not weapon_name:
                        messagebox.showwarning("警告", "请输入适用的武器名称")
                        return
                    
                    if weapon_name not in ATTACHMENTS_DATA['specific']:
                        ATTACHMENTS_DATA['specific'][weapon_name] = {}
                    if attachment_data['attachment_type'] not in ATTACHMENTS_DATA['specific'][weapon_name]:
                        ATTACHMENTS_DATA['specific'][weapon_name][attachment_data['attachment_type']] = []
                    ATTACHMENTS_DATA['specific'][weapon_name][attachment_data['attachment_type']].append(attachment_data)
                else:
                    if attachment_data['attachment_type'] not in ATTACHMENTS_DATA['common']:
                        ATTACHMENTS_DATA['common'][attachment_data['attachment_type']] = []
                    ATTACHMENTS_DATA['common'][attachment_data['attachment_type']].append(attachment_data)
                
                save_attachments_data()
                messagebox.showinfo("成功", "配件添加成功！")
                dialog.destroy()
                self.update_attachment_tree()  # 更新配件列表显示
                
            except ValueError as e:
                messagebox.showerror("错误", f"输入错误: {str(e)}")
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="保存", command=save_attachment).pack(side='left', padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side='left', padx=5)
    
    def edit_attachment(self):
        """修改配件"""
        selection = self.attachment_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要修改的配件")
            return
        
        # 获取选中的配件数据
        item = self.attachment_tree.item(selection[0])
        attachment_type = item['values'][0]
        attachment_name = item['values'][1]
        
        # 查找配件数据
        attachment_data = None
        is_specific = False
        weapon_name = None
        
        # 在通用配件中查找
        if attachment_type in ATTACHMENTS_DATA['common']:
            for att in ATTACHMENTS_DATA['common'][attachment_type]:
                if att['name'] == attachment_name:
                    attachment_data = att
                    break
        
        # 在特定武器配件中查找
        if not attachment_data:
            for wpn, types in ATTACHMENTS_DATA['specific'].items():
                if attachment_type in types:
                    for att in types[attachment_type]:
                        if att['name'] == attachment_name:
                            attachment_data = att
                            is_specific = True
                            weapon_name = wpn
                            break
                    if attachment_data:
                        break
        
        if not attachment_data:
            messagebox.showerror("错误", "找不到配件数据")
            return
        
        # 创建编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("修改配件")
        dialog.geometry("400x500")
        
        # ... ��建与add_new_attachment相似的界面，但预填充现有数据 ...
        # (这部分代码与add_new_attachment类似，只是需要预填充数据)
    
    def delete_attachment(self):
        """删除配件"""
        selection = self.attachment_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的配件")
            return
        
        if not messagebox.askyesno("确认", "确定要删除选中的配件吗？"):
            return
        
        item = self.attachment_tree.item(selection[0])
        attachment_type = item['values'][0]
        attachment_name = item['values'][1]
        
        # 从数据中删除配件
        deleted = False
        
        # 从通用配件中删除
        if attachment_type in ATTACHMENTS_DATA['common']:
            ATTACHMENTS_DATA['common'][attachment_type] = [
                att for att in ATTACHMENTS_DATA['common'][attachment_type]
                if att['name'] != attachment_name
            ]
            deleted = True
        
        # 从特定武器配件中删除
        for weapon_types in ATTACHMENTS_DATA['specific'].values():
            if attachment_type in weapon_types:
                weapon_types[attachment_type] = [
                    att for att in weapon_types[attachment_type]
                    if att['name'] != attachment_name
                ]
                deleted = True
        
        if deleted:
            save_attachments_data()
            self.update_attachment_tree()
            messagebox.showinfo("成功", "配件已删除")
        else:
            messagebox.showerror("错误", "删除失败")
    
    def update_attachment_tree(self):
        """更新配件列表显示"""
        self.attachment_tree.delete(*self.attachment_tree.get_children())
        
        # 添加通用配件
        for att_type, attachments in ATTACHMENTS_DATA['common'].items():
            for att in attachments:
                mods = []
                if att['recoil_mod']: mods.append(f"后坐力{att['recoil_mod']:+}")
                if att['handling_mod']: mods.append(f"操控{att['handling_mod']:+}")
                if att['stability_mod']: mods.append(f"稳定性{att['stability_mod']:+}")
                if att['hip_fire_mod']: mods.append(f"精度{att['hip_fire_mod']:+}")
                
                self.attachment_tree.insert('', 'end', values=(
                    att_type,
                    att['name'],
                    ', '.join(mods)
                ))
        
        # 添加特定武器配件
        for weapon, types in ATTACHMENTS_DATA['specific'].items():
            for att_type, attachments in types.items():
                for att in attachments:
                    mods = []
                    if att['recoil_mod']: mods.append(f"后坐力{att['recoil_mod']:+}")
                    if att['handling_mod']: mods.append(f"操控{att['handling_mod']:+}")
                    if att['stability_mod']: mods.append(f"稳定性{att['stability_mod']:+}")
                    if att['hip_fire_mod']: mods.append(f"精度{att['hip_fire_mod']:+}")
                    
                    self.attachment_tree.insert('', 'end', values=(
                        att_type,
                        f"{att['name']} ({weapon}专用)",
                        ', '.join(mods)
                    ))
    
    def create_weapon_config_tab(self):
        """创建枪械配置标签页"""
        config_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(config_frame, text='枪械配置')
        
        # 配置网格
        config_frame.grid_rowconfigure(0, weight=1)
        config_frame.grid_columnconfigure(1, weight=1)
        
        # 左侧选择区域
        left_frame = ttk.Frame(config_frame)
        left_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # 为列表框添加滚动条
        list_scroll = ttk.Scrollbar(left_frame)
        self.config_weapon_listbox = tk.Listbox(left_frame, width=30, height=10,
                                              yscrollcommand=list_scroll.set)
        list_scroll.config(command=self.config_weapon_listbox.yview)
        
        ttk.Label(left_frame, text="选择枪械:").pack()
        self.config_weapon_listbox.pack(side='left', fill='y', expand=True)
        list_scroll.pack(side='right', fill='y')
        
        # 右侧息显示区域
        right_frame = ttk.Frame(config_frame)
        right_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # 当前选中枪械显示
        current_weapon_frame = ttk.LabelFrame(right_frame, text="当前配置枪械")
        current_weapon_frame.pack(fill='x', padx=5, pady=5)
        self.current_weapon_label = ttk.Label(current_weapon_frame, text="未选择枪械")
        self.current_weapon_label.pack(padx=5, pady=5)
        
        # 配件类型和选择区域
        attachment_frame = ttk.LabelFrame(right_frame, text="配件管理")
        attachment_frame.pack(fill='x', pady=5)
        
        # 使用Checkbutton代替Listbox
        self.config_type_vars = {}  # 存储Checkbutton变量
        for type_name in Attachment.TYPES.values():
            var = tk.BooleanVar()
            check = ttk.Checkbutton(
                attachment_frame,
                text=type_name,
                variable=var,
                command=lambda t=type_name: self.on_config_type_check(t),
                state='disabled'  # 初始状态为禁用
            )
            check.pack(anchor='w', padx=5, pady=2)
            self.config_type_vars[type_name] = {
                'var': var,
                'check': check
            }
        
        # 可用配件选择
        available_frame = ttk.LabelFrame(right_frame, text="可用配件")
        available_frame.pack(fill='both', expand=True)
        self.config_available_listbox = tk.Listbox(available_frame, width=30, height=8)
        self.config_available_listbox.pack(fill='both', expand=True)
        
        # 添加选择事件绑定
        self.config_available_listbox.bind('<<ListboxSelect>>', self.on_available_attachment_select)
        
        # 添加和移除配件的按钮
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill='x', pady=5)
        self.add_attachment_button = ttk.Button(
            button_frame, 
            text="添加配件", 
            command=self.add_config_attachment,
            state='disabled'
        )
        self.add_attachment_button.pack(side='left', padx=5)
        
        self.remove_attachment_button = ttk.Button(
            button_frame, 
            text="移除配件", 
            command=self.remove_config_attachment,
            state='disabled'
        )
        self.remove_attachment_button.pack(side='left', padx=5)
        
        # 基础属性显示
        base_stats_frame = ttk.LabelFrame(right_frame, text="基础属性")
        base_stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.base_stats_labels = {}
        stats_fields = [
            ('recoil_control', '后坐力控制'),
            ('handling_speed', '操控速度'),
            ('ads_stability', '据枪稳定性'),
            ('hip_fire_accuracy', '腰际射击精度')
        ]
        
        for i, (field, label) in enumerate(stats_fields):
            ttk.Label(base_stats_frame, text=f"{label}:").grid(row=i, column=0, padx=5, pady=2)
            value_label = ttk.Label(base_stats_frame, text="0")
            value_label.grid(row=i, column=1, padx=5, pady=2)
            self.base_stats_labels[field] = value_label
        
        # 配件加成显示
        mods_frame = ttk.LabelFrame(right_frame, text="配件加成")
        mods_frame.pack(fill='x', padx=5, pady=5)
        
        self.mods_labels = {}
        for i, (field, label) in enumerate(stats_fields):
            ttk.Label(mods_frame, text=f"{label}加成:").grid(row=i, column=0, padx=5, pady=2)
            value_label = ttk.Label(mods_frame, text="0")
            value_label.grid(row=i, column=1, padx=5, pady=2)
            self.mods_labels[field] = value_label
        
        # 最终属性显示
        final_stats_frame = ttk.LabelFrame(right_frame, text="最终属性")
        final_stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.final_stats_labels = {}
        for i, (field, label) in enumerate(stats_fields):
            ttk.Label(final_stats_frame, text=f"{label}:").grid(row=i, column=0, padx=5, pady=2)
            value_label = ttk.Label(final_stats_frame, text="0")
            value_label.grid(row=i, column=1, padx=5, pady=2)
            self.final_stats_labels[field] = value_label
        
        # 更新枪械列表
        self.update_config_weapon_list()
    
    def update_config_weapon_list(self):
        """更新配置页面的枪械列表"""
        self.config_weapon_listbox.delete(0, tk.END)
        for weapon in self.weapons:
            self.config_weapon_listbox.insert(tk.END, weapon.name)
    
    def on_config_weapon_select(self, event):
        """当在配置页面选择枪械时"""
        selection = self.config_weapon_listbox.curselection()
        if not selection:
            # 清除当前选择
            self.current_weapon_label.config(text="未选择枪械")
            # 禁用所有配件类型选择
            for type_data in self.config_type_vars.values():
                type_data['check'].config(state='disabled')
                type_data['var'].set(False)
            # 禁用按钮
            self.add_attachment_button.config(state='disabled')
            self.remove_attachment_button.config(state='disabled')
            return
        
        weapon = self.weapons[selection[0]]
        # 更新当前选中枪械显示
        self.current_weapon_label.config(text=weapon.name)
        
        # 启用所有配件类型选择
        for type_data in self.config_type_vars.values():
            type_data['check'].config(state='normal')
        
        # 启用按钮
        self.add_attachment_button.config(state='normal')
        self.remove_attachment_button.config(state='normal')
        
        # 清除所有选中状态
        for type_data in self.config_type_vars.values():
            type_data['var'].set(False)
        
        # 清空可用配件列表
        self.config_available_listbox.delete(0, tk.END)
        
        # 更新基础属性显示
        base_stats = {
            'recoil_control': weapon.recoil_control,
            'handling_speed': weapon.handling_speed,
            'ads_stability': weapon.ads_stability,
            'hip_fire_accuracy': weapon.hip_fire_accuracy
        }
        
        for field, label in self.base_stats_labels.items():
            label.config(text=str(base_stats[field]))
        
        # 计算并显示配件加成
        total_mods = {
            'recoil_control': 0,
            'handling_speed': 0,
            'ads_stability': 0,
            'hip_fire_accuracy': 0
        }
        
        for attachment in weapon.attachments:
            total_mods['recoil_control'] += attachment.recoil_mod
            total_mods['handling_speed'] += attachment.handling_mod
            total_mods['ads_stability'] += attachment.stability_mod
            total_mods['hip_fire_accuracy'] += attachment.hip_fire_mod
        
        for field, label in self.mods_labels.items():
            mod_value = total_mods[field]
            label.config(text=f"{mod_value:+}" if mod_value != 0 else "0")
        
        # 更新最终属性显示
        modified_stats = weapon.get_modified_stats()
        field_to_key = {
            'recoil_control': '后坐力控制',
            'handling_speed': '操控速度',
            'ads_stability': '据枪稳定性',
            'hip_fire_accuracy': '腰际射击精度'
        }
        
        for field, label in self.final_stats_labels.items():
            label.config(text=str(modified_stats[field_to_key[field]]))
    
    def on_config_type_check(self, type_name):
        """当配件类型复选状态改变时"""
        weapon_selection = self.config_weapon_listbox.curselection()
        if not weapon_selection:
            self.config_type_vars[type_name].set(False)  # 如果没有选择武器，取消勾选
            messagebox.showwarning("警", "请先选择一个枪械")
            return
        
        weapon = self.weapons[weapon_selection[0]]
        
        # 如果取消勾选，清空可用配件列表
        if not self.config_type_vars[type_name].get():
            self.config_available_listbox.delete(0, tk.END)
            return
        
        # 取消其他类型的选中状态
        for t, var in self.config_type_vars.items():
            if t != type_name:
                var.set(False)
        
        # 更新可用配件列表
        self.config_available_listbox.delete(0, tk.END)
        
        # 获取该类型的所有可用配件
        available_attachments = get_available_attachments(weapon.name, type_name)
        
        # 显示当前安装的配件（如果有）
        installed = next((att for att in weapon.attachments if att.attachment_type == type_name), None)
        if installed:
            self.config_available_listbox.insert(tk.END, f"当前安装: {installed.name}")
            self.config_available_listbox.insert(tk.END, "-" * 30)
        
        # 显示可用配件
        for att in available_attachments:
            self.config_available_listbox.insert(tk.END, att['name'])
    
    def add_config_attachment(self):
        """在配置页面添加配件"""
        weapon_selection = self.config_weapon_listbox.curselection()
        if not weapon_selection:
            messagebox.showwarning("警告", "请选择一个械")
            return
        
        # 获取选中的配件类型
        selected_type = None
        for type_name, var in self.config_type_vars.items():
            if var.get():
                selected_type = type_name
                break
        
        if not selected_type:
            messagebox.showwarning("警告", "请选择配件类型")
            return
        
        available_selection = self.config_available_listbox.curselection()
        if not available_selection:
            messagebox.showwarning("警告", "请选择具体配件")
            return
        
        # 保存当前选择的索引
        weapon_idx = weapon_selection[0]
        available_idx = available_selection[0]
        
        weapon = self.weapons[weapon_idx]
        
        # 获取选中的配件文本
        available_text = self.config_available_listbox.get(available_idx)
        
        # 跳过分线和"当前安装"项
        if available_text.startswith("当前安装:") or available_text.startswith("-"):
            return
        
        # 获取可用配件列表
        available_attachments = get_available_attachments(weapon.name, selected_type)
        
        try:
            # 查找选中的配件数据
            selected_attachment = None
            for att in available_attachments:
                if att['name'] == available_text:
                    selected_attachment = att
                    break
            
            if selected_attachment:
                # 创建并添加配件
                attachment = Attachment(
                    name=selected_attachment['name'],
                    attachment_type=selected_type,
                    recoil_mod=selected_attachment['recoil_mod'],
                    handling_mod=selected_attachment['handling_mod'],
                    stability_mod=selected_attachment['stability_mod'],
                    hip_fire_mod=selected_attachment['hip_fire_mod'],
                    can_mount_grip=selected_attachment.get('can_mount_grip', False)
                )
                
                weapon.add_attachment(attachment)
                save_weapon(weapon)
                
                # 更新显示
                self.on_config_weapon_select(None)
                
                # 恢复选择状态
                self.config_weapon_listbox.selection_clear(0, tk.END)
                self.config_weapon_listbox.selection_set(weapon_idx)
                self.config_type_vars[selected_type].set(True)
                self.on_config_type_check(selected_type)
                
                messagebox.showinfo("成功", "配件添加成功！")
            else:
                messagebox.showerror("错误", "无法找到选中的配件数据")
                
        except ValueError as e:
            messagebox.showerror("错误", str(e))
    
    def remove_config_attachment(self):
        """在配置页面移除配件"""
        weapon_selection = self.config_weapon_listbox.curselection()
        if not weapon_selection:
            messagebox.showwarning("警告", "请选择一个枪械")
            return
        
        # 获取选中的配件类型
        selected_type = None
        for type_name, var in self.config_type_vars.items():
            if var.get():
                selected_type = type_name
                break
        
        if not selected_type:
            messagebox.showwarning("警告", "请选择配件类型")
            return
        
        weapon = self.weapons[weapon_selection[0]]
        
        # 查找并移除配件
        attachment = next((att for att in weapon.attachments if att.attachment_type == selected_type), None)
        if attachment:
            weapon.remove_attachment(attachment.name)
            save_weapon(weapon)
            
            # 更新显示
            self.on_config_weapon_select(None)
            messagebox.showinfo("成功", "配件移除成功！")
        else:
            messagebox.showinfo("提示", "该类型没有已安装的配件")
    
    def create_btk_calculator_tab(self):
        """创建BTK计算器标签页"""
        btk_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(btk_frame, text='BTK计算器')
        
        # 配置网格
        btk_frame.grid_rowconfigure(1, weight=1)
        btk_frame.grid_columnconfigure(0, weight=1)
        
        # 生命值输入
        input_frame = ttk.Frame(btk_frame)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # 为文本框添加滚动条
        text_scroll = ttk.Scrollbar(btk_frame)
        self.btk_result_text = tk.Text(btk_frame, height=20, width=50,
                                      yscrollcommand=text_scroll.set)
        text_scroll.config(command=self.btk_result_text.yview)
        
        self.btk_result_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        text_scroll.pack(side='right', fill='y')
        
        ttk.Label(input_frame, text="目标生命值:").pack(side='left')
        self.health_entry = ttk.Entry(input_frame, width=10)
        self.health_entry.pack(side='left', padx=5)
        self.health_entry.insert(0, "100")
        
        ttk.Button(input_frame, text="计算", command=self.calculate_btk).pack(side='left', padx=5)
    
    def update_weapon_list(self):
        """更新武器列表"""
        self.weapon_listbox.delete(0, tk.END)
        for weapon in self.weapons:
            self.weapon_listbox.insert(tk.END, weapon.name)
    
    def update_attachment_weapon_list(self):
        """更新配件管理中的武器列表"""
        self.attachment_weapon_listbox.delete(0, tk.END)
        for weapon in self.weapons:
            self.attachment_weapon_listbox.insert(tk.END, weapon.name)
    
    def on_weapon_select(self, event):
        """当选择武器时更新显示信息"""
        selection = self.weapon_listbox.curselection()
        if not selection:
            # 清空所有输入框和选择
            for field, entry in self.weapon_entries.items():
                entry.delete(0, tk.END)
            self.weapon_type_var.set('')
            for var in self.soldier_class_vars.values():
                var.set(False)
            return
        
        weapon = self.weapons[selection[0]]
        
        # 更新基本属性输入框
        basic_fields = {
            'name': weapon.name,
            'base_damage': weapon.base_damage,
            'stomach_damage': weapon.stomach_damage,
            'limb_damage': weapon.limb_damage,
            'foot_damage': weapon.foot_damage,
            'range_meters': weapon.range_meters,
            'fire_rate': weapon.fire_rate,
            'recoil_control': weapon.recoil_control,
            'handling_speed': weapon.handling_speed,
            'ads_stability': weapon.ads_stability,
            'hip_fire_accuracy': weapon.hip_fire_accuracy
        }
        
        # 更新所有输入框
        for field, value in basic_fields.items():
            if field in self.weapon_entries:
                self.weapon_entries[field].delete(0, tk.END)
                self.weapon_entries[field].insert(0, str(value))
        
        # 更新枪械类型选择
        if weapon.weapon_type:
            self.weapon_type_var.set(weapon.weapon_type)
        
        # 更新兵种选择
        for sclass, var in self.soldier_class_vars.items():
            var.set(sclass in weapon.soldier_classes)
        
        # 打印调试信息
        print("\n选中枪械详细信息:")
        print(f"名称: {weapon.name}")
        print(f"枪械类型: {weapon.weapon_type}")
        print(f"适用兵种: {weapon.soldier_classes}")
        print("基本属性:")
        for field, value in basic_fields.items():
            print(f"  {field}: {value}")
    
    def on_soldier_class_select(self, event):
        """当选择兵种时"""
        soldier_class = self.soldier_class_combo.get()
        if not soldier_class:
            return
        
        # 更新枪械类型下拉框
        available_types = set()
        for weapon in self.weapons:
            if soldier_class in weapon.soldier_classes:
                available_types.add(weapon.weapon_type)
        
        # 按照预定义的顺序排序械类型
        sorted_types = [wtype for wtype in Weapon.WEAPON_TYPES if wtype in available_types]
        
        # 更新枪械类型下拉框
        self.weapon_type_combo['values'] = sorted_types
        self.weapon_type_combo.set('')  # 清除当前选择
        
        # 清空枪械名称下拉框
        self.weapon_name_combo['values'] = []
        self.weapon_name_combo.set('')
    
    def on_weapon_type_select(self, event):
        """当选择枪械类型时"""
        soldier_class = self.soldier_class_combo.get()
        weapon_type = self.weapon_type_combo.get()
        
        if not soldier_class or not weapon_type:
            return
        
        # 取符合条件的枪械
        matching_weapons = []
        for weapon in self.weapons:
            if (soldier_class in weapon.soldier_classes and 
                weapon.weapon_type == weapon_type):
                matching_weapons.append(weapon)
        
        # 按名称排序
        matching_weapons.sort(key=lambda w: w.name)
        weapon_names = [w.name for w in matching_weapons]
        
        # 更新枪械名称下拉框
        self.weapon_name_combo['values'] = weapon_names
        self.weapon_name_combo.set('')  # 清除当前选择
        
        print(f"\n选择枪械类型: {weapon_type}")
        print(f"可用枪械: {weapon_names}")
    
    def on_attachment_weapon_select(self, event):
        """当选择枪械时"""
        weapon_name = self.weapon_name_combo.get()
        if not weapon_name:
            return
        
        # 查找选中的武器
        weapon = next((w for w in self.weapons if w.name == weapon_name), None)
        if not weapon:
            return
        
        # 更新配件树形视图
        self.update_attachment_tree()  # 确保这个方法存在
        
        print(f"\n选择枪械: {weapon_name}")
        if weapon.attachments:
            print("已安装配件:")
            for att in weapon.attachments:
                print(f"- {att.name} ({att.attachment_type})")
        else:
            print("当前没有已安装的配件")
    
    def add_weapon(self):
        """添加新枪械"""
        try:
            # 检查是否选择了枪械类型
            if not self.weapon_type_var.get():
                messagebox.showwarning("警告", "请选择枪械类型")
                return
            
            # 检查是否选择了至少一个兵种
            selected_classes = [
                sclass for sclass, var in self.soldier_class_vars.items() 
                if var.get()
            ]
            if not selected_classes:
                messagebox.showwarning("警告", "请选择至少一个适用兵种")
                return
            
            weapon_data = {}
            for field, entry in self.weapon_entries.items():
                value = entry.get()
                weapon_data[field] = float(value) if field != 'name' else value
            
            # 添加类型和兵种数据
            weapon_data['weapon_type'] = self.weapon_type_var.get()
            weapon_data['soldier_classes'] = selected_classes
            
            weapon = Weapon(**weapon_data)
            self.weapons.append(weapon)
            save_weapon(weapon)
            self.update_weapon_list()
            self.update_attachment_weapon_list()
            messagebox.showinfo("成功", "枪械添加成功！")
        except Exception as e:
            messagebox.showerror("错误", f"添加枪械失败: {str(e)}")
    
    def save_weapon(self):
        """保存枪械修改"""
        selection = self.weapon_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个枪械")
            return
        
        try:
            weapon = self.weapons[selection[0]]
            
            # 保存基本属性
            for field, entry in self.weapon_entries.items():
                value = entry.get()
                setattr(weapon, field, float(value) if field != 'name' else value)
            
            # 保存枪械类型
            weapon.weapon_type = self.weapon_type_var.get()
            
            # 保存适用兵种
            weapon.soldier_classes = [
                sclass for sclass, var in self.soldier_class_vars.items() 
                if var.get()
            ]
            
            save_weapon(weapon)
            messagebox.showinfo("成功", "修改已保存")
            
            # 打印试信息
            print(f"保存枪械: {weapon.name}")
            print(f"枪械类型: {weapon.weapon_type}")
            print(f"适用兵种: {weapon.soldier_classes}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def delete_weapon(self):
        """删除枪械"""
        selection = self.weapon_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个枪械")
            return
        
        weapon = self.weapons[selection[0]]
        if messagebox.askyesno("确认", f"确定要删除 {weapon.name} 吗？"):
            if delete_weapon(weapon.name):
                self.weapons.pop(selection[0])
                # 更新所有相关的列表和显示
                self.update_all_weapon_lists()
                messagebox.showinfo("成功", "枪械已删除")
            else:
                messagebox.showerror("错误", "删除失败")
    
    def update_all_weapon_lists(self):
        """更新所有涉及到枪械列表的显示"""
        # 更新枪械管理标签页的列表
        self.update_weapon_list()
        
        # 更新配件管理标签页的下拉框
        if hasattr(self, 'weapon_name_combo'):
            current_selection = self.weapon_name_combo.get()
            self.weapon_name_combo['values'] = [w.name for w in self.weapons]
            if current_selection not in self.weapon_name_combo['values']:
                self.weapon_name_combo.set('')
        
        # 更新枪械配置标签页的列表
        if hasattr(self, 'config_weapon_listbox'):
            self.update_config_weapon_list()
    
    def add_attachment(self):
        """添加配件"""
        type_selection = self.attachment_type_listbox.curselection()
        if not type_selection:
            messagebox.showwarning("警告", "请选择配件类型")
            return
        
        try:
            attachment_type = list(Attachment.TYPES.values())[type_selection[0]]
            
            # 收集配件基本数据
            attachment_data = {
                'name': self.attachment_entries['name'].get(),
                'attachment_type': attachment_type,
                'recoil_mod': float(self.attachment_entries['recoil_mod'].get()),
                'handling_mod': float(self.attachment_entries['handling_mod'].get()),
                'stability_mod': float(self.attachment_entries['stability_mod'].get()),
                'hip_fire_mod': float(self.attachment_entries['hip_fire_mod'].get())
            }
            
            if attachment_type == '后握把':
                attachment_data['can_mount_grip'] = self.can_mount_grip_var.get()
            
            # 处理特定武器配件
            if self.is_specific_var.get():
                weapon_name = self.specific_weapon_entry.get().strip()
                if not weapon_name:
                    messagebox.showwarning("警告", "请输入适用的武器名称")
                    return
                
                # 保存配件数据
                if weapon_name not in ATTACHMENTS_DATA['specific']:
                    ATTACHMENTS_DATA['specific'][weapon_name] = {}
                if attachment_type not in ATTACHMENTS_DATA['specific'][weapon_name]:
                    ATTACHMENTS_DATA['specific'][weapon_name][attachment_type] = []
                ATTACHMENTS_DATA['specific'][weapon_name][attachment_type].append(attachment_data)
                
                save_attachments_data()
                messagebox.showinfo("成功", "特定武器配件添加成功！")
            else:
                # 通用配件的处理逻辑保持不变
                if attachment_type not in ATTACHMENTS_DATA['common']:
                    ATTACHMENTS_DATA['common'][attachment_type] = []
                ATTACHMENTS_DATA['common'][attachment_type].append(attachment_data)
                
                save_attachments_data()
                messagebox.showinfo("成功", "通用配件添加成功！")
                
                # 清空输入框
                for entry in self.attachment_entries.values():
                    entry.delete(0, tk.END)
                self.can_mount_grip_var.set(False)
                self.is_specific_var.set(False)
                self.specific_weapon_frame.grid_remove()  # 隐藏武器名称输入框
            
        except ValueError as e:
            messagebox.showerror("错误", f"添加配件失: {str(e)}")
    
    def create_weapon_input_window(self):
        """创建枪械输入窗口"""
        weapon_input = tk.Toplevel(self.root)
        weapon_input.title("添加新枪械")
        
        # 创建输入框
        input_frame = ttk.Frame(weapon_input)
        input_frame.pack(padx=10, pady=10)
        
        entries = {}
        row = 0
        
        # 基本信息
        basic_fields = [
            ('name', '枪械名称'),
            ('base_damage', '胸部基础伤害'),
            ('stomach_damage', '腹部伤害'),
            ('limb_damage', '手部伤害'),
            ('foot_damage', '脚部伤害'),
            ('range_meters', '射程(米)'),
            ('fire_rate', '射速(发/分钟)')
        ]
        
        for field, label in basic_fields:
            ttk.Label(input_frame, text=label).grid(row=row, column=0, padx=5, pady=2)
            entry = ttk.Entry(input_frame)
            entry.grid(row=row, column=1, padx=5, pady=2)
            entries[field] = entry
            row += 1
        
        # 性能参数
        ttk.Label(input_frame, text="\n性能参数 (1-100):").grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        stats_fields = [
            ('recoil_control', '后坐力控制'),
            ('handling_speed', '操控速度'),
            ('ads_stability', '据枪稳定性'),
            ('hip_fire_accuracy', '腰际射击精度')
        ]
        
        for field, label in stats_fields:
            ttk.Label(input_frame, text=label).grid(row=row, column=0, padx=5, pady=2)
            entry = ttk.Entry(input_frame)
            entry.grid(row=row, column=1, padx=5, pady=2)
            entries[field] = entry
            row += 1
        
        def save_weapon():
            try:
                weapon_data = {}
                for field, entry in entries.items():
                    value = entry.get()
                    weapon_data[field] = float(value) if field != 'name' else value
                
                weapon = Weapon(**weapon_data)
                self.weapons.append(weapon)
                save_weapon(weapon)
                self.update_weapon_list()
                self.update_attachment_weapon_list()
                messagebox.showinfo("成功", "枪械添加成功！")
                weapon_input.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"添加枪械失败: {str(e)}")
        
        # 按钮
        button_frame = ttk.Frame(weapon_input)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="保存", command=save_weapon).pack(side='left', padx=5)
        ttk.Button(button_frame, text="取消", command=weapon_input.destroy).pack(side='left', padx=5)
        
        # 使窗口模态
        weapon_input.transient(self.root)
        weapon_input.grab_set()
    
    def view_installed_attachments(self):
        """查看已安装的配件"""
        weapon_selection = self.attachment_weapon_listbox.curselection()
        if not weapon_selection:
            messagebox.showwarning("警告", "请选择一个枪械")
            return
        
        weapon = self.weapons[weapon_selection[0]]
        if not weapon.attachments:
            messagebox.showinfo("信息", "当前没有安装的配件")
            return
        
        # 创建新窗口显示配件信息
        top = tk.Toplevel(self.root)
        top.title(f"{weapon.name} - 已安装配件")
        
        text = tk.Text(top, height=20, width=50)
        text.pack(padx=5, pady=5)
        
        for att in weapon.attachments:
            text.insert(tk.END, f"\n- {att.name} ({att.attachment_type}):\n")
            if att.recoil_mod: text.insert(tk.END, f"  后坐力修改: {att.recoil_mod:+}\n")
            if att.handling_mod: text.insert(tk.END, f"  操控速度修改: {att.handling_mod:+}\n")
            if att.stability_mod: text.insert(tk.END, f"  据枪稳定性修改: {att.stability_mod:+}\n")
            if att.hip_fire_mod: text.insert(tk.END, f"  腰际射击精度修改: {att.hip_fire_mod:+}\n")
            if hasattr(att, 'can_mount_grip'):
                text.insert(tk.END, f"  可安装握把座: {'是' if att.can_mount_grip else '否'}\n")
    
    def calculate_btk(self):
        """计算BTK"""
        try:
            health = float(self.health_entry.get())
            self.btk_result_text.delete(1.0, tk.END)
            
            for weapon in self.weapons:
                self.btk_result_text.insert(tk.END, f"\n{weapon.name}的BTK:\n")
                btks = weapon.calculate_btk(health)
                for part, btk in btks.items():
                    self.btk_result_text.insert(tk.END, f"{part}: {btk}发\n")
                kill_time_ms = (min(btks.values()) - 1) * (60000 / weapon.fire_rate)
                self.btk_result_text.insert(tk.END, f"最快理论击杀时间: {kill_time_ms:.1f}毫秒\n")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的生命值")
    
    def on_available_attachment_select(self, event):
        """当选择可用配件时"""
        # 防止事件处理过程中的选择状态丢失
        self.root.after(100, self.maintain_selection_state)

    def maintain_selection_state(self):
        """维持选择状态"""
        # 保存当前选择状态
        weapon_selection = self.config_weapon_listbox.curselection()
        if not weapon_selection:
            return
        
        # 获取选中的配件类型
        selected_type = None
        for type_name, var in self.config_type_vars.items():
            if var.get():
                selected_type = type_name
                break
        
        if not selected_type:
            return
        
        # 确保选择状态保持不变
        self.config_weapon_listbox.selection_clear(0, tk.END)
        self.config_weapon_listbox.selection_set(weapon_selection[0])
        self.config_type_vars[selected_type].set(True)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeaponSystemGUI(root)
    root.mainloop() 