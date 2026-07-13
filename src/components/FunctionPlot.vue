<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">
      <div class="canvas-container p-4">
        <div ref="chartRef" class="w-full h-[500px]"></div>
      </div>
    </div>
    <div class="control-panel p-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">函数设置</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">选择函数</label>
          <select v-model="selectedFunction" @change="updatePlot" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
            <option v-for="func in functions" :key="func.id" :value="func.id">{{ func.name }}</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">参数 a: {{ params.a }}</label>
          <input type="range" v-model.number="params.a" @input="updatePlot" :min="-10" :max="10" :step="0.1" class="w-full">
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">参数 b: {{ params.b }}</label>
          <input type="range" v-model.number="params.b" @input="updatePlot" :min="-10" :max="10" :step="0.1" class="w-full">
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">参数 c: {{ params.c }}</label>
          <input type="range" v-model.number="params.c" @input="updatePlot" :min="-10" :max="10" :step="0.1" class="w-full">
        </div>
        
        <div class="pt-4 border-t border-gray-200">
          <div class="text-center">
            <div class="text-sm text-gray-600 mb-2">当前函数</div>
            <div class="text-xl font-bold text-purple-600" v-html="currentFormula"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const chartRef = ref(null)
const selectedFunction = ref('sin')
const params = ref({ a: 1, b: 1, c: 0 })

const functions = [
  { id: 'sin', name: '正弦函数', formula: 'a·sin(bx + c)', func: (x, a, b, c) => a * Math.sin(b * x + c) },
  { id: 'cos', name: '余弦函数', formula: 'a·cos(bx + c)', func: (x, a, b, c) => a * Math.cos(b * x + c) },
  { id: 'tan', name: '正切函数', formula: 'a·tan(bx)', func: (x, a, b, c) => a * Math.tan(b * x) },
  { id: 'parabola', name: '抛物线', formula: 'ax² + bx + c', func: (x, a, b, c) => a * x * x + b * x + c },
  { id: 'exp', name: '指数函数', formula: 'a·e^(bx)', func: (x, a, b, c) => a * Math.exp(b * x) },
  { id: 'log', name: '对数函数', formula: 'a·ln(x + c)', func: (x, a, b, c) => a * Math.log(x + Math.abs(c) + 1) },
  { id: 'sqrt', name: '平方根函数', formula: 'a·√(x + c)', func: (x, a, b, c) => a * Math.sqrt(Math.max(0, x + c)) },
  { id: 'abs', name: '绝对值函数', formula: 'a·|bx + c|', func: (x, a, b, c) => a * Math.abs(b * x + c) }
]

const currentFormula = computed(() => {
  const func = functions.find(f => f.id === selectedFunction.value)
  if (!func) return ''
  let formula = func.formula
  formula = formula.replace(/a/g, params.value.a.toFixed(1))
  formula = formula.replace(/b/g, params.value.b.toFixed(1))
  formula = formula.replace(/c/g, params.value.c.toFixed(1))
  return formula
})

let svg = null

const drawPlot = () => {
  if (!chartRef.value) return
  
  const width = chartRef.value.clientWidth
  const height = 500
  const margin = { top: 20, right: 20, bottom: 40, left: 50 }
  
  d3.select(chartRef.value).selectAll('*').remove()
  
  svg = d3.select(chartRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
  
  const innerWidth = width - margin.left - margin.right
  const innerHeight = height - margin.top - margin.bottom
  
  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  
  const xScale = d3.scaleLinear()
    .domain([-10, 10])
    .range([0, innerWidth])
  
  const yScale = d3.scaleLinear()
    .domain([-5, 5])
    .range([innerHeight, 0])
  
  const xAxis = d3.axisBottom(xScale).ticks(11)
  const yAxis = d3.axisLeft(yScale).ticks(11)
  
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(xAxis)
    .style('color', '#666')
  
  g.append('g')
    .call(yAxis)
    .style('color', '#666')
  
  g.append('line')
    .attr('x1', 0)
    .attr('y1', innerHeight / 2)
    .attr('x2', innerWidth)
    .attr('y2', innerHeight / 2)
    .style('stroke', '#ccc')
    .style('stroke-dasharray', '4,4')
  
  g.append('line')
    .attr('x1', innerWidth / 2)
    .attr('y1', 0)
    .attr('x2', innerWidth / 2)
    .attr('y2', innerHeight)
    .style('stroke', '#ccc')
    .style('stroke-dasharray', '4,4')
  
  const func = functions.find(f => f.id === selectedFunction.value)
  if (!func) return
  
  const line = d3.line()
    .x(d => xScale(d.x))
    .y(d => yScale(d.y))
    .defined(d => !isNaN(d.y) && isFinite(d.y))
  
  const data = []
  for (let x = -10; x <= 10; x += 0.01) {
    const y = func.func(x, params.value.a, params.value.b, params.value.c)
    if (Math.abs(y) <= 100) {
      data.push({ x, y })
    }
  }
  
  g.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', '#8b5cf6')
    .attr('stroke-width', 2)
    .attr('d', line)
  
  g.append('text')
    .attr('transform', `translate(${innerWidth / 2}, ${innerHeight + 35})`)
    .style('text-anchor', 'middle')
    .style('fill', '#666')
    .style('font-size', '12px')
    .text('x')
  
  g.append('text')
    .attr('transform', `translate(-35, ${innerHeight / 2}) rotate(-90)`)
    .style('text-anchor', 'middle')
    .style('fill', '#666')
    .style('font-size', '12px')
    .text('y')
}

const updatePlot = () => {
  drawPlot()
}

onMounted(() => {
  drawPlot()
  window.addEventListener('resize', drawPlot)
})

watch([selectedFunction, params], () => {
  drawPlot()
}, { deep: true })
</script>
