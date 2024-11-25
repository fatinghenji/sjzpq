import json
import os
import math
from attachments_config import ATTACHMENTS_PRESETS
from attachments_data import ATTACHMENTS_DATA, ATTACHMENT_DEPENDENCIES
import time

# 在类定义之前添加常量定义
WEAPON_TYPES = [
    '冲锋枪',
    '步枪',
    '霰弹枪',
    '精确射手步枪',
    '狙击步枪',
    '手枪'
]

SOLDIER_CLASSES = [
    '突击',
    '支援',
    '工程',
    '侦查'
]

class Attachment:
    # 定义配件类型
    TYPES = {
        'TOP_RAIL': '上导轨',
        'LEFT_RAIL': '左导轨',
        'RIGHT_RAIL': '右导轨',
        'BARREL': '枪管',
        'MUZZLE': '枪口',
        'FOREGRIP': '前握把',
        'MAGAZINE': '弹匣',
        'MAG_WELL': '弹匣座',
        'CANTED_SIGHT': '侧瞄具',
        'STOCK': '枪托',
        'PISTOL_GRIP': '后握把',
        'GRIP_MOUNT': '握把座'
    }

    def __init__(self, name, attachment_type, recoil_mod=0, handling_mod=0, 
                 stability_mod=0, hip_fire_mod=0, can_mount_grip=False):
        self.name = name
        if attachment_type not in self.TYPES.values():
            raise ValueError(f"无效的配件类型。可用类型: {', '.join(self.TYPES.values())}")
        self.attachment_type = attachment_type
        self.recoil_mod = recoil_mod
        self.handling_mod = handling_mod
        self.stability_mod = stability_mod
        self.hip_fire_mod = hip_fire_mod
        self.can_mount_grip = can_mount_grip

    def to_dict(self):
        return {
            'name': self.name,
            'attachment_type': self.attachment_type,
            'recoil_mod': self.recoil_mod,
            'handling_mod': self.handling_mod,
            'stability_mod': self.stability_mod,
            'hip_fire_mod': self.hip_fire_mod,
            'can_mount_grip': self.can_mount_grip
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Weapon:
    # 将常量作为类属性
    WEAPON_TYPES = WEAPON_TYPES
    SOLDIER_CLASSES = SOLDIER_CLASSES

    def __init__(self, name='', weapon_type='', soldier_classes=None, base_damage=0, 
                 stomach_damage=0, limb_damage=0, foot_damage=0, range_meters=0, 
                 fire_rate=0, recoil_control=0, handling_speed=0, ads_stability=0, 
                 hip_fire_accuracy=0):
        self.name = name
        self.weapon_type = weapon_type
        self.soldier_classes = soldier_classes if soldier_classes is not None else []
        self.base_damage = float(base_damage)
        self.stomach_damage = float(stomach_damage)
        self.limb_damage = float(limb_damage)
        self.foot_damage = float(foot_damage)
        self.range_meters = float(range_meters)
        self.fire_rate = float(fire_rate)
        self.recoil_control = float(recoil_control)
        self.handling_speed = float(handling_speed)
        self.ads_stability = float(ads_stability)
        self.hip_fire_accuracy = float(hip_fire_accuracy)
        self.attachments = []

    def to_dict(self):
        return {
            'name': self.name,
            'weapon_type': self.weapon_type,
            'soldier_classes': self.soldier_classes,
            'base_damage': self.base_damage,
            'stomach_damage': self.stomach_damage,
            'limb_damage': self.limb_damage,
            'foot_damage': self.foot_damage,
            'range_meters': self.range_meters,
            'fire_rate': self.fire_rate,
            'recoil_control': self.recoil_control,
            'handling_speed': self.handling_speed,
            'ads_stability': self.ads_stability,
            'hip_fire_accuracy': self.hip_fire_accuracy,
            'attachments': [att.to_dict() for att in self.attachments]
        }

    @classmethod
    def from_dict(cls, data):
        # 确保所有必要的字段都存在，如果不存在则使用默认值
        weapon_data = {
            'name': data.get('name', ''),
            'weapon_type': data.get('weapon_type', ''),
            'soldier_classes': data.get('soldier_classes', []),
            'base_damage': data.get('base_damage', 0),
            'stomach_damage': data.get('stomach_damage', 0),
            'limb_damage': data.get('limb_damage', 0),
            'foot_damage': data.get('foot_damage', 0),
            'range_meters': data.get('range_meters', 0),
            'fire_rate': data.get('fire_rate', 0),
            'recoil_control': data.get('recoil_control', 0),
            'handling_speed': data.get('handling_speed', 0),
            'ads_stability': data.get('ads_stability', 0),
            'hip_fire_accuracy': data.get('hip_fire_accuracy', 0)
        }
        
        weapon = cls(**weapon_data)
        
        # 加载配件数据
        attachments_data = data.get('attachments', [])
        weapon.attachments = [Attachment.from_dict(att) for att in attachments_data]
        
        return weapon

    def get_modified_stats(self):
        """计算包含配件加成后的属性值"""
        total_recoil = self.recoil_control
        total_handling = self.handling_speed
        total_stability = self.ads_stability
        total_hip_fire = self.hip_fire_accuracy

        for attachment in self.attachments:
            total_recoil = max(0, min(100, total_recoil + attachment.recoil_mod))
            total_handling = max(0, min(100, total_handling + attachment.handling_mod))
            total_stability = max(0, min(100, total_stability + attachment.stability_mod))
            total_hip_fire = max(0, min(100, total_hip_fire + attachment.hip_fire_mod))

        return {
            '后坐力控制': total_recoil,
            '操控速度': total_handling,
            '据枪稳定性': total_stability,
            '腰际射击精度': total_hip_fire
        }

    def add_attachment(self, attachment):
        # 检查是否已经安装了同类型的配件
        for att in self.attachments:
            if att.attachment_type == attachment.attachment_type:
                raise ValueError(f"已安装了{attachment.attachment_type}类型的配件")
        
        # 检查弹匣座的特殊限制
        if attachment.attachment_type == '弹匣座':
            for att in self.attachments:
                if att.attachment_type == '弹匣' and '弹鼓' in att.name:
                    raise ValueError("使用弹鼓类型弹匣时不能安装弹匣座")
        
        # 检查弹鼓的特殊限制
        if attachment.attachment_type == '弹匣' and '弹鼓' in attachment.name:
            for att in self.attachments:
                if att.attachment_type == '弹匣座':
                    raise ValueError("安装弹鼓类型弹匣时需要先移除弹匣座")
        
        # 检查握把座的特殊限制
        if attachment.attachment_type == '握把座':
            # 检查是否安装了可安装握把座的后握把
            has_compatible_grip = False
            for att in self.attachments:
                if att.attachment_type == '后握把' and att.can_mount_grip:
                    has_compatible_grip = True
                    break
            if not has_compatible_grip:
                raise ValueError("需要先安装可支持握把座的后握把")
        
        self.attachments.append(attachment)

    def remove_attachment(self, attachment_name):
        self.attachments = [att for att in self.attachments if att.name != attachment_name]

    def calculate_btk(self, health=100):
        btks = {
            '胸部': math.ceil(health / self.base_damage),
            '腹部': math.ceil(health / self.stomach_damage),
            '手部': math.ceil(health / self.limb_damage),
            '脚部': math.ceil(health / self.foot_damage)
        }
        return btks

    def display_info(self):
        print(f"\n枪��信息:")
        print(f"名称: {self.name}")
        print(f"枪械类型: {self.weapon_type}")
        print(f"适用兵种: {', '.join(self.soldier_classes)}")
        print(f"胸部基础伤害: {self.base_damage}")
        print(f"腹部伤害: {self.stomach_damage}")
        print(f"手部伤害: {self.limb_damage}")
        print(f"脚部伤害: {self.foot_damage}")
        print(f"射程: {self.range_meters}米")
        print(f"射速: {self.fire_rate}发/分钟")
        print(f"\n性能参数:")
        print(f"后坐力控制: {self.recoil_control}")
        print(f"操控速度: {self.handling_speed}")
        print(f"据枪稳定性: {self.ads_stability}")
        print(f"腰际射击精度: {self.hip_fire_accuracy}")
        
        modified_stats = self.get_modified_stats()
        print(f"\n当前性能参数 (包含配件加成):")
        print(f"后坐力控制: {modified_stats['后坐力控制']} (基础: {self.recoil_control})")
        print(f"操控速度: {modified_stats['操控速度']} (基础: {self.handling_speed})")
        print(f"据枪稳定性: {modified_stats['据枪稳定性']} (基础: {self.ads_stability})")
        print(f"腰际射击精度: {modified_stats['腰际射击精度']} (基础: {self.hip_fire_accuracy})")

        if self.attachments:
            print("\n已安装配件:")
            for att in self.attachments:
                print(f"\n- {att.name}:")
                if att.recoil_mod: print(f"  后坐力修改: {att.recoil_mod:+}")
                if att.handling_mod: print(f"  操控速度修改: {att.handling_mod:+}")
                if att.stability_mod: print(f"  据枪稳定性修改: {att.stability_mod:+}")
                if att.hip_fire_mod: print(f"  腰际射击精度修改: {att.hip_fire_mod:+}")

        # BTK信息显示保持不变
        print("\nBTK（击杀所需子弹数）:")
        btks = self.calculate_btk()
        for part, btk in btks.items():
            print(f"{part}: {btk}发")
        
        fastest_btk = min(btks.values())
        kill_time_ms = (fastest_btk - 1) * (60000 / self.fire_rate)
        print(f"\n最快理论击杀时间: {kill_time_ms:.1f}毫秒")

def input_weapon_data():
    print("\n请输入枪械数:")
    name = input("枪械名称: ")
    weapon_type = input("枪械类型: ")
    soldier_classes = input("适用兵种 (用逗号分隔): ").split(',')
    base_damage = float(input("基础伤害（胸部）: "))
    stomach_damage = float(input("部位伤害（腹部）: "))
    limb_damage = float(input("部位伤害（手部）: "))
    foot_damage = float(input("部位伤害（脚部）: "))
    range_meters = float(input("射程（米）: "))
    fire_rate = int(input("射速（发/分钟）: "))
    
    print("\n请输入性能参数 (1-100的数值):")
    recoil_control = float(input("后坐力控制: "))
    handling_speed = float(input("操控速度: "))
    ads_stability = float(input("据枪稳定性: "))
    hip_fire_accuracy = float(input("腰际射击精度: "))
    
    return Weapon(name, weapon_type, soldier_classes, base_damage, stomach_damage, 
                 limb_damage, foot_damage, range_meters, fire_rate, recoil_control,
                 handling_speed, ads_stability, hip_fire_accuracy)

def input_attachment_data():
    """输入配件数据"""
    print("\n请输入配件数据:")
    
    # 1. 选择配件类型
    print("\n可用的配件类型:")
    for i, (_, type_name) in enumerate(Attachment.TYPES.items(), 1):
        print(f"{i}. {type_name}")
    
    while True:
        try:
            type_idx = int(input("\n选择配件类型 (输入序号): ")) - 1
            if 0 <= type_idx < len(Attachment.TYPES):
                attachment_type = list(Attachment.TYPES.values())[type_idx]
                break
            else:
                print("无效的序号，请重试")
        except ValueError:
            print("请输入有效的数字")
    
    # 2. 输入配件名称
    name = input("\n配件名称: ")
    
    # 3. 确定是否为特定武器配件
    is_specific = input("\n是否是特定武器的专用配件？(y/n): ").lower() == 'y'
    
    if is_specific:
        weapon_name = input("\n请输入适用的武器名称: ")
    
    # 4. 检查是否需要前置配件
    if attachment_type in ATTACHMENT_DEPENDENCIES:
        dep = ATTACHMENT_DEPENDENCIES[attachment_type]
        if '前置配件' in dep:
            print(f"\n注意：{attachment_type}需要先安装{dep['前置配件']}")
            print(f"且{dep['前置配件']}必须支持安装{attachment_type}")
    
    # 5. 输入属性修改值
    print("\n请输入属性修改值 (+/- 数值):")
    recoil_mod = float(input("后坐力控制修改值: "))
    handling_mod = float(input("操控速度修改值: "))
    stability_mod = float(input("据枪稳定性修改值: "))
    hip_fire_mod = float(input("腰际射击精度修改值: "))
    
    # 6. 特殊属性
    special_attributes = {}
    if attachment_type == '后握把':
        special_attributes['can_mount_grip'] = input("\n是否可以安装握把座？(y/n): ").lower() == 'y'
    elif attachment_type == '弹匣':
        special_attributes['is_drum_mag'] = '弹鼓' in name
    
    # 创建配件数据
    attachment_data = {
        'name': name,
        'type': attachment_type,
        'recoil_mod': recoil_mod,
        'handling_mod': handling_mod,
        'stability_mod': stability_mod,
        'hip_fire_mod': hip_fire_mod,
        **special_attributes
    }
    
    # 保存配件数据
    if is_specific:
        if weapon_name not in ATTACHMENTS_DATA['specific']:
            ATTACHMENTS_DATA['specific'][weapon_name] = {}
        if attachment_type not in ATTACHMENTS_DATA['specific'][weapon_name]:
            ATTACHMENTS_DATA['specific'][weapon_name][attachment_type] = []
        ATTACHMENTS_DATA['specific'][weapon_name][attachment_type].append(attachment_data)
    else:
        if attachment_type not in ATTACHMENTS_DATA['common']:
            ATTACHMENTS_DATA['common'][attachment_type] = []
        ATTACHMENTS_DATA['common'][attachment_type].append(attachment_data)
    
    # 保存到文件
    save_attachments_data()
    
    return Attachment(**attachment_data)

def save_attachments_data(filename='attachments_data.json'):
    """保存配件数据到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ATTACHMENTS_DATA, f, ensure_ascii=False, indent=4)

def load_attachments_data(filename='attachments_data.json'):
    """从文件加载配件数据"""
    global ATTACHMENTS_DATA
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                ATTACHMENTS_DATA = json.load(f)
    except Exception as e:
        print(f"\n警告：加载配件数据时出错: {e}")

def get_available_attachments(weapon_name, attachment_type):
    """获取可用的配件列表"""
    available = []
    
    # 添加通用配件
    if attachment_type in ATTACHMENTS_DATA['common']:
        available.extend(ATTACHMENTS_DATA['common'][attachment_type])
    
    # 添加特定武器配件
    if weapon_name in ATTACHMENTS_DATA['specific']:
        if attachment_type in ATTACHMENTS_DATA['specific'][weapon_name]:
            available.extend(ATTACHMENTS_DATA['specific'][weapon_name][attachment_type])
    
    return available

def save_weapon(weapon, directory='weapons'):
    """保存单个武器数据到独立文件"""
    try:
        # 确保目录存在
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # 生成文件名（使用枪械名称，移除特殊字符）
        filename = ''.join(c for c in weapon.name if c.isalnum() or c in (' ', '-', '_'))
        if not filename:  # 如果名称��空，使用时间戳
            filename = f"weapon_{int(time.time())}"
        filepath = os.path.join(directory, f"{filename}.json")
        
        # 准备要保存的数据
        weapon_data = {
            'name': weapon.name,
            'weapon_type': weapon.weapon_type,
            'soldier_classes': weapon.soldier_classes,
            'base_damage': weapon.base_damage,
            'stomach_damage': weapon.stomach_damage,
            'limb_damage': weapon.limb_damage,
            'foot_damage': weapon.foot_damage,
            'range_meters': weapon.range_meters,
            'fire_rate': weapon.fire_rate,
            'recoil_control': weapon.recoil_control,
            'handling_speed': weapon.handling_speed,
            'ads_stability': weapon.ads_stability,
            'hip_fire_accuracy': weapon.hip_fire_accuracy,
            'attachments': [att.to_dict() for att in weapon.attachments]
        }
        
        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(weapon_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存武器数据时出错: {e}")
        return False

def load_weapons(directory='weapons'):
    """从目录加载所有武器数据"""
    weapons = []
    
    # 如果目录不存在，创建它
    if not os.path.exists(directory):
        os.makedirs(directory)
        return weapons
    
    # 遍历目录中的所有json文件
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据中包含所有必要的字段
                    weapon_data = {
                        'name': data.get('name', ''),
                        'weapon_type': data.get('weapon_type', ''),
                        'soldier_classes': data.get('soldier_classes', []),
                        'base_damage': data.get('base_damage', 0),
                        'stomach_damage': data.get('stomach_damage', 0),
                        'limb_damage': data.get('limb_damage', 0),
                        'foot_damage': data.get('foot_damage', 0),
                        'range_meters': data.get('range_meters', 0),
                        'fire_rate': data.get('fire_rate', 0),
                        'recoil_control': data.get('recoil_control', 0),
                        'handling_speed': data.get('handling_speed', 0),
                        'ads_stability': data.get('ads_stability', 0),
                        'hip_fire_accuracy': data.get('hip_fire_accuracy', 0)
                    }
                    
                    weapon = Weapon(**weapon_data)
                    
                    # 加载配件数据
                    attachments_data = data.get('attachments', [])
                    weapon.attachments = [Attachment.from_dict(att) for att in attachments_data]
                    
                    weapons.append(weapon)
            except json.JSONDecodeError:
                print(f"\n警告：文件 {filename} 已损坏，已跳过")
            except Exception as e:
                print(f"\n警告：加载文件 {filename} 时出错: {e}")
    
    return weapons

def delete_weapon(weapon_name, directory='weapons'):
    """删除定武器的数据文件"""
    filename = ''.join(c for c in weapon_name if c.isalnum() or c in (' ', '-', '_'))
    filepath = os.path.join(directory, f"{filename}.json")
    
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"\n已删除 {weapon_name} 的数据文件")
        return True
    return False

def display_available_slots(weapon):
    """显示武器可用的配件槽位"""
    used_slots = {att.attachment_type for att in weapon.attachments}
    print("\n可用配件槽位:")
    for type_name in Attachment.TYPES.values():
        if type_name not in used_slots:
            # 检查特殊限制
            if type_name == '弹匣座':
                has_drum = any('弹鼓' in att.name for att in weapon.attachments 
                             if att.attachment_type == '弹匣')
                if not has_drum:
                    print(f"- {type_name}")
            elif type_name == '握把座':
                # 检查是否有可安装握把座的后握把
                has_compatible_grip = any(att.can_mount_grip for att in weapon.attachments 
                                       if att.attachment_type == '后握把')
                if has_compatible_grip:
                    print(f"- {type_name}")
            else:
                print(f"- {type_name}")

def save_attachments_presets(filename='attachments_presets.json'):
    """保存配件预设到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ATTACHMENTS_PRESETS, f, ensure_ascii=False, indent=4)

