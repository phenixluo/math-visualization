<template>
  <div class="space-y-6">
    <!-- 章节选择器 -->
    <div class="flex flex-wrap gap-2 mb-4">
      <button 
        v-for="chapter in chapters" 
        :key="chapter.id"
        :class="[
          'px-4 py-2 rounded bg-slate-700 text-white',
          currentChapter === chapter.id ? 'bg-amber-600' : 'hover:bg-slate-600'
        ]"
        @click="currentChapter = chapter.id"
      >
        {{ chapter.title }}
      </button>
    </div>

    <!-- 知识点思维导图展示区 -->
    <div class="bg-slate-800 rounded-xl p-6 min-h-[500px] relative">
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-slate-900/50">
        <div class="text-gray-400">正在生成思维导图...</div>
      </div>
      
      <transition name="fade">
        <div v-if="knowledgeMapContent" :key="currentChapter" class="relative">
          <!-- 这里将嵌入具体章节的知识点思维导图 -->
          <div class="h-full">
            <!-- 知识点节点和连接线将通过SVG或Canvas绘制 -->
            <svg ref="svgRef" class="w-full h-full" style="background:rgba(15,23,42,.6)"></svg>
          </div>
        </div>
      </transition>
      
      <!-- 提示信息 -->
      <div v-else class="text-center text-gray-500 py-10">
        请选择一个章节查看其知识点思维导图
      </div>
    </div>
    
    <!-- 知识点详情面板 -->
    <div v-if="selectedKnowledgePoint" class="bg-slate-800 rounded-xl p-4">
      <h3 class="text-xl font-bold text-amber-400 mb-2">{{ selectedKnowledgePoint.title }}</h3>
      <p class="text-gray-300 mb-2">{{ selectedKnowledgePoint.description }}</p>
      <div class="flex flex-wrap gap-2">
        <span v-for="tag in selectedKnowledgePoint.tags" :key="tag"
              class="px-2 py-1 bg-slate-700 text-xs rounded">{{ tag }}</span>
      </div>
      
      <!-- 如果有可视化内容，显示对应的学习组件 -->
      <div v-if="selectedKnowledgePoint.component" class="mt-4">
        <keep-alive>
          <component :is="selectedKnowledgePoint.component" />
        </keep-alive>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as d3 from 'd3'

// 定义北师大版初一数学知识点结构（基于实际教材）
const chapters = ref([
  { id: 'rational', title: '有理数', icon: '🔢' },
  { id: 'expression', title: '整式的加减', icon: '📐' },
  { id: 'equation', title: '一元一次方程', icon: '⚖️' },
  { id: 'geometry', title: '几何图形初步', icon: '📐' },
  { id: 'data', title: '数据收集与描述', icon: '📊' },
  { id: 'inequality', title: '一元一次不等式', icon: '📏' },
  { id: 'triangle', title: '三角形', icon: '🔺' },
  { id: 'polynomial', title: '整式的乘法与因式分解', icon: '🔢' },
  { id: 'fraction', title: '分数', icon: '➗' }
])

const currentChapter = ref('rational')
const loading = ref(false)
const knowledgeMapContent = ref(null)
const selectedKnowledgePoint = ref(null)
const selectedNodeId = ref(null)
const svgRef = ref(null)

