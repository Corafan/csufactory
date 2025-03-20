import gdsfactory as gf
import datetime
from functools import partial
from csufactory.csupdk.layer_map import CSULAYER as LAYER
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer
from csufactory.components.awg import free_propagation_region
# from csufactory.components.awg import awg
#from gdsfactory.components.awg import wg
nm = 1e-3


#0.45%,Si衬底。后续核对(问号表示待定)：
thickness_substrate: float = 625                   #基板厚度um
thickness_bottom_clad: float = 15                  #下包层——镀层厚度um
thickness_wg: float = 6.5                          #波导层厚度(core)
thickness_top_clad: float = 20                     #上包层——镀层厚度um
thickness_metal_TiN: float = round(200 * nm, 10)   #TiN加热层厚度
#zmin_heater: float = 1.1                          #位置?
thickness_heater_clad: float = 2                   #加热层TiN的氧化层um
thickness_metal_Ti: float = round(1400 * nm, 10)   #间隔层厚度
#zmin_metal_Ti: float = 1.1                        #位置?
thickness_metal_Al: float = round(700 * nm, 10)    #电极层Al的厚度：？
#zmin_metal_Al: float = 2.3                        #位置?
thickness_SiN: float = round(300 * nm, 10)         #保护层SiN厚度
thickness_full_etch = thickness_wg + 1                                #全刻蚀深度

c = gf.Component()

#阵列波导光栅AWG（0.45%，Si基板）：
Si_Sub = c << gf.components.rectangle(size=(100, 100), layer=(88, 0))

#芯层
awg= c << gf.components.awg(
    inputs= 1,
    arms= 9,                                       #阵列波导数量
    outputs= 1,
    free_propagation_region_input_function= partial(free_propagation_region, width1=2, width2=20.0),
    free_propagation_region_output_function= partial(free_propagation_region, width1=2, width2=20.0),
    fpr_spacing= 50.0,                            #输入/输出FPR的间距
    arm_spacing= 1.0,                             #阵列波导间距
)  
#这部分LayerSpec是WG，所以层数为（200，0）=layer_corelayer_core
awg.movex(25)
awg.movey(35)


heater_etch_1 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_1.movex(20)
heater_etch_2 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_2.movex(47.5)
heater_etch_3 = c << gf.components.rectangle(size=(5, 100), layer=(5, 2))
heater_etch_3.movex(75)
heater_clad_etch_1 = c << gf.components.rectangle(size=(45/2, 100), layer=(6, 2))
heater_clad_etch_1.movex(25)
heater_clad_etch_2 = c << gf.components.rectangle(size=(45/2, 100), layer=(6, 2))
heater_clad_etch_2.movex(30+45/2)
wet_etch_electrode = c << gf.components.rectangle(size=(8, 100), layer=(7, 2))
wet_etch_electrode.movex(88)
full_etch_SiN = c << gf.components.rectangle(size=(5, 100), layer=(8, 2))
full_etch_SiN.movex(89.5)

layer_Si_Sub = LogicalLayer(layer=LAYER.Si_Sub)                                         
layer_box = LogicalLayer(layer=LAYER.SiO_Bottom_Clad)                                 
layer_core = LogicalLayer(layer=LAYER.WG)              #这部分实际对应的是器件的形状 
layer_full_etch = LogicalLayer(layer=LAYER.Full_Etch)  #全刻蚀形状还是COUPLER，只不过最后派生成了FullEtch  
layer_top_clad = LogicalLayer(layer=LAYER.SiO_ToP_Clad)                                          
layer_metal_TiN = LogicalLayer(layer=LAYER.Metal_TiN)
layer_wet_etch_heater = LogicalLayer(layer=LAYER.Wet_Etch_Heater)   
layer_heater_clad = LogicalLayer(layer=LAYER.SiO_Oxide_1)       
layer_dry_etch_heater_clad = LogicalLayer(layer=LAYER.Dry_Etch_Heater_Clad) 
layer_metal_Ti = LogicalLayer(layer=LAYER.Metal_Ti) 
layer_metal_Al = LogicalLayer(layer=LAYER.Metal_Al) 
layer_wet_etch_electrode = LogicalLayer(layer=LAYER.Wet_Etch_Electrode) 
layer_SiN = LogicalLayer(layer=LAYER.SiN) 
layer_full_etch_SiN = LogicalLayer(layer=LAYER.Full_Etch_SiN) 

