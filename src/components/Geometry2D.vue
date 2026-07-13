<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">
      <div class="canvas-container p-4">
        <svg ref="svgRef" class="w-full h-[500px]" viewBox="-250 -250 500 500">
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#8b5cf6"/>
            </marker>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#eee" stroke-width="0.5"/>
            </pattern>
          </defs>
          
          <rect width="500" height="500" x="-250" y="-250" fill="url(#grid)"/>
          
          <line x1="-250" y1="0" x2="250" y2="0" stroke="#9ca3af" stroke-width="1"/>
          <line x1="0" y1="-250" x2="0" y2="250" stroke="#9ca3af" stroke-width="1"/>
          
          <line v-for="i in 10" :key="'hx'+i" 
            :x1="i * 50" :y1="-5" :x2="i * 50" :y2="5" stroke="#9ca3af" stroke-width="1"/>
          <line v-for="i in 10" :key="'hn'+i" 
            :x1="-i * 50" :y1="-5" :x2="-i * 50" :y2="5" stroke="#9ca3af" stroke-width="1"/>
          <line v-for="i in 10" :key="'vy'+i" 
            :x1="-5" :y1="i * 50" :x2="5" :y2="i * 50" stroke="#9ca3af" stroke-width="1"/>
          <line v-for="i in 10" :key="'vn'+i" 
            :x1="-5" :y1="-i * 50" :x2="5" :y2="-i * 50" stroke="#9ca3af" stroke-width="1"/>
          
          <text x="250" y="15" fill="#6b7280" font-size="12">x</text>
          <text x="10" y="-245" fill="#6b7280" font-size="12">y</text>
          
          <circle v-if="showCircle" :cx="circleCenter.x" :cy="circleCenter.y" 
            :r="circleRadius" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="5,5"/>
          <circle v-if="showCircle" :cx="circleCenter.x" :cy="circleCenter.y" 
            r="4" fill="#ef4444"/>
          
          <circle v-if="showCircle" :cx="circleCenter.x + circleRadius" :cy="circleCenter.y" 
            r="4" fill="#f97316"/>
          <line v-if="showCircle" :x1="circleCenter.x" :y1="circleCenter.y" 
            :x2="circleCenter.x + circleRadius" :y2="circleCenter.y" 
            stroke="#f97316" stroke-width="2" marker-end="url(#arrowhead)"/>
          
          <polygon v-if="showTriangle" :points="trianglePoints" fill="none" 
            stroke="#22c55e" stroke-width="2"/>
          <circle v-for="(p, i) in triangleCoords" :key="'t'+i" 
            :cx="p.x" :cy="p.y" r="4" fill="#22c55e"/>
          
          <line v-if="showLine" :x1="lineStart.x" :y1="lineStart.y" 
            :x2="lineEnd.x" :y2="lineEnd.y" stroke="#3b82f6" stroke-width="2" 
            marker-end="url(#arrowhead)"/>
          <circle v-if="showLine" :cx="lineStart.x" :cy="lineStart.y" r="4" fill="#3b82f6"/>
          
          <rect v-if="showRectangle" :x="rectStart.x" :y="rectStart.y" 
            :width="rectWidth" :height="rectHeight" fill="none" stroke="#a855f7" stroke-width="2"/>
          
          <circle v-for="(point, i) in points" :key="'p'+i" 
            :cx="point.x" :cy="point.y" :r="point.r" :fill="point.color"/>
        </svg>
      </div>
    </div>
    
    <div class="control-panel p-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">几何图形</h3>
      
      <div class="space-y-4">
        <div>
          <label class="flex items-center space-x-2">
            <input type="checkbox" v-model="showCircle" class="w-4 h-4 text-purple-600 rounded">
            <span class="text-sm text-gray-700">圆形</span>
          </label>
        </div>
        
        <div v-if="showCircle" class="pl-4 space-y-2">
          <div>
            <label class="block text-xs text-gray-500">半径: {{ circleRadius }}</label>
            <input type="range" v-model.number="circleRadius" min="20" max="150" class="w-full">
          </div>
        </div>
        
        <div>
          <label class="flex items-center space-x-2">
            <input type="checkbox" v-model="showTriangle" class="w-4 h-4 text-purple-600 rounded">
            <span class="text-sm text-gray-700">三角形</span>
          </label>
        </div>
        
        <div>
          <label class="flex items-center space-x-2">
            <input type="checkbox" v-model="showLine" class="w-4 h-4 text-purple-600 rounded">
            <span class="text-sm text-gray-700">线段</span>
          </label>
        </div>
        
        <div>
          <label class="flex items-center space-x-2">
            <input type="checkbox" v-model="showRectangle" class="w-4 h-4 text-purple-600 rounded">
            <span class="text-sm text-gray-700">矩形</span>
          </label>
        </div>
        
        <div class="pt-4 border-t border-gray-200">
          <button @click="animateShape" class="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            演示动画
          </button>
        </div>
        
        <div class="pt-4">
          <h4 class="text-sm font-medium text-gray-700 mb-2">当前图形属性</h4>
          <div v-if="showCircle" class="text-xs text-gray-600 space-y-1">
            <div>圆面积: {{ circleArea.toFixed(1) }}</div>
            <div>圆周长: {{ circleCircumference.toFixed(1) }}</div>
          </div>
          <div v-if="showTriangle" class="text-xs text-gray-600 space-y-1">
            <div>三角形面积: {{ triangleArea.toFixed(1) }}</div>
            <div>三角形周长: {{ trianglePerimeter.toFixed(1) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const svgRef = ref(null)

const showCircle = ref(true)
const showTriangle = ref(true)
const showLine = ref(false)
const showRectangle = ref(false)

const circleCenter = ref({ x: 0, y: 0 })
const circleRadius = ref(80)

const triangleCoords = ref([
  { x: 100, y: -50 },
  { x: 150, y: 50 },
  { x: 50, y: 50 }
])

const lineStart = ref({ x: -100, y: -100 })
const lineEnd = ref({ x: 100, y: 100 })

const rectStart = ref({ x: -100, y: -60 })
const rectWidth = ref(120)
const rectHeight = ref(80)

const points = ref([
  { x: 0, y: 0, r: 6, color: '#ef4444' }
])

const circleArea = computed(() => Math.PI * circleRadius.value * circleRadius.value)
const circleCircumference = computed(() => 2 * Math.PI * circleRadius.value)

const trianglePoints = computed(() => {
  return triangleCoords.value.map(p => `${p.x},${p.y}`).join(' ')
})

const triangleArea = computed(() => {
  const [a, b, c] = triangleCoords.value
  return Math.abs((a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2)
})

const trianglePerimeter = computed(() => {
  const [a, b, c] = triangleCoords.value
  const d1 = Math.sqrt(Math.pow(b.x - a.x, 2) + Math.pow(b.y - a.y, 2))
  const d2 = Math.sqrt(Math.pow(c.x - b.x, 2) + Math.pow(c.y - b.y, 2))
  const d3 = Math.sqrt(Math.pow(a.x - c.x, 2) + Math.pow(a.y - c.y, 2))
  return d1 + d2 + d3
})

const animateShape = () => {
  let angle = 0
  const animate = () => {
    angle += 0.05
    circleCenter.value = {
      x: 50 * Math.cos(angle),
      y: 50 * Math.sin(angle)
    }
    circleRadius.value = 60 + 20 * Math.sin(angle * 2)
    requestAnimationFrame(animate)
  }
  animate()
}
</script>
