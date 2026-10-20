<template>
  <div class="space-y-6">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-2 bg-slate-800 rounded-xl border border-slate-700">
      <h2 class="text-lg font-bold text-white">初一上册数学 · 知识点因果链</h2>
      <div class="flex items-center gap-3">
        <button
          @click="resetView"
          class="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white text-sm rounded transition"
        >
          重置视图
        </button>
        <span class="text-xs text-slate-400">点击节点 → 展开下游 · 悬停 → 看因果链</span>
      </div>
    </div>

    <!-- 桑基图展示区 -->
    <div class="bg-slate-900 rounded-xl p-2 relative overflow-hidden min-h-[700px] min-w-[600px]">
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-slate-900/80 z-10">
        <div class="text-gray-400 text-sm">正在生成因果链...</div>
      </div>

      <!-- SVG 画布 -->
      <svg ref="svgRef" class="w-full h-full" style="background:transparent"></svg>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="absolute inset-0 flex items-center justify-center bg-red-950/95 z-20 p-4 overflow-auto">
        <pre class="text-red-400 text-xs whitespace-pre-wrap break-all font-mono max-h-full">{{ errorMessage }}</pre>
      </div>
    </div>

    <!-- 知识点详情面板 -->
    <div v-if="selectedNode" class="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-lg">
      <!-- 标题行 -->
      <div class="flex justify-between items-start mb-3">
        <div>
          <h3 class="text-xl font-bold text-amber-400">{{ selectedNode.name }}</h3>
          <p class="text-sm text-slate-400 mt-1">{{ selectedNode.description }}</p>
        </div>
        <button @click="selectedNode = null" class="text-slate-400 hover:text-white transition">✕</button>
      </div>

      <!-- 标签 -->
      <div class="flex flex-wrap gap-2 mb-4">
        <span v-for="tag in selectedNode.tags || []" :key="tag"
              class="px-2 py-1 bg-slate-700 text-xs rounded border border-slate-600">
          {{ tag }}
        </span>
      </div>

      <!-- 大白话解释 -->
      <div v-if="selectedNode.plainBlocks || selectedNode.plainText" class="mb-4">
        <div class="text-xs font-semibold text-sky-400 mb-1">💬 大白话讲</div>
        <div class="bg-slate-900/50 rounded-lg p-3 border border-slate-700 text-sm text-slate-200 leading-relaxed space-y-3">
          <!-- 新格式：blocks 数组 -->
          <template v-if="selectedNode.plainBlocks">
            <div v-for="(block, i) in selectedNode.plainBlocks" :key="i">
              <!-- 小节标题 -->
              <div v-if="block.type === 'heading'" class="text-sky-300 font-bold text-sm mt-2 mb-1">
                {{ block.text }}
              </div>
              <!-- 普通段落 -->
              <p v-else-if="block.type === 'text'" class="whitespace-pre-wrap">{{ block.content }}</p>
              <!-- 提示/强调框 -->
              <div v-else-if="block.type === 'callout'"
                   :class="[
                     'rounded-md px-3 py-2 border-l-4',
                     block.variant === 'warn' ? 'bg-amber-900/30 border-amber-500 text-amber-200' :
                     block.variant === 'tip'  ? 'bg-emerald-900/30 border-emerald-500 text-emerald-200' :
                                                'bg-sky-900/30 border-sky-500 text-sky-200'
                   ]">
                {{ block.text }}
              </div>
              <!-- 表格 -->
              <table v-else-if="block.type === 'table'" class="w-full text-xs border-collapse">
                <thead>
                  <tr>
                    <th v-for="h in block.headers" :key="h"
                        class="bg-slate-700/60 border border-slate-600 px-2 py-1 text-slate-100 font-semibold">
                      {{ h }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, ri) in block.rows" :key="ri"
                      :class="ri % 2 === 0 ? 'bg-slate-800/40' : 'bg-slate-800/10'">
                    <td v-for="(cell, ci) in row" :key="ci"
                        class="border border-slate-600 px-2 py-1 align-top">
                      <span :class="{ 'text-emerald-300': typeof cell === 'string' && cell.startsWith('✓'), 'text-rose-300': typeof cell === 'string' && cell.startsWith('✗') }">{{ cell }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <!-- 列表 -->
              <template v-else-if="block.type === 'list'">
                <ol v-if="block.ordered" class="list-decimal list-inside space-y-1 text-slate-300">
                  <li v-for="(item, ii) in block.items" :key="ii">{{ item }}</li>
                </ol>
                <ul v-else class="list-disc list-inside space-y-1 text-slate-300">
                  <li v-for="(item, ii) in block.items" :key="ii">{{ item }}</li>
                </ul>
              </template>
              <!-- 树状结构 -->
              <div v-else-if="block.type === 'tree'" class="font-mono text-xs text-slate-300 whitespace-pre leading-relaxed">
{{ block.lines.join('\n') }}
              </div>
            </div>
          </template>
          <!-- 旧格式兼容：纯文本 -->
          <p v-else class="whitespace-pre-wrap">{{ selectedNode.plainText }}</p>
        </div>
      </div>

      <!-- 生活类比 -->
      <div v-if="selectedNode.analogy" class="mb-4">
        <div class="text-xs font-semibold text-emerald-400 mb-1">🌍 生活中类比</div>
        <p class="text-sm text-slate-200 leading-relaxed bg-emerald-900/20 rounded-lg p-3 border border-emerald-800/50 whitespace-pre-wrap">
          {{ selectedNode.analogy }}
        </p>
      </div>

      <!-- 公式展示 -->
      <div v-if="selectedNode.formulaBlocks || selectedNode.formula" class="mb-4">
        <div class="text-xs font-semibold text-violet-400 mb-1">📐 公式 & 例子</div>
        <div class="bg-violet-950/40 rounded-lg p-3 border border-violet-800/50 text-amber-200 text-sm space-y-2">
          <template v-if="selectedNode.formulaBlocks">
            <pre v-for="(fb, fi) in selectedNode.formulaBlocks" :key="fi"
                 :class="fb.type === 'table' ? '' : 'font-mono whitespace-pre-wrap leading-relaxed'">
              <table v-if="fb.type === 'table'" class="w-full text-xs border-collapse">
                <thead>
                  <tr>
                    <th v-for="h in fb.headers" :key="h" class="bg-violet-900/50 border border-violet-700 px-2 py-1 font-semibold text-amber-100">{{ h }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, ri) in fb.rows" :key="ri" :class="ri % 2 === 0 ? 'bg-violet-900/20' : 'bg-violet-900/10'">
                    <td v-for="(cell, ci) in row" :key="ci" class="border border-violet-700 px-2 py-1 font-mono">{{ cell }}</td>
                  </tr>
                </tbody>
              </table>
            </pre>
          </template>
          <pre v-else class="font-mono whitespace-pre-wrap leading-relaxed">{{ selectedNode.formula }}</pre>
        </div>
      </div>

      <!-- 下游提示 -->
      <div v-if="selectedNode.children && selectedNode.children.length" class="text-sm text-slate-500">
        有 {{ selectedNode.children.length }} 个下游知识点 → 点击节点展开
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import { sankey, sankeyLinkHorizontal } from 'd3-sankey'

const svgRef = ref(null)
const loading = ref(false)
const loaded = ref(false)
const selectedNode = ref(null)
const errorMessage = ref('')

// ========== 知识点因果链数据 ==========
// 结构：每个节点有 children（学习它之后才能学的知识点）
// 层级从左到右 = 从因到果 / 从先学到后学
const knowledgeGraph = {
  id: 'root',
  name: '初一上册数学',
  description: '北师大版七年级上册 · 全部知识点因果依赖图',
  tags: ['全册', '起点'],
  children: [
    // ===== 第一章：有理数 =====
    {
      id: 'ch1-1',
      name: '有理数的概念',
      description: '正有理数、负有理数和零统称为有理数 —— 一切运算的基础',
      tags: ['基础', '概念', '第一章'],
      children: [
        {
          id: 'ch1-2',
          name: '数轴表示法',
          description: '用一条有方向的直线来表示数，原点、正方向、单位长度三要素',
          tags: ['基础', '工具', '第一章'],
          children: [
            {
              id: 'ch1-3',
              name: '相反数与绝对值',
              description: '只相异于符号的两个数互为相反数；数轴上到原点的距离叫绝对值',
              tags: ['性质', '第一章'],
              children: [
                {
                  id: 'ch1-4',
                  name: '有理数的加减法',
                  description: '运用符号法则进行加减运算，减法即加上相反数',
                  tags: ['运算', '第一章'],
                  children: [
                    {
                      id: 'ch1-5',
                      name: '有理数的乘除法',
                      description: '同号得正异号得负，绝对值相乘除；除法即乘以倒数',
                      tags: ['运算', '第一章'],
                      children: [
                        {
                          id: 'ch1-rp',
                          name: '倒数',
                          description: '乘积为1的两个数互为倒数；除以一个数等于乘以它的倒数',
                          tags: ['概念', '第一章'],
                          children: [
                            {
                              id: 'ch1-6',
                              name: '乘方与科学记数法',
                              description: '相同因数的积的简便写法；用于表示很大或很小的数',
                              tags: ['运算', '应用', '第一章'],
                              children: [
                                // ↓ 跨章因果：有理数运算 → 整式运算的基础
                                { id: 'ch2-4', name: '整式的加减运算', _cross: true },
                                { id: 'ch2-5', name: '整式的乘法', _cross: true },
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },

    // ===== 第二章：整式的加减 =====
    {
      id: 'ch2-1',
      name: '用字母表示数',
      description: '用字母来表示数和数量关系，这是代数的起点',
      tags: ['基础', '概念', '第二章'],
      children: [
        {
          id: 'ch2-2',
          name: '单项式与多项式',
          description: '不加加减号的字母式叫单项式；几个单项式相加叫多项式',
          tags: ['概念', '分类', '第二章'],
          children: [
            {
              id: 'ch2-3',
              name: '同类项与合并同类项',
              description: '字母和指数都相同的项叫同类项，合并时系数相加',
              tags: ['运算', '技巧', '第二章'],
              children: [
                {
                  id: 'ch2-4',
                  name: '整式的加减运算',
                  description: '去括号、合并同类项、按降幂排列',
                  tags: ['运算', '第二章'],
                  children: [
                    {
                      id: 'ch2-5',
                      name: '整式的乘法',
                      description: '单项式乘单项式、单项式乘多项式、多项式乘多项式',
                      tags: ['运算', '第二章'],
                      children: [
                        // ↓ 跨章因果：整式乘法 → 方程求解的基础
                        { id: 'ch3-3', name: '一元一次方程求解', _cross: true },
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },

    // ===== 第三章：一元一次方程 =====
    {
      id: 'ch3-1',
      name: '方程的概念',
      description: '含有未知数的等式叫方程 —— 建模思想的起点',
      tags: ['概念', '第三章'],
      children: [
        {
          id: 'ch3-2',
          name: '等式的性质',
          description: '等式两边同时加、减、乘、除同一个数（除数不为0），等式仍成立',
          tags: ['性质', '工具', '第三章'],
          children: [
            {
              id: 'ch3-3',
              name: '一元一次方程求解',
              description: '去分母 → 去括号 → 移项 → 合并同类项 → 系数化为1',
              tags: ['方法', '技巧', '第三章'],
              children: [
                {
                  id: 'ch3-4',
                  name: '列方程解应用题',
                  description: '审题 → 设未知数 → 找等量关系 → 列方程 → 求解 → 检验',
                  tags: ['应用', '综合', '第三章'],
                  children: []
                }
              ]
            }
          ]
        }
      ]
    },

    // ===== 第四章：几何图形初步 =====
    {
      id: 'ch4-1',
      name: '图形的运动',
      description: '平移、旋转和对称叫做图形的运动 —— 几何变换入门',
      tags: ['概念', '变换', '第四章'],
      children: [
        {
          id: 'ch4-2',
          name: '线段、射线、直线',
          description: '线段有两个端点可度量；射线一个端点；直线无端点无限延伸',
          tags: ['基础', '图形', '第四章'],
          children: [
            {
              id: 'ch4-3',
              name: '角的概念与度量',
              description: '由两条有公共端点的射线组成；度分秒为基本单位',
              tags: ['基础', '图形', '第四章'],
              children: [
                {
                  id: 'ch4-4',
                  name: '角的比较与运算',
                  description: '叠合法比较大小；角的平分线把角分成两个相等的角',
                  tags: ['运算', '第四章'],
                  children: [
                    {
                      id: 'ch4-5',
                      name: '平行线的判定与性质',
                      description: '同位角相等/内错角相等/同旁内角互补 → 两直线平行',
                      tags: ['性质', '图形', '第四章'],
                      children: [
                        {
                          id: 'ch4-6',
                          name: '垂线与点到线的距离',
                          description: '互相垂直的两条直线；垂线段长度即点到线的距离',
                          tags: ['性质', '图形', '第四章'],
                          children: []
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },

    // ===== 第五章：数据收集与描述 =====
    {
      id: 'ch5-1',
      name: '统计调查的步骤',
      description: '提出问题 → 设计调查 → 收集数据 → 整理数据 → 描述数据 → 分析结论',
      tags: ['方法', '流程', '第五章'],
      children: [
        {
          id: 'ch5-2',
          name: '统计图的种类',
          description: '条形图看数量多少、折线图看变化趋势、扇形图看比例分布',
          tags: ['工具', '表示', '第五章'],
          children: [
            {
              id: 'ch5-3',
              name: '平均数与加权平均数',
              description: '所有数之和除以个数；加权平均数考虑不同数据的权重',
              tags: ['概念', '计算', '第五章'],
              children: [
                {
                  id: 'ch5-4',
                  name: '方差与离散程度',
                  description: '方差反映一组数据相对于平均值的波动大小',
                  tags: ['概念', '分析', '第五章'],
                  children: []
                }
              ]
            }
          ]
        }
      ]
    },
  ]
}

// ========== 辅助函数 ==========
const getChapterPrefix = (id) => {
  if (id === 'root') return 'root'
  const m = id.match(/^(ch\d+)/)
  return m ? m[1] : 'other'
}

const nodeColor = (d) => {
  const colors = {
    root: '#fbbf24',
    ch1: '#60a5fa',
    ch2: '#a78bfa',
    ch3: '#34d399',
    ch4: '#f87171',
    ch5: '#f472b6',
    other: '#94a3b8'
  }
  return colors[getChapterPrefix(d.id)] || colors.other
}

// 从 _cross 引用找到完整节点
const resolveCrossChild = (ref) => {
  const find = (node) => {
    if (node.id === ref.id) return { ...node, name: ref.name, _cross: true }
    if (node.children) {
      for (const c of node.children) {
        const r = find(c)
        if (r) return r
      }
    }
    return null
  }
  return find(knowledgeGraph)
}

// ========== 渐进式展开的状态 ==========
// 初始只显示 root 及其直接子节点
// expandedIds 记录哪些节点的 children 已经展开显示
const expandedIds = ref(new Set(['root']))

// 收集所有已知节点（用于查找）
const allNodes = {}
const collectAll = (node) => {
  allNodes[node.id] = node
  if (node.children) node.children.forEach(c => collectAll(c))
}
collectAll(knowledgeGraph)

// ========== 知识点富化内容 ==========
// 大白话、生活类比、公式 —— 集中管理，按 id 注入
const enrichData = {
  'root': {
    plainText: '这是一份初一上册数学的学习路线图。从左到右就是学习的先后顺序，前面的没学好，后面的就会听不懂。每条连线代表"要学这个，得先会前面那个"。',
    analogy: '就像打游戏的技能树 —— 不先点亮"有理数加减"，就学不会"整式加减"。',
    formula: '学习顺序 = 因 → 果 = 左节点 → 右节点'
  },
  'ch1-1': {
    plainBlocks: [
      { type: 'heading', text: '先搞懂两个最基础的概念' },
      { type: 'text', content: '【什么是整数？】\n像 ...-3、-2、-1、0、1、2、3... 这样没有小数点、没有分数部分的数，就是整数。' },
      { type: 'list', ordered: false, items: [
        '正整数：1、2、3、4...（数东西的数）',
        '负整数：-1、-2、-3...（表示亏欠、零下、往西等）',
        '零：0（介于正负之间，既不正也不负）',
      ]},
      { type: 'text', content: '【什么是分数？】\n把一个整体平均分成若干份，取其中的几份，就是分数。分子在上，分母在下。' },
      { type: 'list', ordered: false, items: [
        '正分数：1/2、3/7、5/4',
        '负分数：-1/2、-3/7',
        '有限小数（0.5=1/2、1.25=5/4）和无限循环小数（0.333...=1/3）本质也是分数',
      ]},

      { type: 'heading', text: '什么是"有理数"？' },
      { type: 'text', content: '有理数 = 所有能写成分数 p/q（p、q 都是整数，q≠0）的数。' },
      { type: 'callout', variant: 'tip', text: '有理数家族三成员：\n① 整数（都能写成分母是1的分数，如 5=5/1，0=0/1）\n② 分数（真分数、假分数、带分数）\n③ 有限小数 & 无限循环小数（本质都是分数）' },

      { type: 'heading', text: '什么"不是"有理数？' },
      { type: 'text', content: '只有一种：无限不循环小数。它们永远无法精确写成分数 p/q 的形式，叫"无理数"（初二学）。' },
      { type: 'table', headers: ['✓ 是有理数', '✗ 不是有理数'],
        rows: [
          ['5、-3、0（整数）', 'π ≈ 3.14159265...'],
          ['1/2、-3/7（分数）', '2开平方 ≈ 1.41421...'],
          ['0.5、1.25（有限小数）', '自然常数 e ≈ 2.71828...'],
          ['0.333...（无限循环小数）', '任何无限不循环小数'],
        ]
      },

      { type: 'heading', text: '两种分类方式' },
      { type: 'table', headers: ['按正负分', '按结构分'],
        rows: [
          ['正有理数', '整数'],
          ['零（单独一类！）', '  ├─ 正整数'],
          ['负有理数', '  ├─ 零'],
          ['', '  └─ 负整数'],
          ['', '分数'],
          ['', '  ├─ 正分数'],
          ['', '  └─ 负分数'],
        ]
      },
      { type: 'callout', variant: 'info', text: '冷知识：0.999...（无限循环9）= 1，可以写成 9/9。' },
    ],
    analogy: '有理数 = 所有"说话算数"的数 —— 你能准确说出它是多少。5 就是 5，0.5 就是一半，0.333... 永远是 1/3。\n\n无理数 = 那些"永远不重复"的数 —— π 后面数字永远不重复，你永远无法精确说出它是几分之几。',
    formula: '有理数的两种表示：\n\n按正负分：\n  有理数 = 正有理数 + 零 + 负有理数\n\n按定义分：\n  有理数 = 整数 + 分数\n  整数 = {...-3, -2, -1, 0, 1, 2, 3...}\n  分数 = 1/2, -3/7, 0.5, 0.333... 等\n\n判断：\n  ✓ 5、-3、0、0.5、1/3、0.333... 都是有理数\n  ✗ π、"2开平方"、2.71828...（e）不是有理数'
  },
  'ch1-2': {
    plainText: '数轴就是一条直线，中间一个点是0（原点），右边是正数，左边是负数。每个有理数都能在上面找到一个位置。',
    analogy: '就像温度计 —— 0°C 在中间，零上是正、零下是负，每一格都是一个数。',
    formula: '数轴三要素：原点(0)、正方向(→)、单位长度\n例：在数轴上标出 -3、0、2.5'
  },
  'ch1-3': {
    plainText: '相反数就是符号相反的两个数 —— 5 和 -5 互为相反数。绝对值就是"去掉符号只看大小" —— |-5| = 5。',
    analogy: '相反数就像电梯上行和下行同一距离：+3楼 和 -3楼 互为相反数。\n绝对值就是"不管正负，看你离原点几格" —— 电梯不管上还是下，距离地面的层数就是绝对值。',
    formula: 'a 的相反数 = -a\n|a| = a（a≥0时）\n|a| = -a（a<0时）\n例：|-7| = 7，|3| = 3'
  },
  'ch1-4': {
    plainText: '有理数加减：同号相加绝对值相加、符号不变；异号相加绝对值相减、取绝对值大的符号。减去一个数 = 加上它的相反数。',
    analogy: '同号相加 = 你今天赚 50 又赚 30，总共 +80\n异号相加 = 你赚 50 又花 30，还剩 +20\n减法 = "欠钱" —— 50 - 30 = 50 + (-30)',
    formula: '(+3) + (+5) = +8\n(-3) + (-5) = -8\n(+3) + (-5) = -2\n5 - 3 = 5 + (-3)'
  },
  'ch1-5': {
    plainText: '有理数乘除：同号得正、异号得负，然后绝对值相乘除。任何数乘 0 得 0。',
    analogy: '乘除的符号规则就像"翻牌"：正正=正、负负=正（翻两次翻回来了）、正负=负（翻一次翻面了）。',
    formula: '(+3) × (+5) = +15\n(-3) × (-5) = +15\n(+3) × (-5) = -15\n(-10) ÷ (+2) = -5'
  },
  'ch1-rp': {
    plainBlocks: [
      { type: 'heading', text: '什么是"倒数"？' },
      { type: 'text', content: '乘积为 1 的两个数互为倒数。' },
      { type: 'callout', variant: 'tip', text: '找倒数的方法：把分子分母倒过来就行！\n整数看成分母是1的分数，比如 5 = 5/1，倒数就是 1/5' },
      { type: 'table', headers: ['原来的数', '它的倒数', '怎么得到的'],
        rows: [
          ['5（即 5/1）', '1/5', '分子分母颠倒'],
          ['2/3', '3/2', '分子分母颠倒'],
          ['-4（即 -4/1）', '-1/4', '分子分母颠倒，符号不变'],
          ['-3/7', '-7/3', '分子分母颠倒，符号不变'],
          ['0.5（即 1/2）', '2', '0.5×2=1'],
        ]
      },

      { type: 'heading', text: '几个重要的特例' },
      { type: 'list', ordered: false, items: [
        '1 的倒数是 1（因为 1×1=1）',
        '-1 的倒数是 -1（因为 (-1)×(-1)=1）',
        '**0 没有倒数！** 因为 0 乘以任何数都是 0，永远得不到 1',
      ]},

      { type: 'heading', text: '倒数最大的用处：把除法变成乘法' },
      { type: 'text', content: '除以一个数（不能是0）= 乘以这个数的倒数\n\n这是除法运算最核心的转化！比如：\n10 ÷ 5 = 10 × (1/5) = 2\n(-12) ÷ (-3) = (-12) × (-1/3) = 4' },
      { type: 'callout', variant: 'info', text: '为什么要这样做？因为乘法比除法好算！\n特别是遇到分数除法时，"除以分数 = 乘以它的倒数"立刻把难题变成简单的分数乘法。' },
    ],
    analogy: '倒数 = 一张纸的正反面 —— 正面是 3/4，翻过来就是 4/3，合在一起（相乘）就像这张纸完整了（等于1）。\n\n0 没有倒数 = 一张空白的纸，你翻过来还是空白，合在一起还是空白，永远凑不到那"完整的1"。',
    formula: '倒数定义：a × (1/a) = 1（a ≠ 0）\n\n求倒数：\n  5 的倒数 = 1/5\n  2/3 的倒数 = 3/2\n  -4 的倒数 = -1/4\n  0 没有倒数\n\n除法变乘法：\n  a ÷ b = a × (1/b)（b ≠ 0）\n  例：10 ÷ 5 = 10 × 1/5 = 2\n  例：(2/3) ÷ (4/5) = (2/3) × (5/4) = 10/12 = 5/6'
  },
  'ch1-6': {
    plainText: '乘方就是"几个相同的数相乘"的简写。科学记数法用来表示很大或很小的数 —— 把小数点移到第一位后面，移了几位就是 10 的几次方。',
    analogy: '乘方 = 叠罗汉 —— 2³ = 2×2×2，就是把 2 叠了 3 层\n科学记数法 = 光年 —— 地球到太阳很远，写成 1.5×10⁸ 千米比写一堆零方便多了。',
    formula: 'aⁿ = a × a × ... × a（n个a相乘）\n10⁵ = 100000\n科学记数法：a×10ⁿ（1≤|a|<10）\n例：56000 = 5.6×10⁴'
  },
  'ch2-1': {
    plainText: '用字母代替具体的数字 —— 这是从"算术"到"代数"最关键的一步。字母 x、y、a、b 都可以代表任意数。',
    analogy: '就像填字游戏 —— 3 + ? = 7 里的问号就是"用字母表示数"的雏形，只不过正式写法是 3 + x = 7。',
    formula: '用字母表示：\n  加法交换律 → a + b = b + a\n  速度公式   → s = v × t\n  面积公式   → S = a × b'
  },
  'ch2-2': {
    plainBlocks: [
      { type: 'heading', text: '什么是"代数式"？' },
      { type: 'text', content: '用运算符号（+ - × ÷）把数和字母连起来的式子，就叫代数式。\n单独一个数（如 7）或单独一个字母（如 x），也算是代数式。' },
      { type: 'callout', variant: 'info', text: '✓ 是代数式：3、x、3+x、5ab、-a²b' },

      { type: 'heading', text: '什么是"单项式"？' },
      { type: 'text', content: '单项式 = 只有数字和字母相乘（包括字母自己乘自己=乘方），绝不出现"+"、"-"或"分母里有字母"。简单说就是一个"完整的块"。' },
      { type: 'callout', variant: 'tip', text: '为什么单独的数和字母也算单项式？\n  单独数字 7 → 可看成 7×x⁰（x⁰=1），还是乘法\n  单独字母 x → 可看成 1×x，系数1省略了\n  πr² → π 是数字（常数），不是字母变量！' },
      { type: 'table', headers: ['✓ 是单项式', '✗ 不是单项式', '为什么'],
        rows: [
          ['7（单独数字）', '3+x', '有+号，是加法'],
          ['x（单独字母）', '2/x', 'x在分母，是除法'],
          ['3x、-5ab', '(x+1)/2', '拆开后有+号'],
          ['πr²、x³y²', 'x+2y', '有+号连接'],
        ]
      },

      { type: 'heading', text: '单项式的两个零件：系数 + 次数' },
      { type: 'table', headers: ['式子', '系数（字母前的数字，带符号）', '次数（所有字母指数之和）'],
        rows: [
          ['3x', '3', '1（x的指数没写=1）'],
          ['-5a²b', '-5', '3（a²的2 + b¹的1 = 3）'],
          ['x', '1（省略了）', '1'],
          ['-x', '-1（省略了）', '1'],
          ['πr²', 'π（π是数字）', '2'],
          ['7（单独数字）', '7', '0（没有字母，叫零次单项式）'],
        ]
      },

      { type: 'heading', text: '什么是"多项式"？' },
      { type: 'text', content: '多项式 = 几个单项式用"+"或"-"连起来的式子。' },
      { type: 'text', content: '【什么是"项"？】把多项式里的每个单项式，连同它前面的符号一起，叫做多项式的一个"项"。\n例：3x² - 2x + 5 有 3 项 → 3x²、-2x、+5（常数项）' },

      { type: 'heading', text: '多项式的命名：几次几项式' },
      { type: 'text', content: '"几次" = 所有项中次数最高那一项的次数\n"几项" = 总共有几项' },
      { type: 'table', headers: ['多项式', '几项', '最高次项', '命名'],
        rows: [
          ['3x + 2y', '2', '3x（次数1）', '一次二项式'],
          ['x² - 2x + 1', '3', 'x²（次数2）', '二次三项式'],
          ['-5x³y + 7xy', '2', '-5x³y（次数4）', '四次二项式'],
          ['5', '1', '5（次数0）', '零次一项式'],
        ]
      },

      { type: 'heading', text: '什么是"整式"？' },
      { type: 'text', content: '整式 = 单项式 和 多项式 的合称。\n整式里不会出现字母在分母的情况。' },
      { type: 'tree', lines: [
        '代数式',
        '├── 整式（字母不在分母）',
        '│   ├── 单项式（没有加减号）',
        '│   └── 多项式（有加减号连接多个单项式）',
        '└── 分式（字母在分母，如 2/x，八年级学）',
      ]},
    ],
    analogy: '单项式 = 一个完整的单词（dog），没有空格也没有标点。单独字母 x = 单字母单词；单独数字 7 = 不带字母的特殊单词。\n\n多项式 = 一串用 + 或 - 连起来的单词（dog + cat - bird），每个单词是一项。\n\n整式 = 所有单词和句子的统称 —— 不允许"字母在分母"的怪东西（那叫分式）。',
    formulaBlocks: [
      { type: 'text', content: '===== 系数与次数速查表 =====' },
      { type: 'table', headers: ['式子', '系数', '次数'],
        rows: [
          ['3x', '3', '1'],
          ['-5a²b', '-5', '3（2+1）'],
          ['x', '1（省略）', '1'],
          ['-x', '-1（省略）', '1'],
          ['πr²', 'π', '2'],
          ['7', '7', '0'],
        ]
      },
      { type: 'text', content: '===== 多项式命名速查 =====\n3x - 5         → 一次二项式\nx² + 3x + 2    → 二次三项式\n2a²b - 3a + 1  → 三次三项式（最高次项 2a²b 次数=2+1=3）' },
    ]
  },
  'ch2-3': {
    plainBlocks: [
      { type: 'heading', text: '什么是同类项？' },
      { type: 'text', content: '两个单项式要成为同类项，必须同时满足两个条件：\n① 所含字母完全相同\n② 相同字母的指数也完全相同\n\n【关键：系数和符号完全无所谓！】' },
      { type: 'table', headers: ['两个单项式', '是同类项？', '原因'],
        rows: [
          ['3x²y 和 -5x²y', '✓ 是', '字母都是x和y，指数都相同'],
          ['7 和 -3', '✓ 是', '都是常数单项式，常数项之间都是同类项'],
          ['3x² 和 3x', '✗ 不是', '字母相同但一个指数2一个指数1'],
          ['2xy 和 3xz', '✗ 不是', '第一个有y没有z，字母不同'],
          ['3x 和 3', '✗ 不是', '第一个有字母x，第二个没有'],
        ]
      },

      { type: 'heading', text: '什么是"合并同类项"？' },
      { type: 'text', content: '把多项式里的同类项合并成一项，就叫合并同类项。\n怎么做？三个字：**系数加，字母留**' },
      { type: 'callout', variant: 'tip', text: '系数带符号相加（有理数加减），字母和指数原样保留，一个字符都别动。\n\n为什么能合并？其实就是乘法分配律的逆运算：\n3x²y - 5x²y = (3-5)x²y = -2x²y' },
    ],
    analogy: '同类项 = 同色同图案的积木块 —— 不管是 3 块红色圆形还是 -5 块红色圆形，都是"红色圆形"，能堆到一起数。合并就是数总数（3 + (-5) = -2 块红色圆形）。\n但红色圆形和蓝色圆形不一样，不能混在一起数！',
    formula: '合并同类项示例：\n  3x²y + (-5x²y) = (3 + -5) · x²y = -2x²y\n\n完整例子：\n  2x² - 3xy + 5 + 4x² + xy - 2\n= (2x² + 4x²) + (-3xy + xy) + (5 - 2)\n= 6x² + (-2xy) + 3\n= 6x² - 2xy + 3'
  },
  'ch2-4': {
    plainBlocks: [
      { type: 'heading', text: '什么是"整式的加减"？' },
      { type: 'text', content: '整式 = 单项式 + 多项式。整式加减 = 对整式做加、减运算。\n\n本质只有两步：\n① 去括号（如果有括号）\n② 合并同类项\n\n结果一定会是一个最简整式。' },

      { type: 'heading', text: '关键难点：去括号！' },
      { type: 'table', headers: ['括号前符号', '操作', '例子'],
        rows: [
          ['+', '括号里每一项不变号，直接拆', '+(3x + 2y - 1) = 3x + 2y - 1'],
          ['-', '括号里**每一项都要变号**', '-(3x + 2y - 1) = -3x - 2y + 1'],
        ]
      },
      { type: 'callout', variant: 'warn', text: '为什么负号要变号？因为负号相当于乘以-1：\n-(3x + 2y - 1) = (-1)×3x + (-1)×2y + (-1)×(-1) = -3x - 2y + 1' },

      { type: 'heading', text: '完整步骤演示' },
      { type: 'text', content: '题目：化简 (3x² - 2x + 1) - (2x² + 3x - 5)\n\n① 去括号：\n  = 3x² - 2x + 1 - 2x² - 3x + 5  （第二个括号前是负号，里面全变号！）\n\n② 找同类项：\n  3x² 和 -2x² 是同类项\n  -2x 和 -3x 是同类项\n  1 和 5 是同类项\n\n③ 合并同类项：\n  = (3-2)x² + (-2-3)x + (1+5)\n  = x² - 5x + 6 ✓' },
    ],
    analogy: '去括号就像拆快递 —— 括号就是快递盒。如果快递盒上写着"+"，东西原样拿出；如果写着"-"，所有东西都要翻一面（变号）。',
    formula: '去括号：+(a - b) = a - b\n        -(a - b) = -a + b\n例子：(3x + 2) - (2x - 5)\n     = 3x + 2 - 2x + 5\n     = x + 7'
  },
  'ch2-5': {
    plainText: '整式乘法分三级：单项式×单项式、单项式×多项式、多项式×多项式。核心就是"分配律" —— 用一个去乘另一个的每一项。',
    analogy: '分配律 = 发作业本 —— 老师拿一摞本子（多项式），每个同学（单项式）都要分到一本，发完所有同学再把本子收回来合并。',
    formula: '单项式×单项式：3a × 4b = (3×4)(a×b) = 12ab\n单项式×多项式：2a(3a + b) = 6a² + 2ab\n多项式×多项式：(a+b)(c+d) = ac + ad + bc + bd（FOIL法）'
  },
  'ch3-1': {
    plainBlocks: [
      { type: 'heading', text: '先搞懂两个前置概念' },
      { type: 'callout', variant: 'info', text: '【式子 vs 等式】\n式子 = 一个"对象"（3、x、3+x、2x²-3y 都是式子）\n等式 = 两个式子之间的"相等关系"（必须有 = 号）' },
      { type: 'list', ordered: false, items: [
        '✓ 是等式：2+3=5（两边都是数）',
        '✓ 是等式：a+b=b+a（永远成立，叫"恒等式"）',
        '✓ 是等式：x+2=5（只有x=3时成立，叫"条件等式"）',
        '✗ 不是等式：3x+2（只是一个式子，没有=号）',
      ]},

      { type: 'heading', text: '什么是"方程"？' },
      { type: 'text', content: '方程 = 含有未知数的等式。两个条件缺一不可：\n① 有未知数（通常用 x、y、z 表示）\n② 是等式（有 = 号）' },
      { type: 'table', headers: ['式子', '是方程吗？', '原因'],
        rows: [
          ['2x + 3 = 7', '✓ 是', '有x，有=号'],
          ['x² = 4', '✓ 是', '有x，有=号'],
          ['x + y = 5', '✗ 不是（本册不学）', '两个未知数，是"二元"方程'],
          ['x + 3 > 5', '✗ 不是', '没有=号，是不等式'],
          ['2 + 3 = 5', '✗ 不是', '没有未知数，是恒等式'],
          ['3x + 2', '✗ 不是', '只是式子，没有=号'],
        ]
      },

      { type: 'heading', text: '什么是"一元一次方程"？' },
      { type: 'text', content: '"一元一次"是两个限定词，必须同时满足：\n① 一元 = 只有一个未知数（只能有 x 或 y，不能同时有 x 和 y）\n② 一次 = 未知数的最高次数是 1（不能有 x²、x³，也不能未知数在分母）' },
      { type: 'table', headers: ['方程', '是一元一次吗？', '原因'],
        rows: [
          ['2x + 3 = 7', '✓ 是', '一个x，次数1'],
          ['-3x = 12', '✓ 是', '一个x，次数1'],
          ['x + y = 5', '✗ 不是', '二元（两个未知数）'],
          ['x² = 4', '✗ 不是', '二次（x次数是2）'],
          ['1/x = 3', '✗ 不是', 'x在分母，不是整式方程'],
        ]
      },

      { type: 'heading', text: '方程的解是什么意思？' },
      { type: 'text', content: '找到一个数，把它代入未知数后，等式两边真的相等，这个数就是方程的解。\n\n例：x + 2 = 5\n把 x=3 代入：左边=3+2=5，右边=5，两边相等！\n所以 x=3 就是这个方程的解。' },
      { type: 'callout', variant: 'tip', text: '解方程 = 找到所有能让等式成立的未知数的值的过程。' },
    ],
    analogy: '方程 = 天平 —— 左右两边重量相等（等式），但一边放了个"神秘物品 x"（未知数），你要找出 x 多重才能让天平继续平衡。\n\n"一元一次"的筛选 = 面试条件：\n  条件1：只能一个候选人（一元）\n  条件2：只能是第一次来应聘（一次，不能有历史记录 x²）',
    formula: '方程的严格定义：\n  含有未知数的等式\n  ↓\n  满足两个条件：有未知数 + 有 = 号\n\n一元一次方程的标准形式：\n  ax + b = 0（a ≠ 0）\n  例：2x + 3 = 7 → 2x + (-4) = 0\n\n最简形式：x = c\n  例：x = 2（已解出）'
  },
  'ch3-2': {
    plainText: '等式性质：等式两边做一样的操作（加、减、乘、除同一个数），等式仍然成立。这就是解方程的"法律"。',
    analogy: '等式 = 跷跷板 —— 两边各加 2 个苹果，还是平衡；两边同时翻倍，还是平衡。但只能"加/减/乘/除"，不能"偷换物品"。',
    formula: '等式性质1：若 a = b，则 a + c = b + c\n等式性质2：若 a = b，则 a × c = b × c（c≠0）\n减法是加法的逆：a = b → a - c = b - c'
  },
  'ch3-3': {
    plainText: '解一元一次方程五步走：去分母 → 去括号 → 移项 → 合并同类项 → 系数化为1。每一步都有明确的操作和目的。',
    analogy: '解方程 = 剥洋葱 —— 一层一层去掉多余的东西，最后只剩 x。\n  去分母 = 剥掉最外层的包装纸\n  去括号 = 拆中间层\n  移项   = 把"无关的"移到另一边\n  合并   = 清理残余\n  系数化1 = 得到纯净的 x',
    formula: '解方程：(x/2) + 3 = 7\n1. 去分母：x + 6 = 14\n2. 去括号：(无)\n3. 移项：x = 14 - 6\n4. 合并：x = 8\n5. 系数化1：x = 8 ✓'
  },
  'ch3-4': {
    plainText: '应用题五步：审题（读懂题意）→ 设未知数（x代表什么）→ 找等量关系（最关键！）→ 列方程 → 求解检验。',
    analogy: '应用题 = 侦探破案 —— 审题就是读案情，设 x 就是锁定嫌疑人，找等量关系就是找到作案手法（最核心的线索），列方程就是写起诉状，求解就是审判。',
    formula: '审题 → 设 x → 列方程 → 解方程 → 检验\n\n例子：小明有 50 元，买了 3 本笔记本后剩 23 元，每本多少钱？\n解：设每本 x 元\n   50 - 3x = 23\n   -3x = -27\n   x = 9\n答：每本 9 元。'
  },
  'ch4-1': {
    plainText: '图形的三种运动：平移（直直地推）、旋转（绕一个点转）、对称（照镜子）。运动前后图形的形状大小都不变，只是位置变了。',
    analogy: '平移 = 把书从书桌左边推到右边\n旋转 = 开门，门绕着门轴转\n对称 = 你和镜子里的你',
    formula: '平移：方向 + 距离（例：向右平移5格）\n旋转：旋转中心 + 旋转方向 + 角度（例：绕O点顺时针转90°）\n对称：对称轴（例：沿y轴对称）'
  },
  'ch4-2': {
    plainBlocks: [
      { type: 'heading', text: '三者对比：端点 vs 方向 vs 能否测量' },
      { type: 'table', headers: ['对比项', '线段', '射线', '直线'],
        rows: [
          ['端点数量', '2 个', '1 个', '0 个'],
          ['延伸方向', '无（不能延伸）', '一个方向', '两个方向'],
          ['长度', '有限，可测量', '无限，不可测量', '无限，不可测量'],
          ['表示法', '线段 AB（或 BA）', '射线 OA（端点O在前）', '直线 AB 或 a'],
          ['大写字母含义', '两个端点', 'O=端点，A=延伸方向上一点', '两个点或一个字母'],
        ]
      },
      { type: 'callout', variant: 'warn', text: '射线表示法容易错：端点 O 必须写在前面！\n射线 OA ≠ 射线 AO（一个从O向A方向延伸，一个从A向O方向延伸）' },

      { type: 'heading', text: '它们之间的关系' },
      { type: 'text', content: '射线是直线的一半（在直线上截一个端点）\n线段是直线上"揪两个端点出来"的部分\n\n线段 → 延长一端 = 射线\n线段 → 延长两端 = 直线' },
      { type: 'tree', lines: [
        '直线',
        '├── 截一个端点 → 射线',
        '└── 截两个端点 → 线段',
      ]},
    ],
    analogy: '线段 = 筷子 —— 两头都封了、长度固定、可测量\n射线 = 手电筒的光 —— 一头在手里（端点）、另一头照到无限远\n直线 = 无限长的铁轨 —— 两头都看不到尽头',
    formula: '三者对比表：\n          线段    射线    直线\n端点数量    2       1       0\n延伸方向    无    一个方向  两个方向\n长度      有限    无限     无限\n能否测量   ✓       ✗       ✗\n\n表示法：\n  线段 AB 或 BA（端点顺序可换）\n  射线 OA（端点 O 必须在前）\n  直线 AB 或 a\n\n作图示意：\n  线段：  ←·———·→  两个端点\n  射线：  ←·——————  一个端点，右侧无限\n  直线：  —·———·—  无端点，两端都无限'
  },
  'ch4-3': {
    plainText: '角是"两条有公共端点的射线"组成的图形。度、分、秒是角的度量单位，60进制（1°=60′，1′=60″）。',
    analogy: '角 = 剪刀 —— 两片刀刃绕着一个点（轴）张开，张得越大角越大。',
    formula: '角的表示：∠AOB（O是顶点）\n角的分类：\n  锐角  0° < α < 90°\n  直角  α = 90°\n  钝角  90° < α < 180°\n度分秒换算：1° = 60′ = 3600″'
  },
  'ch4-4': {
    plainText: '角的比较可以用"叠合法"（把两个角叠在一起看）。角平分线就是把一个角分成两个相等的小角的那条射线。',
    analogy: '角平分线 = 蛋糕的中心线 —— 一刀切下去，左右两块大小完全一样。',
    formula: '若 OC 平分 ∠AOB，则 ∠AOC = ∠BOC = ∠AOB/2\n\n例子：∠AOB = 80°，OC 平分它\n     → ∠AOC = 40°'
  },
  'ch4-5': {
    plainBlocks: [
      { type: 'heading', text: '什么是"三线八角"？' },
      { type: 'text', content: '两条直线（a 和 b）被第三条直线（叫截线 c）穿过，一共形成 8 个角。根据位置不同，分成三类特殊角。' },

      { type: 'table', headers: ['角的类型', '位置特点', '像哪个字母', '平行判定'],
        rows: [
          ['同位角', '位置相同，都在截线同侧、两直线同方向', 'F', '同位角相等 → a∥b'],
          ['内错角', '在两直线之间（内部），截线两侧（错开）', 'Z', '内错角相等 → a∥b'],
          ['同旁内角', '在两直线之间，截线同侧', 'U', '同旁内角互补（和=180°）→ a∥b'],
        ]
      },

      { type: 'heading', text: '关键区分：判定 vs 性质' },
      { type: 'table', headers: ['', '判定（破案）', '性质（定罪后）'],
        rows: [
          ['方向', '角 → 平行', '平行 → 角'],
          ['含义', '已知角的关系，判断平行', '已知平行，推出角的关系'],
          ['同位角', '∠1=∠5 → a∥b', 'a∥b → ∠1=∠5'],
          ['内错角', '∠3=∠5 → a∥b', 'a∥b → ∠3=∠5'],
          ['同旁内角', '∠3+∠6=180° → a∥b', 'a∥b → ∠3+∠6=180°'],
        ]
      },
      { type: 'callout', variant: 'info', text: '判定 = 角的关系是证据，用来"破案"（证明平行）\n性质 = 已经定罪（已知平行），可以"判刑"（推出角的关系）' },
    ],
    analogy: '平行线 = 铁轨 —— 两条永远不交叉的直线。截线 = 一根枕木，同时穿过两条铁轨，产生 8 个角。\n\n同位角 = 两根枕木同一位置的"对应螺丝钉"\n内错角 = 铁轨中间、左右错开的"交叉螺丝钉"\n同旁内角 = 铁轨中间、同一侧的"同侧螺丝钉"',
    formula: '三线八角示意图：\n        c（截线）\n      ↗ ↖ ↗ ↖\n    a ———·——·———\n      ↘ ↙ ↘ ↙\n    b ———·——·———\n\n同位角：∠1 和 ∠5（位置相同）\n内错角：∠3 和 ∠5（内部两侧）\n同旁内角：∠3 和 ∠6（内部同侧）\n\n判定（角→平行）：\n  ∠1=∠5 → a∥b（同位角相等）\n  ∠3=∠5 → a∥b（内错角相等）\n  ∠3+∠6=180° → a∥b（同旁内角互补）\n\n性质（平行→角）：\n  a∥b → ∠1=∠5\n  a∥b → ∠3=∠5\n  a∥b → ∠3+∠6=180°'
  },
  'ch4-6': {
    plainText: '垂线就是相交成 90° 的两条直线。点到线的距离 = 从这个点到直线作垂线段的长度 —— 垂线段最短！',
    analogy: '垂线 = 墙角 —— 两面墙相交成的角就是 90°。\n点到线的距离 = 你站在地上，到头顶天花板的最短路径就是垂直向上 —— 斜着爬反而更远。',
    formula: '垂直：a ⊥ b（表示a与b垂直，交点叫垂足）\n点P到直线l的距离：过P作 l 的垂线，垂足为Q，则 PQ 的长度就是距离\n\n公理：过一点有且只有一条直线与已知直线垂直'
  },
  'ch5-1': {
    plainText: '统计调查六步：提出问题 → 设计调查方案 → 收集数据 → 整理数据 → 描述数据 → 分析数据得出结论。',
    analogy: '统计调查 = 做奶茶市场调研 —— 你想知道什么（问题）→ 怎么查（方案）→ 问谁（收集）→ 把答案分类（整理）→ 画图展示（描述）→ 说结论（分析）。',
    formula: '调查步骤：\n① 提出问题（如：全班同学最喜欢的运动？）\n② 设计方案（问卷/投票）\n③ 收集数据（每个同学选一个）\n④ 整理数据（数一数各运动多少票）\n⑤ 描述数据（画条形图）\n⑥ 分析结论（乒乓球最受欢迎）'
  },
  'ch5-2': {
    plainText: '三种常用统计图：条形图看数量多少；折线图看变化趋势；扇形图看比例分布。各有各的用场！',
    analogy: '条形图 = 成绩单上每科的分数条 —— 一眼看出哪科高哪科低\n折线图 = 股票走势图 —— 看涨跌趋势\n扇形图 = 披萨 —— 一块占多大比例',
    formula: '条形图：独立数据，比较大小\n折线图：时间序列，看变化\n扇形图：百分比，各部分占整体的多少\n  扇形中心角 = 该部分百分比 × 360°'
  },
  'ch5-3': {
    plainText: '平均数就是"把所有数加起来除以个数"。加权平均数就是每个数有不同的权重（重要程度），算的时候要乘上权重。',
    analogy: '平均数 = 全班平均分 —— 所有同学分数加起来除以人数\n加权平均数 = 期末考试总成绩 —— 期中占 40%、期末占 60%，要乘以权重再相加',
    formula: '普通平均数：x̄ = (x₁ + x₂ + ... + xₙ) / n\n\n加权平均数：x̄ = (x₁w₁ + x₂w₂ + ... + xₙwₙ) / (w₁ + w₂ + ... + wₙ)\n\n例子：3, 5, 7 的平均数 = (3+5+7)/3 = 5'
  },
  'ch5-4': {
    plainText: '方差反映一组数据"离平均值有多远" —— 方差越大，数据越分散（不稳定）；方差越小，数据越集中（稳定）。',
    analogy: '方差 = 投篮命中率的"稳定性" —— 小明偶尔投中10个偶尔投中0个（方差大，不稳定）；小红每次都投中5个左右（方差小，稳定）。',
    formula: '方差公式：\ns² = [(x₁-x̄)² + (x₂-x̄)² + ... + (xₙ-x̄)²] / n\n\n方差越小 → 数据越集中越稳定\n方差越大 → 数据越分散波动越大\n标准差 = 方差开平方（初二学）'
  },
}

// 将富化数据注入 allNodes
Object.entries(enrichData).forEach(([id, enrich]) => {
  if (allNodes[id]) {
    Object.assign(allNodes[id], enrich)
  }
})

// 根据展开状态生成当前可见的节点和链接
const buildVisibleGraph = () => {
  const visibleIds = new Set()
  const links = []

  const walk = (node) => {
    visibleIds.add(node.id)
    if (expandedIds.value.has(node.id) && node.children) {
      node.children.forEach(child => {
        const resolved = child._cross ? resolveCrossChild(child) : child
        if (resolved) {
          links.push({ source: node.id, target: resolved.id, value: child._cross ? 0.3 : 1 })
          walk(resolved)
        }
      })
    }
  }
  walk(knowledgeGraph)

  // 构建节点数组（包含所有 visibleIds 的完整数据）
  const nodes = []
  visibleIds.forEach(id => {
    const n = allNodes[id]
    if (n) {
      nodes.push({
        id: n.id,
        name: n.name,
        description: n.description,
        tags: n.tags,
        depth: 0,
        _hasChildren: n.children && n.children.length > 0,
        _isCross: false
      })
    }
  })

  return { nodes, links }
}

// ========== 桑基图渲染 ==========
let svg = null, g = null, linkSel = null, nodeSel = null

const render = () => {
  try {
    errorMessage.value = ''
    if (!svgRef.value) return

    const container = svgRef.value.parentElement
    let width = container.clientWidth || 1200
    let height = container.clientHeight || 800

    svgRef.value.innerHTML = ''

    svg = d3.select(svgRef.value)
      .attr('width', width)
      .attr('height', height)
      .style('background', 'transparent')

    g = svg.append('g')

    d3.select(svgRef.value).call(
      d3.zoom().scaleExtent([0.3, 2]).on('zoom', (e) => g.attr('transform', e.transform))
    )

    const { nodes, links } = buildVisibleGraph()
    const data = JSON.parse(JSON.stringify({ nodes, links }))

    const gen = sankey()
      .nodeId(d => d.id)
      .nodeWidth(40)
      .nodePadding(14)
      // 四周留白：让桑基图不布满全图
      .extent([[80, 60], [width - 100, height - 60]])

    const graph = gen(data)

    // 画链接
    linkSel = g.append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(graph.links)
      .join('path')
      .attr('d', sankeyLinkHorizontal())
      .attr('stroke', d => d.value < 1 ? '#6b7280' : '#475569')
      .attr('stroke-dasharray', d => d.value < 1 ? '4,4' : null)
      .attr('stroke-width', d => Math.max(2, d.width))
      .attr('fill', 'none')
      .attr('opacity', 0.5)

    // 画节点组
    nodeSel = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(graph.nodes)
      .join('g')
      .attr('transform', d => `translate(${d.x0},${d.y0})`)
      .attr('cursor', d => d._hasChildren ? 'pointer' : 'default')
      .on('click', (event, d) => {
        event.stopPropagation()
        selectedNode.value = allNodes[d.id]

        if (d._hasChildren) {
          if (expandedIds.value.has(d.id)) {
            expandedIds.value.delete(d.id)
          } else {
            expandedIds.value.add(d.id)
          }
          render()
        }
      })
      .on('mouseenter', (event, d) => {
        linkSel.attr('stroke-opacity', l =>
          (l.source === d || l.target === d) ? 0.9 : 0.15
        ).attr('stroke-width', l =>
          (l.source === d || l.target === d) ? Math.max(4, l.width + 1) : Math.max(2, l.width * 0.6)
        )
      })
      .on('mouseleave', () => {
        linkSel.attr('stroke-opacity', 0.5)
          .attr('stroke-width', d => Math.max(2, d.width))
      })

    // 节点矩形
    nodeSel.append('rect')
      .attr('width', d => d.x1 - d.x0)
      .attr('height', d => d.y1 - d.y0)
      .attr('fill', d => nodeColor(d))
      .attr('rx', 3)
      .attr('stroke', d => expandedIds.value.has(d.id) ? '#fff' : 'rgba(255,255,255,0.4)')
      .attr('stroke-width', d => expandedIds.value.has(d.id) ? 2 : 1)

    // 节点名称 —— 按节点形状自适应方向
    // 宽节点（扁/方）→ 横排自动换行；瘦长节点（管道）→ 竖排
    nodeSel.each(function(d) {
      const rectW = d.x1 - d.x0
      const rectH = Math.max(24, d.y1 - d.y0)
      const chars = d.name.split('')
      const isRoot = d.id === 'root'
      const fontSize = isRoot ? 12 : 11
      const isTall = rectH > rectW * 1.1  // 高度明显大于宽度 → 竖排

      const text = d3.select(this).append('text')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('fill', '#fff')
        .attr('font-size', fontSize + 'px')
        .attr('font-weight', isRoot ? 'bold' : '500')
        .attr('pointer-events', 'none')

      if (isTall) {
        // === 竖排：逐字符向下 ===
        const charH = Math.max(10, Math.min(14, Math.floor((rectH - 8) / chars.length)))
        const x = rectW / 2
        const totalH = chars.length * charH
        const startY = Math.max(fontSize, (rectH - totalH) / 2 + charH)

        text.attr('x', x).attr('y', startY)
        chars.forEach((ch, i) => {
          text.append('tspan').attr('x', x).attr('dy', i === 0 ? 0 : charH).text(ch)
        })
      } else {
        // === 横排：按节点宽度自动换行 ===
        const padX = 4
        const maxCharsPerLine = Math.max(1, Math.floor((rectW - padX * 2) / (fontSize * 0.9)))
        const lines = []
        for (let i = 0; i < chars.length; i += maxCharsPerLine) {
          lines.push(chars.slice(i, i + maxCharsPerLine).join(''))
        }

        const lineH = fontSize + 2
        const totalH = lines.length * lineH
        const startY = Math.max(fontSize, (rectH - totalH) / 2 + lineH / 2)
        const x = rectW / 2

        text.attr('x', x).attr('y', startY)
        lines.forEach((line, i) => {
          text.append('tspan').attr('x', x).attr('dy', i === 0 ? 0 : lineH).text(line)
        })
      }
    })

    // 展开指示器（节点右上角）
    nodeSel.filter(d => d._hasChildren).append('text')
      .attr('x', d => (d.x1 - d.x0) - 6)
      .attr('y', 14)
      .attr('text-anchor', 'end')
      .attr('fill', 'rgba(255,255,255,0.95)')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('pointer-events', 'none')
      .text(d => expandedIds.value.has(d.id) ? '−' : '+')

    loaded.value = true
    loading.value = false
  } catch (err) {
    errorMessage.value = err.message + '\n' + err.stack
    console.error('Failed to render sankey:', err)
    loading.value = false
  }
}

const resetView = () => {
  expandedIds.value = new Set(['root'])
  selectedNode.value = null
  render()
}

onMounted(() => {
  setTimeout(render, 100)
})
</script>

<style scoped>
</style>
