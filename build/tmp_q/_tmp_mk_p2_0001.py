# -*- coding: utf-8 -*-
import io
rows = [
("TBoGT","MAIN","62F4C1EF","好哥们儿！秃鹰直升机就停在 West River，你随时想用就用。我的就是你的，兄弟！走起！ - Yu$uf","原文是 it's on the West River（在西河/停在西河畔），原译「在西河的停机坪」加了中国语境没有的设施"),
("TBoGT","MAIN","A59683CA","我的床还是那么冰冷。你不必道歉。斗牛士本来就该有很多情妇。只是别忘了我们曾有的干柴烈火。 亲亲","mistresses 是「情妇」，原译「女主人」把情妇误读成女主人"),
("TBoGT","MAIN","22333FFC","~s~由于乘坐了出租车，任务成绩将无法保留，也无法上传至 Rockstar Social Club。完成夜生活之曲的全部主线任务后，再用手机里的任务重玩功能打一遍，才能得到有效成绩。","get usable results 是「拿到有效成绩」，原译「刷分吧」把功能目的改成刷分"),
("TBoGT","MAIN","1A05AFDC","~s~由于使用了续关，任务成绩将无法保留，也无法上传至 Rockstar Social Club。完成夜生活之曲的全部主线任务后，再用手机里的任务重玩功能打一遍，才能得到有效成绩。","同上：usable results 是「有效成绩」，原译「刷分吧」曲解"),
("TBoGT","MAIN","49914354","用~PAD_LSTICK_ALL~在空中移动。~n~按~INPUT_SPRINT~打开降落伞。~n~按住~INPUT_NEXT_CAMERA~切换视角。~n~按~INPUT_DUCK~释放烟雾。","activate smoke 是「释放烟雾」，原译「放烟」把动作缩成两个字看不明白"),
("TBoGT","MAIN","B53E03EB","用~PAD_LSTICK_ALL~在空中移动。~n~按~INPUT_SPRINT~打开降落伞。~n~按住~INPUT_MELEE_ATTACK1~切换视角。~n~按~INPUT_DUCK~释放烟雾。","activate smoke 是「释放烟雾」，原译「放烟」过于口语且不明"),
("TBoGT","MAIN","8554CA44","用~PAD_LSTICK_ALL~控制身体重心。~n~按~PAD_LT~或~PAD_RT~做左右的空中刹车。~n~按~INPUT_ENTER~抛弃降落伞。~n~按住~INPUT_MELEE_ATTACK1~查看不同视角。","air brakes 是「空中刹车（减速）」，原译「急转」把减速操作译成转向"),
("TBoGT","MAIN","E8032E81","用~PAD_LSTICK_ALL~控制身体重心。~n~按~PAD_LB~或~PAD_RB~做左右的空中刹车。~n~按~INPUT_ENTER~脱离降落伞。~n~按住~INPUT_MELEE_ATTACK1~查看不同视角。","air brakes 是「空中刹车」，原译「急转」错误"),
("TBoGT","MAIN","6AC25A30","用~PAD_LSTICK_ALL~控制身体重心。~n~按~INPUT_MOUSE_LMB~或~INPUT_MOUSE_RMB~做左右的空中刹车。~n~按~INPUT_ENTER~抛弃降落伞。~n~按住~INPUT_NEXT_CAMERA~查看不同视角。","air brakes 是「空中刹车」，原译「急转」错误"),
("TBoGT","MAIN","416E3A2D","用~PAD_LSTICK_ALL~控制身体重心。~n~按~INPUT_MOUSE_LMB~或~INPUT_MOUSE_RMB~做左右的空中刹车。~n~按~INPUT_ENTER~脱离降落伞。~n~按住~INPUT_NEXT_CAMERA~查看不同视角。","air brakes 是「空中刹车」，原译「急转」错误"),
("TBoGT","MAIN","9FDA468B","咱们再来一次吧，强尼。我可能会习惯拿棍子甩你脸上的。哈哈哈。","Let's do that again 是「再来一次（刚才那场）」，原译「以后再来赛车啊」把当场提议译成日后邀约"),
("TLAD","MAIN","4EE5A123","兄弟，你怎么不打电话来？前女友走就走，我无所谓，但兄弟不能散。","I can take my bitch of an ex walking out 是「前女友走就走」，原译「把娘们扔在一旁」把被动说成主动抛弃"),
("TLAD","MAIN","B2316B39","胯下一台车，手上一根棍，真是太爽了。要是打太重了，抱歉啊，约翰。","Sorry if I hit you too hard 是「打太重的话抱歉」，原译「没给你放水不好意思」把道歉的理由换成放水"),
("TLAD","MAIN","598E39F0","这场比赛你可能没赢，但你拿棍子把谁都能惹毛。干得好，老兄。回头打给我。","upset anyone with your bat 是「用棍子把谁都能惹毛」，原译「把所有人都打得没脾气」把 upset 译成打服"),
("TLAD","MAIN","F139154D","你可以带吉姆去小地图上标记的任何地点，或者去其他活动的地点。","or to the location of other activities 是「或去其他活动的地点」，原译「未标注的其他活动」把地点说成未标注"),
("TLAD","MAIN","AA0DB5E3","你可以带特里去小地图上标记的任何地点，或者去其他活动的地点。","同上"),
("TLAD","MAIN","1BD2E790","你可以带克莱去小地图上标记的任何地点，或者去其他活动的地点。","同上"),
("TLAD","MAIN","C211E549","强尼，听说你的 Hexer 被弄坏了，给我打个电话，我修好给你送过来。","Hexer 是车型专名，按口径保留英文，原译「迷魅光轮」为自造名"),
("TLAD","MAIN","E508D623","吉姆已在 The Lost 会所为你留了一把全自动 9mm 手枪，配~1~发子弹。","The Lost 是帮派专名，按口径保留英文，原译「失落帮」意译"),
("TLAD","MAIN","B6CC48F4","小地图上方显示的信息，表明你的 Lost 帮成员经过战斗磨砺到什么程度；程度由名字旁边的色条表示。","how fight hardened your Lost gang members are 是「战斗磨砺程度」，原译「此次作战对你战友的强化程度」把主动磨砺译成被动强化"),
("TLAD","MAIN","A1643EC9","干得漂亮。想听你那台窃听器，就打 123-555-0160。 - TS III","原文 Call ... if you want to tune into that listening device of yours 是条件句，原译把它压成「如果你要听」的短句且缺标点"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p2_0001.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
