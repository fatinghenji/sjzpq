# 配件数据存储结构
ATTACHMENTS_DATA = {
    'common': {    # 通用配件
        # 示例结构：
        # '上导轨': [
        #     {
        #         'name': '全息瞄具',
        #         'type': '上导轨',
        #         'recoil_mod': 0,
        #         'handling_mod': -5,
        #         'stability_mod': 10,
        #         'hip_fire_mod': 0
        #     }
        # ]
    },
    'specific': {  # 特定武器配件
        # 示例结构：
        # 'AK47': {
        #     '上导轨': [
        #         {
        #             'name': 'AK专用瞄具',
        #             'type': '上导轨',
        #             'recoil_mod': 0,
        #             'handling_mod': -3,
        #             'stability_mod': 8,
        #             'hip_fire_mod': 0
        #         }
        #     ]
        # }
    }
}

# 配件依赖关系
ATTACHMENT_DEPENDENCIES = {
    '握把座': {'前置配件': '后握把', '条件': 'can_mount_grip'},
    '弹匣座': {'互斥配件': '弹匣', '条件': 'is_drum_mag'}
} 