#Si基板，0.45%，layerStack:
Si_zp45_LayerStack= LayerStack(
        layers={
        "substrate":LayerLevel(
            layer=layer_Si_Sub,
            thickness=thickness_substrate,
            zmin=-thickness_substrate-thickness_bottom_clad,                            
            material="silicon",
            mesh_order=101,                   
        ),
        "box":LayerLevel(
            layer=layer_Si_Sub,
            thickness=thickness_bottom_clad,  
            zmin=-thickness_bottom_clad,                          
            material="silicon",
            mesh_order=9,
            derived_layer=layer_box,
            info={
                "refractive_index": 1.444,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 1.5,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
            }
        ), 
        "core":LayerLevel(
            layer=layer_core,
            thickness=thickness_full_etch,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "refractive_index": 1.4504,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.3,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ), 
        "top_clad":LayerLevel(
            layer=layer_Si_Sub,                  
            zmin=0,                                        #？这部分还有待考量，分不同情况，看怎么安排
            material="sio2",
            thickness=thickness_top_clad + thickness_wg,                  #+ thickness_wg？#同上
            mesh_order=10,
            derived_layer=layer_top_clad, 
            info={
                "refractive_index": 1.444,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,                    # 单位 um
                    "solver": "FDTD"
                }
            } 
        ),
        #从这部分开始layer形状没问题，高度有异？
        "TiN":LayerLevel(                        
            layer=layer_Si_Sub ^ layer_wet_etch_heater,
            thickness=thickness_metal_TiN,                 
            zmin=thickness_wg + thickness_top_clad,
            material="TiN",
            mesh_order=2,
            derived_layer=layer_metal_TiN,
        ),
        "heater_clad":LayerLevel(
            layer=layer_Si_Sub ^ layer_dry_etch_heater_clad,            
            zmin=thickness_wg + thickness_top_clad,       #因为这里只有一种情况，全刻蚀            
            material="sio2",
            thickness=thickness_heater_clad,              
            mesh_order=2,
            derived_layer=layer_heater_clad,
        ),
        "Ti":LayerLevel(
            layer=layer_Si_Sub,
            thickness=thickness_metal_Ti,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN,
            material="Titanium",
            mesh_order=2,
            derived_layer=layer_metal_Ti,
        ),
        "Al":LayerLevel(
            layer=layer_dry_etch_heater_clad + layer_wet_etch_electrode, 
            thickness=thickness_metal_Al,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN + thickness_metal_Ti,          
            material="Aluminum",
            mesh_order=2,
            derived_layer=layer_metal_Al,
        ),
        "SiN":LayerLevel(
            layer=layer_Si_Sub ^ layer_full_etch_SiN,
            thickness=thickness_SiN,
            zmin=thickness_wg + thickness_top_clad + thickness_metal_TiN + thickness_heater_clad + thickness_metal_Ti,
            material="SiN",
            mesh_order=2,
            derived_layer=layer_SiN,
        ),
    }
)

#直波导，不加电极：
Si_zp45_GDS= LayerStack(
        layers={
        "core":LayerLevel(
            layer=layer_core,
            thickness=thickness_full_etch,
            zmin=0,
            material="silicon",
            mesh_order=2,
            width_to_z=0.5,
            derived_layer=layer_core,
            info={
                "refractive_index": 1.4504,
                "uniformity_of_index": 0.0002,
                "uniformity_of_thickness": 0.3,
                "color": "blue",
                "simulation_settings": {
                    "wavelength": 1.55,  # 单位 um
                    "solver": "FDTD"
                }
        }
        ), 
    }
)

#打印层栈信息并保存：
#定义保存路径和文件名
output_file = fr"C:\Windows\System32\csufactory\csufactory\all_output_files\parameter\Si_zp45_LayerStack.txt"
#打开文件进行写入
with open(output_file, "w") as file:
    # 遍历层信息并将输出写入文件
    for layername, layer in Si_zp45_LayerStack.layers.items():
        file.write(
            f"LayerName: {layername}, "
            f"Thickness: {layer.thickness}, "
            f"Material: {layer.material}, "
            f"RefractiveIndex: {layer.info.get('refractive_index', 'none')}, "
            f"Zmin: {layer.zmin}, "
            f"DerivedLayer: {layer.derived_layer}\n"
        )
print(f"TXT文件已保存至: {output_file}")


#输出仅有awg的gds文件，并命名、保存：
z = gf.technology.layer_stack.get_component_with_derived_layers(c, Si_zp45_GDS)
component_name = "awg_1_1" 
#无时间戳：
output_gds_path = fr"C:\Windows\System32\csufactory\csufactory\all_output_files\gds\{component_name}.gds"
#有时间戳：
# timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
z.write_gds(output_gds_path)
print(f"GDS 文件已保存至: {output_gds_path}")
z.show()


#生成仅有awg的3d预览图：
# c = gf.c.awg(
#     inputs= 1,
#     arms= 9,                                      #阵列波导数量
#     outputs= 1,
#     free_propagation_region_input_function= partial(free_propagation_region, width1=2, width2=20.0),
#     free_propagation_region_output_function= partial(free_propagation_region, width1=2, width2=20.0),
#     fpr_spacing= 50.0,                            #输入/输出FPR的间距
#     arm_spacing= 1.0,                             #阵列波导间距
# )
# s =c.to_3d(layer_stack=Si_zp45_LayerStack)
# s.show()


##生成有每个层的3d预览图：
c == awg
s =c.to_3d(layer_stack=Si_zp45_LayerStack)
s.show()


#生成层栈的所有信息：
# x = Si_zp45_LayerStack.get_klayout_3d_script()
# print(x)