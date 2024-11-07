import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import tempfile
from wand.image import Image as WandImage
import logging
import shutil
from PIL import Image, ImageTk

class ImageConverterApp:
    def __init__(self):
        # 设置主题和颜色模式
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.app = ctk.CTk()
        self.app.title("DDSTGA 图片格式转换器")
        self.app.geometry("900x600")
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon', 'logo.ico')
        if os.path.exists(icon_path):
            self.app.iconbitmap(icon_path)
        
        # 创建临时目录
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Temp')
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # 设置环境变量
        os.environ['MAGICK_TEMPORARY_PATH'] = self.temp_dir
        os.environ['MAGICK_TMPDIR'] = self.temp_dir
        tempfile.tempdir = self.temp_dir
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.app)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # 输入文件区域
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(pady=10, padx=10, fill="x")
        
        self.input_label = ctk.CTkLabel(self.input_frame, text="输入文件:")
        self.input_label.pack(side="left", padx=5)
        
        self.input_path = ctk.CTkEntry(self.input_frame, width=500)
        self.input_path.pack(side="left", padx=5)
        
        self.browse_input_btn = ctk.CTkButton(
            self.input_frame, 
            text="浏览", 
            command=self.browse_input,
            width=100
        )
        self.browse_input_btn.pack(side="left", padx=5)
        
        # 输出路径区域
        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.pack(pady=10, padx=10, fill="x")
        
        self.output_label = ctk.CTkLabel(self.output_frame, text="输出路径:")
        self.output_label.pack(side="left", padx=5)
        
        self.output_path = ctk.CTkEntry(self.output_frame, width=500)
        self.output_path.pack(side="left", padx=5)
        
        self.browse_output_btn = ctk.CTkButton(
            self.output_frame, 
            text="浏览", 
            command=self.browse_output,
            width=100
        )
        self.browse_output_btn.pack(side="left", padx=5)
        
        # 转换选项
        self.convert_frame = ctk.CTkFrame(self.main_frame)
        self.convert_frame.pack(pady=10, padx=10, fill="x")
        
        self.convert_type = ctk.CTkSegmentedButton(
            self.convert_frame,
            values=["TGA → DDS", "DDS → TGA"],
            command=self.on_convert_type_change
        )
        self.convert_type.pack(pady=10)
        self.convert_type.set("TGA → DDS")
        
        # 转换按钮
        self.convert_btn = ctk.CTkButton(
            self.main_frame,
            text="开始转换",
            command=self.convert_image,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.convert_btn.pack(pady=10)
        
        # 日志输出框
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log_label = ctk.CTkLabel(self.log_frame, text="日志输出:")
        self.log_label.pack(anchor="w", padx=5, pady=5)
        
        self.log_text = ctk.CTkTextbox(self.log_frame, height=200)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 设置日志处理
        self.setup_logging()

    def setup_logging(self):
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert("end", msg + "\n")
                self.text_widget.see("end")

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def browse_input(self):
        file_types = [
            ("支持的图片格式", "*.dds;*.tga"),
            ("DDS 文件", "*.dds"),
            ("TGA 文件", "*.tga"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=file_types)
        if filename:
            self.input_path.delete(0, "end")
            self.input_path.insert(0, filename)
            # 自动设置输出路径
            output_dir = os.path.dirname(filename)
            self.output_path.delete(0, "end")
            self.output_path.insert(0, output_dir)
            logging.info(f"已选择输入文件: {filename}")

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.delete(0, "end")
            self.output_path.insert(0, directory)
            logging.info(f"已选择输出路径: {directory}")

    def on_convert_type_change(self, value):
        logging.info(f"转换类型已更改为: {value}")

    def convert_image(self):
        input_path = self.input_path.get()
        output_dir = self.output_path.get()
        
        if not input_path or not output_dir:
            messagebox.showerror("错误", "请选择输入文件和输出路径")
            return

        try:
            convert_type = self.convert_type.get()
            input_filename = os.path.basename(input_path)
            output_filename = os.path.splitext(input_filename)[0]
            
            if convert_type == "TGA → DDS":
                output_filename += ".dds"
            else:
                output_filename += ".tga"
                
            output_path = os.path.join(output_dir, output_filename)
            
            logging.info(f"开始转换: {input_path}")
            logging.info(f"输出到: {output_path}")
            
            # 直接读取和写入，不使用临时文件
            with open(input_path, 'rb') as input_file:
                input_data = input_file.read()
                with WandImage(blob=input_data) as img:
                    # 直接写入到输出文件
                    img.format = 'DDS' if convert_type == "TGA → DDS" else 'TGA'
                    img.save(filename=output_path)

            logging.info("转换成功！")
            messagebox.showinfo("成功", "图片转换完成！")
            
        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg)

    def run(self):
        try:
            self.app.mainloop()
        finally:
            # 程序退出时清理临时目录
            if os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                except Exception as e:
                    logging.warning(f"清理临时目录失败: {e}")

if __name__ == "__main__":
    app = ImageConverterApp()
    app.run() 