// 知识点数据结构 - 每个章节包含相互关联的知识点
const knowledgePoints = {
  rational: [
    { 
      id: 'r1', 
      title: '有理数的概念', 
      description: '正有理数、负有理数和零统称为有理数',
      tags: ['概念', '数轴'],
      connections: ['r2', 'r3', 'r4']
    },
    { 
      id: 'r2', 
      title: '数轴表示法', 
      description: '用一条直线来表示数，称为数轴',
      tags: ['表示', '工具'],
      connections: ['r1', 'r3', 'r5']
    },
    { 
      id: 'r3', 
      title: '相反数与绝对值', 
      description: '两个只相异于符号的数互为相反数',
      tags: ['运算', '性质'],
      connections: ['r1', 'r2', 'r4']
    },
    { 
      id: 'r4', 
      title: '有理数的加减法', 
      description: '运用符号的法则进行加减运算',
      tags: ['运算', '技巧'],
      connections: ['r1', 'r3', 'r5', 'e1'] // 关联到整式的加减
    },
    { 
      id: 'r5', 
      title: '有理数的乘方与科学记数法', 
      description: '乘方的概念和科学记数法的表示方法',
      tags: ['运算', '应用'],
      connections: ['r2', 'r4']
    }
  ],
  expression: [
    { 
      id: 'e1', 
      title: '用字母表示数', 
      description: '用字母来表示数，这样表示的式子叫做字母式',
      tags: ['概念', '基础'],
      connections: ['e2', 'e3', 'r4'] // 关联到有理数的加减
    },
    { 
      id: 'e2', 
      title: '单项式与多项式', 
      description: '不加加号或减号的字母式叫做单项式',
      tags: ['概念', '分类'],
      connections: ['e1', 'e3', 'e4', 'p1'] // 关联到整式的乘法
    },
    { 
      id: 'e3', 
      title: '同类项', 
      description: '字母和字母的指数都相同的项叫做同类项',
      tags: ['概念', '技巧'],
      connections: ['e1', 'e2', 'e4']
    },
    { 
      id: 'e4', 
      title: '整式的加减运算', 
      description: '去括号、合并同类项、按降幂排列',
      tags: ['运算', '技巧'],
      connections: ['e2', 'e3', 'r4'] // 关联到有理数的加减
    }
  ],
  equation: [
    { 
      id: 'eq1', 
      title: '方程的概念', 
      description: '含有未知数且成立的等式叫做方程',
      tags: ['概念', '基础'],
      connections: ['eq2', 'eq3', 'eq4']
    },
    { 
      id: 'eq2', 
      title: '等式的性质', 
      description: '等式两边同时加（或减）同一个数，等式仍然成立',
      tags: ['性质', '工具'],
      connections: ['eq1', 'eq3', 'eq4']
    },
    { 
      id: 'eq3', 
      title: '一元一次方程的求解', 
      description: '利用等式的性质求未知数的值的过程',
      tags: ['方法', '技巧'],
      connections: ['eq1', 'eq2', 'eq4', 'ie1'] // 关联到不等式
    },
    { 
      id: 'eq4', 
      title: '应用一元一次方程解决实际问题', 
      description: '列方程解决实际问题的步骤和方法',
      tags: ['应用', '综合'],
      connections: ['eq1', 'eq2', 'eq3']
    }
  ],
  geometry: [
    { 
      id: 'g1', 
      title: '图形的运动', 
      description: '平移、旋转和对称叫做图形的运动',
      tags: ['概念', '变换'],
      connections: ['g2', 'g3', 'g4']
    },
    { 
      id: 'g2', 
      title: '线段与角', 
      description: '线段是直线上两点之间的部分',
      tags: ['基础', '图形'],
      connections: ['g1', 'g3', 'g5']
    },
    { 
      id: 'g3', 
      title: '平行线的性质', 
      description: '被一条线截成的两条线，若对应角相等，则这两条线平行',
      tags: ['性质', '图形'],
      connections: ['g1', 'g2', 'g4']
    },
    { 
      id: 'g4', 
      title: '垂线与到线的距离', 
      description: '从一点到一条线作的垂线段叫做点到线的距离',
      tags: ['性质', '图形'],
      connections: ['g1', 'g3']
    },
    { 
      id: 'g5', 
      title: '角的平分线', 
      description: '把角分成两个相等的角的射线叫做角的平分线',
      tags: ['性质', '图形'],
      connections: ['g2']
    }
  ],
  data: [
    { 
      id: 'd1', 
      title: '统计调查的步骤', 
      description: '提出问题 — 进行调查 — 数据分析 — 得出结论',
      tags: ['方法', '流程'],
      connections: ['d2', 'd3']
    },
    { 
      id: 'd2', 
      title: '统计图的种类', 
      description: '条形图、折线图和饼图等常见统计图',
      tags: ['表示', '工具'],
      connections: ['d1', 'd3', 'd4']
    },
    { 
      id: 'd3', 
      title: '平均数的概念', 
      description: '若干个数的和除以这些数的个数的商叫平均数',
      tags: ['概念', '计算'],
      connections: ['d1', 'd2', 'd4']
    },
    { 
      id: 'd4', 
      title: '方差离散程度的初步认识', 
      description: '方差反映一组数据的离散程度大小',
      tags: ['概念', '分析'],
      connections: ['d2', 'd3']
    }
  ],
  inequality: [
    { 
      id: 'ie1', 
      title: '不等式的概念', 
      description: '含有未知数的不等式叫做不等式',
      tags: ['概念', '基础'],
      connections: ['ie2', 'ie3', 'eq3'] // 关联到方程
    },
    { 
      id: 'ie2', 
      title: '不等式的性质', 
      description: '不等式两边同时加（或减）同一个数，不等式仍然成立',
      tags: ['性质', '工具'],
      connections: ['ie1', 'ie3']
    },
    { 
      id: 'ie3', 
      title: '一元一次不等式的解法', 
      description: '利用不等式的性质求解一元一次不等式',
      tags: ['方法', '技巧'],
      connections: ['ie1', 'ie2']
    }
  ],
  triangle: [
    { 
      id: 't1', 
      title: '三角形的分类', 
      description: '按角度分：锐角三角形、直角三角形和钝角三角形',
      tags: ['分类', '图形'],
      connections: ['t2', 't3', 't4']
    },
    { 
      id: 't2', 
      title: '三角形的边关系', 
      description: '三角形任意两边之和大于第三边',
      tags: ['性质', '图形'],
      connections: ['t1', 't3']
    },
    { 
      id: 't3', 
      title: '三角形的角关系', 
      description: '三角形的三个内角和等于180度',
      tags: ['性质', '图形'],
      connections: ['t1', 't2', 't4']
    },
    { 
      id: 't4', 
      title: '全等三角形的判定', 
      description: 'SSS、SAS、ASA、AAS和HL五种判定方法',
      tags: ['判定', '图形'],
      connections: ['t1', 't2', 't3']
    }
  ],
  polynomial: [
    { 
      id: 'p1', 
      title: '乘法公式', 
      description: '(a+b)² = a² + 2ab + b² 等三个重要的乘法公式',
      tags: ['公式', '运算'],
      connections: ['p2', 'e2'] // 关联到单项式
    },
    { 
      id: 'p2', 
      title: '因式分解', 
      description: '把多项式写成几个整式的乘积的形式',
      tags: ['运算', '技巧'],
      connections: ['p1', 'e2'] // 关联到单项式
    }
  ],
  fraction: [
    { 
      id: 'f1', 
      title: '分数的意义', 
      description: '单位"1"的几个等分中的若干等分叫做分数',
      tags: ['概念', '基础'],
      connections: ['f2', 'f3', 'f4']
    },
    { 
      id: 'f2', 
      title: '分数的基本性质', 
      description: '分子分母同时乘（或除）同一个不为零的数，分数值不变',
      tags: ['性质', '运算'],
      connections: ['f1', 'f3']
    },
    { 
      id: 'f3', 
      title: '分数的加减法', 
      description: '化成同分母分数，然后按照同分母的加减法则计算',
      tags: ['运算', '技巧'],
      connections: ['f1', 'f2', 'f4']
    },
    { 
      id: 'f4', 
      title: '分数的乘除法', 
      description: '分数乘法：分子乘分子，分母乘分母',
      tags: ['运算', '技巧'],
      connections: ['f1', 'f2', 'f3']
    }
  ]
}

