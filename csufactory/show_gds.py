import os
import pathlib
import json
import gdstk
import subprocess
from csufactory import klive
from csufactory import component

#输出gds文件到指定文件夹
def export_gds(
            component,
            filename="output.gds", 
            filepath="C:/Windows/System32/csufactory/csufactory/all_output_files/gds"
        ):
    """导出并保存 GDS 文件，支持自定义路径"""
    os.makedirs(filepath, exist_ok=True)           # 确保目录存在
    file_path = os.path.join(filepath, filename)   # 生成完整的文件路径
    lib = gdstk.Library()                          # 创建 GDS 库
    # 如果使用 gdspy，这里改成 gdspy.Library()
    lib.add(component.cell)                        # 添加 GDS 结构
    lib.write_gds(file_path)                       # 保存 GDS 文件
    print(f"GDSII file saved at: {file_path}")
    return file_path                               #返回文件路径，方便 `show()` 直接调用

#将gds文件同步到klayout
def show(
        component, 
        gdspath="filepath", 
        **kwargs
    ):
    """ write component GDS and shows it in klayout

    Args:
        component
        gdspath: where to save the gds
    """
    os.makedirs(gdspath, exist_ok=True)            # 确保目录存在
    file_path = os.path.join(gdspath)              # 生成完整的文件路径
    component = str(component)
    if isinstance(component, str):
        return klive.show(component)
    if component is None:
        raise ValueError(
            "Component is None, make sure that your function returns the component"
        )
    #生成 GDS 文件，并获取其路径
    gds_file = export_gds(component, filename="output.gds", filepath=gdspath)
    klive.show(gds_file)
    
    return