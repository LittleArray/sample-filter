import os
import shutil
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class ImageClassifier:
    def __init__(self, root):
        self.root = root
        self.root.title("图片样本筛选器")
        self.root.geometry("800x600")

        # 目录配置
        self.input_dir = "./input"
        self.output_dir = "./output"
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # 支持的图片格式
        self.supported_ext = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

        # 加载图片列表
        self.load_image_list()

        # 操作历史栈 (每个元素为 (源路径, 目标路径))
        self.history = []

        # 当前图片索引
        self.current_index = 0 if self.image_list else -1

        # 创建UI组件
        self.create_widgets()

        # 绑定键盘事件
        self.root.bind('<Return>', self.cut_image)      # Enter键剪切
        self.root.bind('<z>', self.undo)                # 小写z撤销
        self.root.bind('<Z>', self.undo)                # 大写Z撤销
        self.root.bind('<Left>', self.prev_image)       # 左箭头上一张
        self.root.bind('<Right>', self.next_image)      # 右箭头下一张

        # 刷新显示
        self.update_display()

    def load_image_list(self):
        """扫描input目录，获取所有图片文件路径并排序"""
        if not os.path.exists(self.input_dir):
            self.image_list = []
            return
        files = os.listdir(self.input_dir)
        self.image_list = [
            os.path.join(self.input_dir, f) for f in files
            if f.lower().endswith(self.supported_ext)
        ]
        self.image_list.sort()

    def rename_output_images(self):
        """将output文件夹下的图片批量重命名为 0001.扩展名 格式"""
        output_dir = self.output_dir
        if not os.path.exists(output_dir):
            messagebox.showinfo("提示", "output文件夹不存在")
            return
        
        # 获取所有图片文件
        files = [f for f in os.listdir(output_dir) if f.lower().endswith(self.supported_ext)]
        if not files:
            messagebox.showinfo("提示", "output文件夹中没有图片")
            return
        
        # 询问确认
        if not messagebox.askyesno("确认", f"即将重命名 {len(files)} 个文件，\n格式：0001、0002...\n是否继续？"):
            return
        
        # 按文件名排序（确保顺序可预测）
        files.sort()
        renamed_count = 0
        
        for idx, filename in enumerate(files, start=1):
            ext = os.path.splitext(filename)[1]  # 包含点，如 ".jpg"
            new_name = f"{idx:04d}{ext}"
            old_path = os.path.join(output_dir, filename)
            new_path = os.path.join(output_dir, new_name)
            
            # 如果新文件名已存在且不是同一文件，添加后缀避免冲突
            if os.path.exists(new_path) and old_path != new_path:
                base = f"{idx:04d}"
                counter = 1
                while os.path.exists(os.path.join(output_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                new_name = f"{base}_{counter}{ext}"
                new_path = os.path.join(output_dir, new_name)
            
            try:
                os.rename(old_path, new_path)
                renamed_count += 1
            except Exception as e:
                messagebox.showerror("错误", f"重命名失败: {filename}\n{str(e)}")
                return
        
        messagebox.showinfo("完成", f"成功重命名 {renamed_count} 个文件")

    def create_widgets(self):
        """创建GUI控件"""
        # 顶部信息栏
        self.info_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.info_label.pack(pady=5)

        # 图片显示区域 (用Label显示图像)
        self.image_label = tk.Label(self.root, bg="gray", relief="sunken")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)

        # 底部提示栏
        tip_text = (
            "操作说明：\n"
            "▶ 按 [Enter] 键：将当前图片剪切到 output 文件夹\n"
            "◀ 按 [Z] 键：撤销上一次剪切操作\n"
            "◀ 按 [←] 或 [→] 键：切换上一张/下一张图片"
        )
        self.tip_label = tk.Label(self.root, text=tip_text, font=("Arial", 10),
                                  justify="left", bg="#f0f0f0", relief="groove")
        self.tip_label.pack(side="bottom", fill="x", padx=5, pady=5)

        # 控制按钮框架（可选，方便操作）
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        self.prev_btn = tk.Button(button_frame, text="上一张 (←)", command=self.prev_image)
        self.prev_btn.pack(side="left", padx=10)

        self.next_btn = tk.Button(button_frame, text="下一张 (→)", command=self.next_image)
        self.next_btn.pack(side="left", padx=10)

        self.cut_btn = tk.Button(button_frame, text="剪切 (Enter)", command=lambda: self.cut_image(None))
        self.cut_btn.pack(side="left", padx=10)

        self.undo_btn = tk.Button(button_frame, text="撤销 (Z)", command=lambda: self.undo(None))
        self.undo_btn.pack(side="left", padx=10)
        
        self.rename_btn = tk.Button(button_frame, text="输出批量重命名", command=self.rename_output_images)
        self.rename_btn.pack(side="left", padx=10)

    def update_display(self):
        """更新显示当前图片"""
        if self.current_index >= 0 and self.current_index < len(self.image_list):
            img_path = self.image_list[self.current_index]
            try:
                # 用PIL打开图片并调整大小适应显示区域
                pil_img = Image.open(img_path)
                # 获取显示区域大小（预留边距）
                display_width = self.image_label.winfo_width() - 20
                display_height = self.image_label.winfo_height() - 20
                if display_width <= 10 or display_height <= 10:
                    # 初始时窗口尚未完全布局，使用默认大小
                    display_width, display_height = 600, 400
                pil_img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                self.tk_img = ImageTk.PhotoImage(pil_img)
                self.image_label.config(image=self.tk_img, text="")
            except Exception as e:
                self.image_label.config(image="", text=f"无法加载图片:\n{img_path}\n错误: {e}")
                self.tk_img = None
            # 更新信息栏
            total = len(self.image_list)
            filename = os.path.basename(img_path)
            self.info_label.config(text=f"{self.current_index+1}/{total}  {filename}")
        else:
            # 无图片时显示提示
            self.image_label.config(image="", text="没有可预览的图片\n请将图片放入 ./input 目录")
            self.info_label.config(text="0/0  无图片")
            self.tk_img = None

    def cut_image(self, event=None):
        """将当前图片剪切到output目录"""
        if self.current_index < 0 or self.current_index >= len(self.image_list):
            messagebox.showinfo("提示", "没有可剪切的图片")
            return

        src_path = self.image_list[self.current_index]
        filename = os.path.basename(src_path)
        dst_path = os.path.join(self.output_dir, filename)

        try:
            # 执行移动（剪切）
            shutil.move(src_path, dst_path)
            # 记录操作历史
            self.history.append((src_path, dst_path))
            # 从图片列表中移除当前图片
            self.image_list.pop(self.current_index)

            # 调整索引
            if self.current_index >= len(self.image_list):
                self.current_index = len(self.image_list) - 1

            self.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"剪切失败:\n{str(e)}")

    def undo(self, event=None):
        """撤销上一次剪切操作，将文件从output移回input"""
        if not self.history:
            messagebox.showinfo("提示", "没有可撤销的操作")
            return

        src_path, dst_path = self.history.pop()
        # 检查目标文件是否存在（可能被手动删除或覆盖）
        if not os.path.exists(dst_path):
            messagebox.showwarning("警告", f"无法撤销，文件已不存在:\n{dst_path}")
            return

        try:
            # 移回原位置
            shutil.move(dst_path, src_path)
            # 重新加载图片列表（保持顺序）
            self.load_image_list()
            # 尝试定位到刚刚撤销回来的图片
            filename = os.path.basename(src_path)
            try:
                new_index = self.image_list.index(src_path)
            except ValueError:
                # 若文件名冲突（理论上不会），则设为第一张
                new_index = 0
            self.current_index = new_index if self.image_list else -1
            self.update_display()
        except Exception as e:
            messagebox.showerror("错误", f"撤销失败:\n{str(e)}")

    def prev_image(self, event=None):
        """显示上一张图片"""
        if self.image_list:
            self.current_index = (self.current_index - 1) % len(self.image_list)
            self.update_display()

    def next_image(self, event=None):
        """显示下一张图片"""
        if self.image_list:
            self.current_index = (self.current_index + 1) % len(self.image_list)
            self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifier(root)
    root.mainloop()