// 章节对应的知识点
const chapterKnowledgePoints = computed(() => {
  return knowledgePoints[currentChapter.value] || []
})

// 构建思维导图数据
const mapData = computed(() => {
  const points = chapterKnowledgePoints.value
  if (!points || points.length === 0) return { nodes: [], links: [] }
  
  // 创建节点数据
  const nodes = points.map(point => ({
    id: point.id,
    title: point.title,
    description: point.description,
    tags: point.tags,
    connections: point.connections || [],
    // 计算节点大小（基于连接数量）
    size: 16 + (point.connections?.length || 0) * 4
  }))
  
  // 创建连接数据（避免重复）
  const links = []
  const linkSet = new Set()
  
  points.forEach(point => {
    point.connections?.forEach(connId => {
      // 确保连接不重复且双向只记录一次
      const linkKey = [point.id, connId].sort().join('-')
      if (!linkSet.has(linkKey)) {
        linkSet.add(linkKey)
        links.push({
          source: point.id,
          target: connId
        })
      }
    })
  })
  
  return { nodes, links }
})

// 选中知识点时加载对应的学习组件
const loadKnowledgePointComponent = async (pointId) => {
  // 根据知识点ID返回对应的组件
  // 这里简化处理，实际应该根据点ID动态加载对应章节的具体组件
  const chapterMap = {
    rational: 'RationalNumberDemo',
    expression: 'ExpressionDemo', 
    equation: 'EquationDemo',
    geometry: 'GeometryDemo',
    data: 'DataDemo',
    inequality: 'InequalityDemo',
    triangle: 'TriangleDemo',
    polynomial: 'PolynomialDemo',
    fraction: 'FractionDemo'
  }
  
  // 找到知识点所属的章节
  let chapterId = null
  for (const [chapId, points] of Object.entries(knowledgePoints)) {
    if (points.some(p => p.id === pointId)) {
      chapterId = chapId
      break
    }
  }
  
  if (chapterId && chapterMap[chapterId]) {
    try {
      const component = await import(`../components/${chapterMap[chapterId]}.vue`)
      return component.default
    } catch (e) {
      console.warn(`Component not found for ${chapterMap[chapterId]}`, e)
      return null
    }
  }
  return null
}

