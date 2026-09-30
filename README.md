# 万紫千红 · 行旅手册

双击 `index.html` 即可离线使用，不需要安装依赖。也可运行 `node server.cjs`，然后访问 http://127.0.0.1:4175。

## 已收录

- 送礼攻略：63 位人物，61 位有明确的“非常喜欢 / 喜欢”记录；2 位仍待确认。
- 商店攻略：46 个地点（30 个据点或准据点、7 个地图商会地点、9 个旅行商人观测地点），616 条商品记录；535 条有来源数量，81 条库存待确认。旅行商人数量为截图时剩余库存。
- 道具店、武器店、市场、旺达尔商会分别展示；帝都额外保留礼物店，旅行商人单独标注观测地点。
- 送礼总览：按人物头像与姓名、非常喜欢、喜欢三列展示全部人物，可搜索人物或礼物并跳转详情。
- 按中日名称、英文人物名查询；点击礼物可查看已收录销售地点。
- 151 个参考页面，包含中文、英文和日文资料。

**最新合并日期为 2026-10-01（各来源采集日期分别保留）。资料并非全部章节与隐藏货品的穷尽清单；尚未查到的内容明确留空，不以 0 或无限代替。** 页面及数据均没有声称已在游戏内逐项实测。

## 文件

- `index.html`：页面入口。
- `style.css`、`app.js`：样式和交互。
- `aliases.js`：人物、地点、礼物、商品及兑换材料的别名提示。
- `data/gifts.json`：人物及非常喜欢、喜欢的礼物清单。
- `data/shops.json`：地点、店铺、商品、价格、库存、兑换材料。
- `data/sources.json`：参考页面和来源说明。
- `data/portraits.json`：人物头像与原始图片来源的对应表。
- `assets/portraits/`：本地人物头像，离线可用。
- `data.js`：从人物、商店、来源及别名 JSON 生成的离线副本，支持直接双击 HTML。
- `translations.json`：未覆盖物品与地名的补充中文暂译。
- `data/name-aliases.json`：用户确认的人物、地点、物品标准名及旧译名，优先于网上资料和暂译。
- `normalize_names.py`：按别名表转换导入数据，并同步离线页面。
- `sync-data.cjs`：编辑 JSON 后更新离线副本。
- `validation.json`：页面和数据验证结果。
- `data/imports/fwsite-*.json`：新来源的礼物与商店记录快照，保留原始中文译名和导入日期。
- `data/fwsite-mapping.json`：人物、礼物、商店商品及材料的名称对齐证据。
- `data/fwsite-merge-report.json`：首次合并数量统计。
- `merge_fwsite.py`：按物品身份取并集，保留来源差异并优先应用用户修正。

## 更新数据

JSON 是维护数据的主文件。修改 `data` 目录中的 JSON 后，在此目录运行：

```text
node sync-data.cjs
```

HTTP 预览会直接读取 JSON；直接打开 HTML 时使用同步生成的 `data.js`。

## 分享搜索与筛选结果

搜索与筛选条件会自动写入 URL 查询参数，复制地址即可保留当前状态。打开链接、刷新和浏览器前进后退都会恢复这些条件；输入时更新当前历史记录，切换栏目时保留前一个栏目，避免每输入一个字都增加一条历史记录。清空搜索或选择“全部”会移除对应参数。

| 参数 | 保存内容 |
| --- | --- |
| `giftSearch` / `preference` | 送礼攻略搜索词 / 偏好筛选 |
| `overviewSearch` | 送礼总览搜索词 |
| `shopSearch` / `placeKind` | 地图商店搜索词 / 地点类型筛选 |
| `character` / `place` / `shop` | 当前人物、地点和店铺类型 |

栏目仍由 `#gifts`、`#overview`、`#shops`、`#sources` 指定，例如 `?shopSearch=手斧&placeKind=据点#shops`。各栏目的条件分别保存，未使用的默认值省略，无效筛选值回退到默认值。本地文件和 HTTP 页面均支持；发送给其他人时应使用部署后网站的地址。

