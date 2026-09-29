# 万紫千红 · 行旅手册

双击 `index.html` 即可离线使用，不需要安装依赖。也可运行 `node server.cjs`，然后访问 http://127.0.0.1:4175。

## 已收录

- 送礼攻略：63 位人物，60 位有明确的“非常喜欢 / 喜欢”记录；3 位仍待确认。
- 商店攻略：37 个地点（30 个据点或准据点、7 个地图商会地点），566 条商品记录；489 条有明确库存，77 条库存待确认。
- 道具店、武器店、市场、旺达尔商会分别展示；帝都额外保留礼物店。
- 按中日名称、英文人物名查询；点击礼物可查看已收录销售地点。
- 144 个参考页面，包含中文、英文和日文资料。

**资料快照为 2026-09-29。资料并非全部章节与隐藏货品的穷尽清单；尚未查到的内容明确留空，不以 0 或无限代替。** 页面及数据均没有声称已在游戏内逐项实测。

## 文件

- `index.html`：页面入口。
- `style.css`、`app.js`：样式和交互。
- `data/gifts.json`：人物及非常喜欢、喜欢的礼物清单。
- `data/shops.json`：地点、店铺、商品、价格、库存、兑换材料。
- `data/sources.json`：参考页面和来源说明。
- `data/portraits.json`：人物头像与原始图片来源的对应表。
- `assets/portraits/`：本地人物头像，离线可用。
- `data.js`：从三个 JSON 生成的离线副本，支持直接双击 HTML。
- `translations.json`：补充中文暂译。源文中的人名、道具名始终保留。
- `sync-data.cjs`：编辑 JSON 后更新离线副本。
- `validation.json`：页面和数据验证结果。

## 更新数据

JSON 是维护数据的主文件。修改 `data` 目录中的 JSON 后，在此目录运行：

```text
node sync-data.cjs
```

HTTP 预览会直接读取 JSON；直接打开 HTML 时使用同步生成的 `data.js`。

## 字段约定

人物 `loves` 表示来源列出的非常喜欢，`likes` 表示来源列出的喜欢。数组为空表示尚未获得明确记录，不能理解为角色没有喜好。每项保留 `sourceIds`，人物的 `sourceDifference` 保存中文旧稿独有项目以便核对。GameWith 网页中的类别提示只展开其明确列举的物品，不凭类别推测更多礼物。

商店 `type`：`items` 道具店、`weapons` 武器店、`market` 市场、`vandhal` 旺达尔商会、`gifts` 礼物店。

- `stockStatus: known`：`stock` 为来源明确列出的数量。
- `stockStatus: unlimited`：来源明确写无限，`stock` 留 `null`。
- `stockStatus: unknown`：来源未给出数量，`stock` 留 `null`。
- `exchange[].quantity`：一次兑换需要的材料数，与商品库存无关。
- `phase: null`：来源没有逐项注明章节，不能解释为全章节通用。
- `status: not_listed`：参考资料没有列出此类店铺，不是确认该店不存在。
- `alternativePrices`：其他来源的报价；无法确认是折扣、阶段还是来源误差，未强行合并。
- `quantitySourceId` / `priceSourceId`：补充字段的直接来源。

## 资料方法与局限

送礼主要依据 [GameWith 人物偏好](https://gamewith.jp/fefw/577115)，中文名称和旧记录对照 [游民星空全角色礼物攻略](https://www.gamersky.com/handbook/202609/2217606.shtml)。游民星空引用 GameWith，二者不算两次独立实测。剩余未知人物为救世主、杰斯特、塔霍妮娅。

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

人物名称与实测礼物修正保留在生成规则及 `data/gift-corrections.json` 中。页面资源均采用相对路径，兼容 GitHub Pages 项目路径和离线打开。