// 点击思维导图节点
const handleNodeClick = async (node) => {
  selectedKnowledgePoint.value = {
    ...node,
    component: await loadKnowledgePointComponent(node.id)
  }
}

// 初始化思维导图
const initializeKnowledgeMap = async () => {
  loading.value = true
  try {
    // 等待DOM加载完成
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const container = svgRef.value.parentElement
    if (!container) {
      loading.value = false
      return
    }
    
    const width = container.clientWidth
    const height = 500
    
    // 创建SVG
    const svg = d3.select(svgRef.value)
      .attr('width', width)
      .attr('height', height)
      .style('background', 'rgba(15,23,42,.6)')
    
    // 创建组
    const g = svg.append('g')
    const linkG = g.append('g').attr('class', 'links')
    const nodeG = g.append('g').attr('class', 'nodes')
    
    // 创建缩放行为
    const zoom = d3.zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })
    
    svg.call(zoom)
    
    // 创建模拟力
    const simulation = d3.forceSimulation()
      .force('link', d3.forceLink().id(d => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(50))
      .on('tick', ticked)
    
    // 渲染函数
    function render(data) {
      // 更新模拟力的连接
      simulation.nodes(data.nodes).force('link').links(data.links)
      
      // 节点拖拽行为
    const drag = d3.drag()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
        // 拖拽开始时选中该节点
        if (selectedNodeId.value !== d.id) {
          selectedNodeId.value = d.id
        }
      })
      .on('drag', (event, d) => {
        d.fx = event.x
        d.fy = event.y
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0)
      })
    
    // 高亮与选中节点相关的链接
    const highlightLinks = (nodeId) => {
      if (!nodeId) {
        link.attr('stroke', 'rgba(148,163,184,0.2)')
          .attr('stroke-width', 1.5)
        return
      }
      link.each(function(d) {
        const isConnected = d.source.id === nodeId || d.target.id === nodeId
        d3.select(this)
          .attr('stroke', isConnected ? '#fbbf24' : 'rgba(148,163,184,0.1)')
          .attr('stroke-width', isConnected ? 3 : 1)
      })
    }
    
    // 绘制连接线
    const link = linkG.selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', 'rgba(148,163,184,0.2)')
      .attr('stroke-width', 1.5)
    
    // 绘制节点
    const node = nodeG.selectAll('g')
      .data(data.nodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(drag)
      .on('click', (event, d) => {
        // 防止事件冒泡
        event.stopPropagation()
        selectedNodeId.value = d.id
        highlightLinks(d.id)
        handleNodeClick(d)
      })
      .on('mouseenter', (event, d) => {
        d3.select(event.currentTarget).select('circle').attr('stroke-width', 3)
        highlightLinks(d.id)
      })
      .on('mouseleave', (event, d) => {
        // 只有当节点未被选中时才恢复
        if (selectedNodeId.value !== d.id) {
          d3.select(event.currentTarget).select('circle').attr('stroke-width', 2)
          highlightLinks(null)
        }
      })
    
    // 节点圆圈
    node.append('circle')
      .attr('r', d => d.size)
      .attr('fill', d => {
        // 根据章节分配颜色
        const chapterColors = {
          rational: '#fbbf24',
          expression: '#60a5fa',
          equation: '#a78bfa',
          geometry: '#34d399',
          data: '#f87171',
          inequality: '#f472b6',
          triangle: '#fbbf24',
          polynomial: '#60a5fa',
          fraction: '#a78bfa'
        }
        return chapterColors[currentChapter.value] || '#fbbf24'
      })
      .attr('stroke', d => selectedNodeId.value === d.id ? '#ffffff' : '#1e293b')
      .attr('stroke-width', d => selectedNodeId.value === d.id ? 4 : 2)
      .attr('filter', d => selectedNodeId.value === d.id ? 'url(#glow)' : null)
    
    // 添加发光滤镜（仅在需要时定义一次）
    const defs = svg.append('defs')
    const filter = defs.append('filter')
      .attr('id', 'glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%')
    filter.append('feGaussianBlur')
      .attr('stdDeviation', '4')
      .attr('result', 'coloredBlur')
    const feMerge = filter.append('feMerge')
    feMerge.append('feMergeNode').attr('in', 'coloredBlur')
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic')
    
    // 节点标题
    node.append('text')
      .attr('x', 0)
      .attr('y', -20)
      .attr('text-anchor', 'middle')
      .attr('fill', '#f1f5f9')
      .attr('font-size', '12px')
      .attr('font-weight', 600)
      .text(d => d.title)
      .style('pointer-events', 'none')
      .style('user-select', 'none')
    
    // 节点标签（技能标签）
    const labelGroups = node.selectAll('.label-group')
      .data(d => d.tags.map((tag, i) => ({ tag, index: i, parent: d })))
      .join('g')
      .attr('class', 'label-group')
      .attr('transform', d => {
        // 计算标签位置（在节点下方排列）
        const radius = d.parent.size
        const offset = 20 + (d.index * 18)
        return `translate(${-d.tag.length * 4},${offset})`
      })
    
    labelGroups.append('rect')
      .attr('width', d => d.tag.length * 8 + 10)
      .attr('height', 16)
      .attr('rx', 4)
      .attr('fill', 'rgba(30,41,59,0.6)')
      .attr('stroke', 'rgba(148,163,184,0.3)')
      .attr('stroke-width', 1)
    
    labelGroups.append('text')
      .attr('x', 5)
      .attr('y', 12)
      .attr('fill', '#94a3b8')
      .attr('font-size', '10px')
      .text(d => d.tag)
      .style('pointer-events', 'none')
      .style('user-select', 'none')
    }
    
    // 模拟力tick事件处理
    function ticked() {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
      
      node
        .attr('transform', d => `translate(${d.x},${d.y})`)
    }
    
    // 初始渲染
    render(mapData.value)
    
    // 监听数据变化
    const unwatchData = watch(mapData, (newData) => {
      render(newData)
    })
    
    // 监听选中节点变化，更新节点和链接样式
    const unwatchNode = watch(selectedNodeId, (newId) => {
      if (link) {
        highlightLinks(newId)
      }
      if (node) {
        node.select('circle')
          .attr('stroke', d => newId === d.id ? '#ffffff' : '#1e293b')
          .attr('stroke-width', d => newId === d.id ? 4 : 2)
          .attr('filter', d => newId === d.id ? 'url(#glow)' : null)
      }
    })
    
    // 处理组件卸载时清理监听
    onMounted(() => {
      return () => {
        unwatchData()
        unwatchNode()
      }
    })
    
  } catch (err) {
    console.error('Failed to initialize knowledge map:', err)
  } finally {
    loading.value = false
  }
}

// 章节切换时重新生成思维导图
watch(currentChapter, () => {
  // 重新初始化思维导图
  initializeKnowledgeMap()
  // 清除选中的知识点和节点
  selectedKnowledgePoint.value = null
  selectedNodeId.value = null
})

// 组件挂载时初始化
onMounted(() => {
  initializeKnowledgeMap()
})
</script>

<style scoped>
.knowledge-map-container {
  min-height: 500px;
}

/* 淡入淡出动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 链接线动画效果 */
.links line {
  transition: stroke-width 0.2s, stroke 0.2s;
}

/* 节点悬停效果 */
.nodes g:hover circle {
  filter: brightness(1.1);
  transition: filter 0.2s;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .knowledge-map-container {
    min-height: 400px;
  }
}
</style>