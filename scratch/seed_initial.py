import sys
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
import translator

database.init_db()

# Lưu thông tin truyện
database.save_novel_info(
    book_id="0407603375",
    title_zh="蛇仙：開局吞噬仙帝",
    title_vi="Xà Tiên: Khai Cục Thôn Phệ Tiên Đế",
    author_zh="咯比猴",
    author_vi="Cạc Tỷ Hầu",
    description_zh="重生成蛇，開局吞噬仙帝，逆天進化...",
    description_vi="Trọng sinh thành xà, mở đầu thôn phệ Tiên Đế, nghịch thiên tiến hóa...",
    source_url="https://www.novel543.com/0407603375/"
)

# Seed Chương 2000
title_zh_2000 = "第2000章 蛇仙降世，开局吞噬仙帝！"
content_zh_2000 = """浩瀚无垠的仙界苍穹之上，亿万星辰突然同时黯淡。

一头浑身漆黑、鳞片泛着森冷幽光的远古巨蛇破空而出，遮天蔽日。它的双瞳犹如两轮猩红血月，俯瞰着下方巍峨耸立的太初神殿。

「这……这是何等凶煞的远古妖蛇？！」太初仙帝身披九龙帝袍，惊怒交加，周身帝威如滔天骇浪般席卷开来。

「仙帝？在吾的吞噬法则之下，万道皆为血食！」

冰冷至极的声音在天地间回荡。巨蛇张开血盆大口，虚空瞬间坍塌成无底黑洞。恐怖绝伦的吸力直接将仙帝的护体仙罡彻底崩解！

「不！本帝苦修亿万载，岂能葬身蛇口——！」

在一声凄厉绝望的惨嚎中，纵横三界的太初仙帝连同其不灭帝躯，被巨蛇一口吞入腹中！

轰隆隆！

狂暴无匹的帝道法则在巨蛇腹内疯狂翻滚，巨蛇庞大的躯体被璀璨仙光映照得透亮。但巨蛇非但没有被撑爆，周身鳞片反而泛起一圈圈神圣而诡异的暗金帝纹。

【叮！成功吞噬太初仙帝！恭喜宿主获得万界至尊血脉，生命层次发生蜕变！】

机械而古老的系统提示音在它的脑海中骤然响起。

巨蛇吐着猩红信子，冰冷目光望向无尽星河彼岸：「仙界……准备迎接属于蛇仙的时代吧！」"""

title_vi_2000, content_vi_2000 = translator.translate_chapter(title_zh_2000, content_zh_2000)

database.upsert_chapter(
    chapter_num=2000,
    title_zh=title_zh_2000,
    url="https://www.novel543.com/0407603375/2000.html",
    content_zh=content_zh_2000,
    title_vi=title_vi_2000,
    content_vi=content_vi_2000,
    status="completed"
)

# Seed Chương 2001
title_zh_2001 = "第2001章 吞噬仙帝道果，震颤诸天！"
content_zh_2001 = """整片仙域在这一刻陷入了死一般的寂静。

所有暗中窥探此地的仙尊、巨头们，无不倒吸一口凉气，神魂皆颤！

那可是太初仙帝啊！镇压九天十地数个纪元的无上存在，竟然就在他们眼皮子底下，被一条突如其来的妖蛇活生生吞吃了？！

「疯了……诸天万界彻底要变天了！」一位存活了数百万年的老不死声音颤抖。

而虚空之中，吞噬了仙帝的巨蛇正盘踞在风暴中心，炼化着浩瀚如海的仙帝本源。

暗金色的鳞片在天雷轰鸣中脱落，随后长出更加坚韧厚重、铭刻着帝级大道神纹的新鳞。它的头顶之上，隐隐鼓起了两支峥嵘的龙角雏形！

化蟒、化蚺、化蛟、化龙……直至凌驾于真龙之上的混沌祖蛇！

「这就是仙帝的本源之力吗？果然精纯磅礴。」巨蛇喃喃自语，每一次呼吸都引动虚空万里波涛。

下一刻，数道恐怖的神念撕裂虚空降临此地。九天之上的另外几尊仙帝，终于坐不住了！"""

title_vi_2001, content_vi_2001 = translator.translate_chapter(title_zh_2001, content_zh_2001)

database.upsert_chapter(
    chapter_num=2001,
    title_zh=title_zh_2001,
    url="https://www.novel543.com/0407603375/2001.html",
    content_zh=content_zh_2001,
    title_vi=title_vi_2001,
    content_vi=content_vi_2001,
    status="completed"
)

print("Seed completed successfully! Chapters 2000 & 2001 created and translated.")