运行 `node verify-url.cjs` 可验证分享链接、刷新恢复、历史导航、栏目跳转和特殊字符处理（需 Playwright 及 Edge）。

## 字段约定

人物 `loves` 表示来源列出的非常喜欢，`likes` 表示来源列出的喜欢。数组为空表示尚未获得明确记录，不能理解为角色没有喜好。每项保留 `sourceIds`，人物的 `sourceDifference` 保存中文旧稿独有项目以便核对。GameWith 网页中的类别提示只展开其明确列举的物品，不凭类别推测更多礼物。

商店 `type`：`items` 道具店、`weapons` 武器店、`market` 市场、`vandhal` 旺达尔商会、`gifts` 礼物店、`travel` 旅行商人。

- `stockStatus: known`：`stock` 为来源明确列出的数量。
- `stockStatus: unlimited`：来源明确写无限，`stock` 留 `null`。
- `stockStatus: unknown`：来源未给出数量，`stock` 留 `null`。
- `exchange[].quantity`：一次兑换需要的材料数，与商品库存无关。
- `phase: null`：来源没有逐项注明章节，不能解释为全章节通用。
- `status: not_listed`：参考资料没有列出此类店铺，不是确认该店不存在。
- `alternativePrices`：其他来源的报价；无法确认是折扣、阶段还是来源误差，未强行合并。
- `quantitySourceId` / `priceSourceId`：补充字段的直接来源。

## 资料方法与局限

