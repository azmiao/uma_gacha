
## 写在前面

### 【重要】插件移植自[@HibiKier](https://github.com/HibiKier)大佬的[nonebot插件](https://github.com/HibiKier/nonebot_plugin_gamedraw)

在原有基础上持续适配卡池，biliwiki的公告页面布局老是变2333，b站wiki的ui也有变化，导致得一直适配，部分wiki内容我也有在更改，图鉴缺少的内容我也补上了，新年祈愿一下后续稍微平稳一点hhhh（

插件后续将持续更新，其他马娘插件也在绝赞开发中（大概

### 本插件仅供研究学习使用

### 另外感谢三个多月来参与测试的大佬们

## 更新日志

22-02-01    v1.4    成功给aiocq的基础框架移植了一份，代码日渐完善（大概），准备正式开源

22-01-20    v1.3.2    一些适配更新（biliwiki的公告页面布局老是变2333

22-01-14    v1.3.1    重构部分代码，使之适配新的页面布局和其他什么什么的

22-01-06    v1.2    更改卡池信息文件，指令结果等

21-12-15    v1.1    修复部分异常，调整代码结构

21-11-23    v1.0    首次移植适配

## 使用前须知

卡池受限于biliwiki的公告更新速度，插件会在每天凌晨4点自动更新数据

## 项目地址：
https://github.com/azmiao/uma_gacha

## 功能
```
[查看马娘卡池] 看马娘当前的池子

[@bot马娘单抽] 马娘池子单抽
[@bot马娘十连] 马娘池子十连
[@bot马之井] 马娘池子抽一井

[@bot育成卡单抽] 育成卡池子单抽
[@bot育成卡十连] 育成卡池子十连
[@bot育成卡井] 育成卡池子抽一井
```
## 简单食用教程：

1. 下载或git clone本插件：

在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目
```
git clone https://github.com/azmiao/uma_gacha
```

2. 安装依赖，不一定全，请视自己日志然后补全：
```
pip install -r requirements.txt
```

3. 在 HoshinoBot\hoshino\config\ `__bot__.py` 文件的 MODULES_ON 加入 'uma_gacha'

然后重启 HoshinoBot即可，会自动检测文件和更新数据的，自动更新完方可使用，详情请看hoshino的日志，若有报错请看看是否有什么依赖没有装，如若依赖没有问题仍报错，请反馈bug