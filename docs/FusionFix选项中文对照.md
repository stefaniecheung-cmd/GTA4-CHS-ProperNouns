# FusionFix 选项中文对照表

对应文件：`plugins\GTAIV.EFLC.FusionFix.ini`（手动调参）与 `plugins\GTAIV.EFLC.FusionFix.cfg`（游戏内菜单改动后的存档，会覆盖 ini 同名项）。

说明分两类：
- **菜单项**：游戏内 FusionFix 菜单里会出现，玩家能直接改。
- **仅 ini**：只能在 ini 文件里改，游戏菜单不显示。

> 游戏内菜单中文化需要额外补丁（旧补丁 `GTA4.CHS.asi` + `custom_translations.json` 就是干这个的）。本表用于让手动改 ini 的人看懂每一项。

## MAIN

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `RecoilFix` | 后坐力修复 | 键鼠游玩时，让后坐力表现与手柄一致 | 菜单项 |
| `AimingZoomFix` | 瞄准缩放修复 | -1：TBoGT 瞄准缩放同 IV 与 TLaD；0：关闭；1：TBoGT 用 Xbox 版表现；2：IV 与 TLaD 也启用 | 菜单项 |

## CAMERASENSITIVITY

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `MouseLookSensitivityRange` | 鼠标视角灵敏度范围 | 鼠标视角灵敏度滑条的最小/最大值 | 仅 ini |
| `GamepadLookSensitivityRange` | 手柄视角灵敏度范围 | 手柄视角灵敏度滑条的区间 | 仅 ini |
| `MouseAimSensitivityRange` | 鼠标瞄准灵敏度范围 | 鼠标瞄准灵敏度滑条的区间 | 仅 ini |
| `GamepadAimSensitivityRange` | 手柄瞄准灵敏度范围 | 手柄瞄准灵敏度滑条的区间 | 仅 ini |

## SHADOWS

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `ExtraDynamicShadows` | 额外动态阴影 | 补回缺失阴影：1=部分植被；2=栅栏、格栅、道路、墙体及部分植被 | 仅 ini |
| `CascadeBlendSize` | 级联阴影混合范围 | 级联阴影过渡区大小，取值 0.0–1.0 | 仅 ini |
| `HighResolutionShadows` | 高分辨率阴影 | 级联阴影贴图分辨率翻倍，非常吃显卡 | 仅 ini |
| `ForceShadowFilter` | 强制阴影过滤 | 0=模糊质量跟随画质定义；1=始终低质量；2=始终高质量 | 仅 ini |

## FRAMELIMIT

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `FrameLimitType` | 锁帧模式 | 1=实时（线程锁）；2=精确（sleep-yield），更省资源 | 仅 ini |
| `FpsLimit` | 帧率上限 | 当菜单里帧率上限选「自定义」时使用（负数表示以刷新率为基数） | 仅 ini |
| `CutsceneFpsLimit` | 过场动画帧率上限 | 过场动画的独立帧率上限 | 仅 ini |
| `LoadingFpsLimit` | 载入帧率上限 | 避免某些任务载入时卡死（如 Off Route） | 仅 ini |
| `UnlockFramerateDuringLoadscreens` | 载入时不锁帧 | 载入画面解除锁帧，加载更快 | 仅 ini |
| `MinigamesFpsLimit` | 小游戏帧率上限 | 避免 `MinigamesList` 里的小游戏出问题 | 仅 ini |
| `MinigamesList` | 小游戏列表 | 受上述帧率上限约束的小游戏清单 | 仅 ini |