def load_attachments_presets(filename='attachments_presets.json'):
    """从文件加载配件预设"""
    global ATTACHMENTS_PRESETS
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                ATTACHMENTS_PRESETS = json.load(f)
    except Exception as e:
        print(f"\n警告：加载配件预设时出错: {e}")

# 主程序
if __name__ == "__main__":
    load_attachments_data()
    weapons = load_weapons()
    while True:
        print("\n1. 添加新枪械")
        print("2. 显示所有枪械")
        print("3. 计算特定生命值的BTK")
        print("4. 管理枪械配件")
        print("5. 删除枪械")
        print("6. 管理配件预设")  # 新选项
        print("7. 退出")
        
        choice = input("\n请选择操作 (1-7): ")
        
        if choice == "1":
            weapon = input_weapon_data()
            weapons.append(weapon)
            save_weapon(weapon)  # 保存单个武器数据
            print("\n枪械添加成功！")
        
        elif choice == "2":
            if not weapons:
                print("\n当前没有枪械数据！")
            else:
                for weapon in weapons:
                    weapon.display_info()
        
        elif choice == "3":
            if not weapons:
                print("\n当前没有枪械数据！")
                continue
                
            try:
                health = float(input("\n请输入目标生命值: "))
                print("\n计算结果:")
                for weapon in weapons:
                    print(f"\n{weapon.name}的BTK:")
                    btks = weapon.calculate_btk(health)
                    for part, btk in btks.items():
                        print(f"{part}: {btk}发")
                    kill_time_ms = (min(btks.values()) - 1) * (60000 / weapon.fire_rate)
                    print(f"最快理论击杀时间: {kill_time_ms:.1f}毫秒")
            except ValueError:
                print("\n请输入有效的生值！")
        
        elif choice == "4":
            if not weapons:
                print("\n当前没有枪械数据！")
                continue
                
            print("\n可用枪械:")
            for i, weapon in enumerate(weapons, 1):
                print(f"{i}. {weapon.name}")
            
            try:
                weapon_idx = int(input("\n选择要管理配件的枪械 (输入序号): ")) - 1
                weapon = weapons[weapon_idx]
                
                while True:
                    print("\n配件管理:")
                    print("1. 添加配件")
                    print("2. 移除配件")
                    print("3. 显示当前配件")
                    print("4. 返回主菜单")
                    
                    sub_choice = input("\n请选择操作 (1-4): ")
                    
                    if sub_choice == "1":
                        try:
                            print("\n当前件状态:")
                            display_available_slots(weapon)
                            
                            # 选择配件类型
                            print("\n可用的配件类型:")
                            for i, (_, type_name) in enumerate(Attachment.TYPES.items(), 1):
                                print(f"{i}. {type_name}")
                            
                            type_idx = int(input("\n选择配件类型 (输入序号): ")) - 1
                            attachment_type = list(Attachment.TYPES.values())[type_idx]
                            
                            # 获取可用配件
                            available_attachments = get_available_attachments(weapon.name, attachment_type)
                            
                            if available_attachments:
                                print(f"\n可用的{attachment_type}配件:")
                                for i, att in enumerate(available_attachments, 1):
                                    print(f"\n{i}. {att['name']}")
                                    print(f"   后坐力修改: {att['recoil_mod']:+}")
                                    print(f"   操控速度修改: {att['handling_mod']:+}")
                                    print(f"   据枪稳定性修改: {att['stability_mod']:+}")
                                    print(f"   腰际射击精度修改: {att['hip_fire_mod']:+}")
                                
                                print(f"{len(available_attachments) + 1}. 添加新配件")
                                
                                choice = int(input("\n请选择配件 (输入序号): "))
                                if 1 <= choice <= len(available_attachments):
                                    attachment = Attachment(**available_attachments[choice - 1])
                                else:
                                    attachment = input_attachment_data()
                            else:
                                print("\n当前没有可用的预设配件，请添加新配件")
                                attachment = input_attachment_data()
                            
                            weapon.add_attachment(attachment)
                            save_weapon(weapon)
                            print("\n配件添加成功！")
                        except ValueError as e:
                            print(f"\n错误: {e}")
                    
                    elif sub_choice == "2":
                        if not weapon.attachments:
                            print("\n当前没有已安装的配件！")
                            continue
                        
                        print("\n已安装的配件:")
                        for i, att in enumerate(weapon.attachments, 1):
                            print(f"{i}. {att.name}")
                        
                        att_idx = int(input("\n选择要移除的配件 (输入序号): ")) - 1
                        att_name = weapon.attachments[att_idx].name
                        weapon.remove_attachment(att_name)
                        save_weapon(weapon)  # 保存更新后的武器数据
                        print("\n配件移除成功！")
                    
                    elif sub_choice == "3":
                        weapon.display_info()
                    
                    elif sub_choice == "4":
                        break
                    
                    else:
                        print("\n无效选择，请重试")
                        
            except (ValueError, IndexError):
                print("\n无效输入！")
                
        elif choice == "5":  # 新增删除枪械选项
            if not weapons:
                print("\n当前没有枪械数据！")
                continue
            
            print("\n可用枪械:")
            for i, weapon in enumerate(weapons, 1):
                print(f"{i}. {weapon.name}")
            
            try:
                weapon_idx = int(input("\n选择要删除的枪械 (输入序号): ")) - 1
                weapon = weapons[weapon_idx]
                confirm = input(f"\n确定要删除 {weapon.name}？(y/n): ").lower()
                
                if confirm == 'y':
                    if delete_weapon(weapon.name):
                        weapons.pop(weapon_idx)
                        print(f"\n已删除 {weapon.name}")
                    else:
                        print("\n删除失败")
            except (ValueError, IndexError):
                print("\n无效输入！")
        
        elif choice == "6":
            print("\n配件预设管理:")
            print("1. 添加新配件预设")
            print("2. 显示所有配件预设")
            print("3. 返回主菜单")
            
            sub_choice = input("\n请选择操作 (1-3): ")
            
            if sub_choice == "1":
                # 显示可用的配件类型
                print("\n可用的配件类型:")
                for i, (_, type_name) in enumerate(Attachment.TYPES.items(), 1):
                    print(f"{i}. {type_name}")
                
                try:
                    type_idx = int(input("\n选择配件类型 (输入序号): ")) - 1
                    if 0 <= type_idx < len(Attachment.TYPES):
                        attachment_type = list(Attachment.TYPES.values())[type_idx]
                        
                        # 输入新配件预设数据
                        preset = {
                            'name': input("\n配件名称: "),
                            'recoil_mod': float(input("后坐力控制修改值: ")),
                            'handling_mod': float(input("操控速度修改值: ")),
                            'stability_mod': float(input("据枪稳定性修改值: ")),
                            'hip_fire_mod': float(input("腰际射击精度修改值: "))
                        }
                        
                        # 如果是后握把，询问是否可以安装握把座
                        if attachment_type == '后握把':
                            preset['can_mount_grip'] = input("\n是否可以安装握把座？(y/n): ").lower() == 'y'
                        
                        # 将新预设添加到配置中
                        if attachment_type not in ATTACHMENTS_PRESETS:
                            ATTACHMENTS_PRESETS[attachment_type] = []
                        ATTACHMENTS_PRESETS[attachment_type].append(preset)
                        
                        # 保存更新后的预设
                        save_attachments_presets()
                        print("\n配件预设添加成功！")
                    else:
                        print("\n无效的类型序号")
                except ValueError:
                    print("\n请输入有效的数值")
            
            elif sub_choice == "2":
                print("\n当前所有配件预设:")
                for type_name, presets in ATTACHMENTS_PRESETS.items():
                    print(f"\n{type_name}:")
                    for preset in presets:
                        print(f"\n  - {preset['name']}")
                        print(f"    后坐力修改: {preset['recoil_mod']:+}")
                        print(f"    操控速度修改: {preset['handling_mod']:+}")
                        print(f"    据枪稳定性修改: {preset['stability_mod']:+}")
                        print(f"    腰际射击精度修改: {preset['hip_fire_mod']:+}")
                        if 'can_mount_grip' in preset:
                            print(f"    可安装握把座: {'是' if preset['can_mount_grip'] else '否'}")
        
        elif choice == "7":
            print("\n程序已退出")
            break
        
        else:
            print("\n无效选择，请重试") 