送礼主要依据 [GameWith 人物偏好](https://gamewith.jp/fefw/577115)，中文名称和旧记录对照 [游民星空全角色礼物攻略](https://www.gamersky.com/handbook/202609/2217606.shtml)。游民星空引用 GameWith，二者不算两次独立实测。剩余未知人物为救世主、塔霍妮娅。杰斯塔非常喜欢“鱼酱”的记录由用户补充，日文原名「ガルム」已通过中日礼物清单对齐。

商店优先采用 [AppMedia 地图攻略](https://appmedia.jp/fe_banshisenkou/80369863) 链接到的地点专页。使用 [Game8 据点商店总表](https://game8.jp/fe-banshisenko/818736) 及单品详情补充，并对照 [Gamecap 商店资料](https://gamecap.jp/fe_fw/shop.html)。卡利亚内拉港的 AppMedia 市场标题重复写成道具店，经 Game8 和 Gamecap 对照后归入市场；该市场的库存列本身为空。

英文检索包括 [KeenGamer 送礼指南](https://www.keengamer.com/articles/guides/fire-emblem-fortunes-weave-best-gifts-guide/) 和 [Raider King 旺达尔商会](https://raiderking.com/fe-fortunes-weave-vandhal-trading-co-all-trader-locations-items-exchange-and-resources/)。英文推荐类别没有自动当成已确认的喜好等级；英文兑换表另存于 `englishExchangeObservations`，并在相关商会显示对照。英日成本不同时均保留来源。

首都部分商品、卡利亚内拉港市场及少量其他商品仍无可确认库存。各章节、名声、路线、复兴状态可能影响货品与价格；来源没有给出这些条件时，不补造统一条件。

中文人物及部分礼物采用中文攻略译名，其他地名与物品名是本手册暂译，可能与官方中文文本不同。日文原名用于精确查证。

## 验证

已验证 JSON 结构、唯一标识、来源引用、库存类型、代表性原始条目，以及浏览器中的人物搜索、礼物跳转商店、空结果、库存展示、英文资料展开、手机布局和本地文件离线打开。浏览器未发现运行错误。

页面无远程字体、远程脚本或必需联网图片。仅点击资料链接时前往外部站点。

## GitHub Pages

在线地址：https://lpegasus.github.io/fe-fortune-s-weave/

仓库：https://github.com/LPegasus/fe-fortune-s-weave

这是无需服务器或构建依赖的静态网站。`main` 保存维护版本，GitHub Pages 从 `gh-pages` 分支的根目录发布。`.nojekyll` 让 GitHub 直接提供原始静态文件。

更新资料后，同步离线数据并提交，再更新发布分支：

```sh
node sync-data.cjs
git add .
git commit -m "Update guide"
git push origin main main:gh-pages
```

名称修正保存在 `data/name-aliases.json`，礼物偏好修正保存在 `data/gift-corrections.json` 中。页面资源均采用相对路径，兼容 GitHub Pages 项目路径和离线打开。

## 同步资料时的名称转换

`data/name-aliases.json` 是用户确认名称的统一维护位置，保存用户确认的名称、跨站译名对照及物品名称替换规则。`canonicalName` 是页面使用的名称；`aliases` 保存旧译名，`nameJa` 和已有的 `nameEn` 用于识别网上的原文名称。人物、地点和物品分别匹配，避免把人物更名应用到书名等物品中。

`build_data.py` 在采集数据生成阶段自动读取该表，输出前统一处理人物、礼物、商店商品、兑换材料和头像说明。它保留原文名称、来源、喜好等级和库存。`translations.json` 继续提供其他暂译；与别名表冲突时，以别名表为准。

从其他渠道导入或手动合并 JSON 后，运行：

```sh
python normalize_names.py
```

这会转换当前 JSON，并同步 `data.js`，无需重新抓取资料。只需新增或修改 JSON 别名记录，无需再修改人物名称转换代码。礼物偏好补充仍独立保存在 `data/gift-corrections.json`；别名转换不会更改喜好等级。

有其他名称的词条带虚线下划线。悬停或键盘聚焦会显示别名浮层，列表去重并排除当前显示名；按 Escape 或点击外部关闭。手机轻点名称查看，位于人物链接或礼物按钮内的名称再次轻点执行原操作。浮层位于页面顶层，不受表格滚动区域裁切。HTTP 和离线模式均读取同一份别名数据。`node verify-aliases.cjs` 验证这些交互。


## 2026-10-01 中文站资料合并

合并 [万缕千丝中文攻略站](https://fire-emblem-fw.site/misc.html) 的送礼和商店资料。57 位人物的 751 条喜好观察中，673 条为本地新增等级记录；共 113 个人物—礼物组合存在来源等级分歧。按并集保留两栏，并在详情和总览标注“来源分歧”。卡塔妮娅的手环等用户确认记录优先，不被网上资料覆盖。类别推测仅存为来源备注，不扩展成具体礼物。

90 个来源礼物名按 [Game8 日文清单](https://game8.jp/fe-banshisenko/816847) 与既有名称对齐；人物使用共同头像编号与日文姓名交叉核对。136 个商店商品和材料名结合日文用途、获取地点、出售地点与兑换配方对齐，证据链接逐项记录。新旅行商人地点尚未核对日文名称时保留中文原文，不编造原名。

合入 141 条商店观察，包括 99 条商人截图商品与 42 条帝都兑换方案；新增 50 条商品记录。截图时期为赛奥朵拉篇第 10 章、游戏内 1449 年 9 月 12 日。截图剩余库存不覆盖旧来源库存。相同商品的不同材料组合全部保留，可展开“中文站记录”对照；旅行商人会随机移动。

- 礼物 `sourceObservations` 保存来源原名、来源等级、页面链接及采集日期。`preferenceConflict` 标识两栏分歧；`preferenceConflicts` 记录用户修正覆盖来源的情况。
- 商店商品 `sourceObservations` 保存完整的库存、价格、兑换材料和章节上下文；多条记录代表不同方案或快照，不累计库存。`stockMeaning: observed_remaining` 明确表示截图剩余量。
- 数据构建会自动重放导入快照。单独重放可运行 `python merge_fwsite.py` 后运行 `node sync-data.cjs`。重复导入不会添加重复观察。
- 验证：`python -m unittest test_name_aliases.py test_fwsite_merge.py`；浏览器验证 `node verify.cjs` 与 `node verify-import.cjs`（需安装 Playwright 及 Edge）。