## MISC

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `DefaultCameraAngleInTLaD` | TLAD 默认镜头角度 | 在 TLaD 骑车时沿用 IV 的默认镜头角度 | 仅 ini |
| `PedDeathAnimFixFromTBoGT` | 路人死亡动作修复 | 去掉 IV/TLaD 反击路人后多出的死亡动作，与 TBoGT 一致 | 仅 ini |
| `DisableCameraCenteringInCover` | 禁用掩体准心回中 | 禁用贴墙移动时强制回正镜头 | 仅 ini |
| `ExtraInfo` | 附加信息 | 暂停菜单显示额外信息（如已加载的 img 数量） | 仅 ini |
| `OverrideTreeAlpha` | 树木透明度覆盖 | PC/PS3/X360 分别约 0.625 / 2.5 / 4.0 | 仅 ini |
| `ConsoleCarReflectionsAndDirt` | 主机版车漆反射与污渍 | 用主机强度的车漆反射，且车辆生成时可带污渍 | 仅 ini |
| `BrakeLightsWhenStopped` | 停车亮刹车灯 | 静止时点亮刹车灯，与 AI 车辆一致（原版仅行走速度以上才亮） | 仅 ini |
| `FixHelicopterSearchlights` | 修复直升机探照灯 | 0=关闭；1=同时只有一束（最长 10 秒）；2=全部独立绘制 | 仅 ini |
| `AlwaysDisplayHealthOnReticle` | 准心显示敌人血量 | 键鼠游玩时在准心上显示 NPC 血量 | 仅 ini |
| `SmoothShorelines` | 平滑海岸线 | 柔化水陆交界并调整泡沫噪声 | 仅 ini |
| `SmoothLightVolumes` | 平滑光体积 | 柔化光体积边缘 | 仅 ini |
| `NoBloomColorShift` | 关闭泛光色偏 | 避免开启色调映射后泛光阈值造成剧烈偏色 | 仅 ini |
| `MenuEnteringDelay` | 菜单进入延迟 | 400=默认；0=无延迟 | 仅 ini |
| `MenuExitingDelay` | 菜单退出延迟 | 800=默认；0=无延迟 | 仅 ini |
| `MenuAccessDelayOnStartup` | 启动菜单延迟 | 3000=默认；0=无延迟 | 仅 ini |
| `RadarZoomDelay` | 雷达缩放延迟 | 0=默认；3000=延迟 3 秒 | 仅 ini |
| `DeathMusic` | 死亡音乐 | IV 中玩家死亡时播放被删减的死亡音乐 | 仅 ini |
| `AutoClimbLaddersRange` | 自动爬梯触发距离 | 距离多近可自动攀爬（单位同游戏，手动按键为 4.0） | 仅 ini |
| `PlayerJumpRagdollControl` | 跳跃布娃娃控制 | 跳跃时按换弹键可主动触发布娃娃，类似 GTA V | 仅 ini |
| `PlayerClimbRagdollControl` | 攀爬布娃娃控制 | 攀爬时同样可主动触发布娃娃 | 仅 ini |

## FOG

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `VolFogFarClip` | 体积雾远距裁剪 | 覆盖体积雾的远裁剪距离 | 仅 ini |
| `ExtendedTimecycEditing` | 扩展 timecyc 编辑 | 0=关闭；1=显示调试信息并按 F3 重载 .dat | 仅 ini |

## BudgetedIV

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `VehicleBudget` | 载具预算 | 避免「出租车 Bug」，可能引起载具音效问题 | 仅 ini |
| `PedBudget` | 路人预算 | 调整可能引发问题 | 仅 ini |
| `ExtendedLimits` | 扩展上限 | 提高 modelinfo、handling、carcols 及部分池的上限 | 仅 ini |

## EPISODICCONTENT

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `EpisodicVehicles` | 资料片载具 | IV/TLaD 支持 APC、Buzzard、走私船、浮空器、Blade 及其能力 | 仅 ini |
| `EpisodicWeapons` | 资料片武器 | 支持 DSR1、榴弹发射器、管状炸弹、粘弹、AA12 爆弹、P90 载具检查、降落伞等 | 仅 ini |
| `ExplosiveAnnihilator` | 歼灭者爆炸弹 | 让 IV 中歼灭者直升机使用爆炸弹（需先开资料片武器） | 仅 ini |
| `OtherEpisodicChecks` | 其他资料片检查 | 支持迪斯科镜头摇摆、手机切换、高度表、降落伞、爆炸狙击与拳头秘籍（需相应资料片文件） | 仅 ini |
| `TBoGTHelicopterHeightLimit` | TBoGT 直升机高度限制 | 将 IV/TLaD 直升机高度上限提高到 TBoGT 水平 | 仅 ini |
| `TBoGTPoliceWeapons` | TBoGT 警用武器 | IV/TLaD 中给 SWAT 与 FIB 配 P90/AA12，给直升机内警察配 M249（需先开资料片武器） | 仅 ini |
| `RemoveSCOSignatureCheck` | 移除 SCO 签名检查 | 允许在所有资料片使用任意 SCO 脚本 | 仅 ini |
| `EpisodicDeathMusic` | 资料片死亡音乐 | 让恢复的死亡音乐在所有资料片播放（需按资料片分别放置自定义音效） | 仅 ini |

## SUNSHAFTS

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `SunShaftsDensity` | 太阳光束密度 | 光束长度，0.0–1.0 | 仅 ini |
| `SunShaftsDecay` | 太阳光束衰减 | 光束由中心向外的衰减速度，0.0–1.0 | 仅 ini |

## POSTFX

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `EnablePreAlphaDepth` | 启用预透明深度 | 让景深、太阳光束等深度后处理能正确透过窗户/透明物渲染 | 仅 ini |
| `AmbientOcclusionBlurPasses` | 环境光遮蔽模糊次数 | 模糊迭代次数 | 仅 ini |
| `AmbientOcclusionSamples` | 环境光遮蔽采样数 | 每像素采样数 | 仅 ini |
| `AmbientOcclusionLogMaxOffset` | 环境光遮蔽对数最大偏移 | 偏移量上限的对数控制 | 仅 ini |
| `AmbientOcclusionMaxMipLevel` | 环境光遮蔽最大 Mip 层级 | 参与计算的最高 Mip 层 | 仅 ini |
| `AmbientOcclusionFarClip` | 环境光遮蔽远距裁剪 | 计算的最大距离 | 仅 ini |
| `AmbientOcclusionRadius` | 环境光遮蔽半径 | 采样球半径 | 仅 ini |
| `AmbientOcclusionBias` | 环境光遮蔽偏移 | 深度偏移，用于抑制自遮蔽 | 仅 ini |
| `AmbientOcclusionIntensity` | 环境光遮蔽强度 | 遮蔽强度 | 仅 ini |
| `AmbientOcclusionBlurRadius` | 环境光遮蔽模糊半径 | 模糊半径 | 仅 ini |

## SHADOWFILTERSHARP / SHADOWFILTERSOFT / SHADOWFILTERCHSS

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `ShadowSoftness` | 阴影柔和度 | 控制阴影模糊程度 | 仅 ini |
| `ShadowBias` | 阴影偏移 | 控制阴影偏置，需配合柔和度调整 | 仅 ini |
| `MaxSoftness` | 最大柔和度 | CHSS/PCSS 模式下的最大模糊 | 仅 ini |

（三节分别为 CE 风格、1.0.4.0 风格、CHSS/PCSS 风格，同名键取值不同。）

## PROJECT2DFX

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `CoronaRadiusMultiplier` | 光晕半径倍率 | 光晕半径的倍数 | 仅 ini |
| `CoronaAlphaMultiplier` | 光晕透明度倍率 | 光晕透明度的倍数 | 仅 ini |
| `SlightlyIncreaseRadiusWithDistance` | 光晕随距离微增 | 随距离轻微增大光晕半径 | 仅 ini |
| `DisableDefaultLodLights` | 禁用默认远景灯光 | 关闭默认的远景灯点 | 仅 ini |

## TURNINDICATORS

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `ManualTurnIndicators` | 手动转向灯 | 开启手动转向灯，手柄按 LB/RB 触发 | 仅 ini |
| `LeftIndicatorKey` | 左转向灯键 | `0xDB` = VK_OEM_4（左花括号键） | 仅 ini |
| `RightIndicatorKey` | 右转向灯键 | `0xDD` = VK_OEM_6（右花括号键） | 仅 ini |

## EXPERIMENTAL

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `DisplayMemoryStats` | 显示内存统计 | 帧率计数器旁额外打印流式内存与进程内存占用 | 仅 ini |
| `ReflectionMSAAQuality` | 反射 MSAA 质量 | 对反射贴图（室外、室内、水面、镜面）应用 MSAA，如 Xbox 360；有效值 2/4/8 | 仅 ini |

## LANGUAGEOVERRIDE

| 键 | 中文 | 说明 | 类型 |
|---|---|---|---|
| `Language` | 语言 | 游戏文本语言覆盖（不是菜单界面语言）。`0` 为不覆盖 | 菜单项 |

> 注意：此项控制的是**游戏内文本（gxt）语言**，与 FusionFix 菜单自身显示语言无关。我们的 `zchs.gxt` 重定向走的是文件名替换，与此项无冲突。

## 游戏内菜单可见项（旧补丁翻译表覆盖）

以下 86 项是旧补丁 `custom_translations.json` 收录的菜单可见项（含各级取值），已录入 `data\ff_menu_zh.tsv`：

跳过开场、跳过主菜单、无边框窗口、帧率上限、泛光、主机伽马、画面滤镜、窗口化、画质定义、阴影过滤、树木光照、景深、动态模糊、RGB 灯效同步、树木透明度、太阳光束、显示帧率、始终奔跑、备用对白、掩体准心回中、键鼠镜头回中延迟、手柄镜头回中延迟、视野、原始输入、按键提示、上下黑边、左右黑边、抗锯齿、检查更新、失焦暂停、透明地图菜单、扩展狙击操作、限时事件、体积雾、色调映射、缩放移动、解除光照限制、远景灯光、载具居中镜头、步行居中镜头、镜头抖动、过场音频同步、转向灯、额外夜间阴影、图形接口、始终显示弹道、主机自动曝光、键鼠车内回中延迟、手柄车内回中延迟、键鼠车内转向速度、手柄车内转向速度、手柄视角灵敏度、手柄瞄准灵敏度、鼠标瞄准灵敏度、关闭换装转场、立即刹停出租车、环境光遮蔽、自动爬梯、特技跳跃镜头、动作镜头、视野距离、关闭、锐利、柔和、CHSS、仅过场动画、低、中、高、极高、电脑版、电脑版+、主机版、Xbox 360、Xbox One、PlayStation 3、PlayStation 4、PlayStation 5、Nintendo Switch、Steam Deck、Steam 手柄、FXAA、SMAA、默认、自定义。
