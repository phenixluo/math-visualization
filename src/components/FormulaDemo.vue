<template>
  <div class="max-w-4xl mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="control-panel p-4">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">选择演示内容</h3>
        
        <div class="space-y-2">
          <button 
            v-for="demo in demos" 
            :key="demo.id"
            @click="selectDemo(demo.id)"
            :class="['w-full text-left px-4 py-3 rounded-lg border transition-all', 
              currentDemo === demo.id 
                ? 'border-purple-500 bg-purple-50' 
                : 'border-gray-200 hover:border-gray-300']"
          >
            <div class="font-medium text-gray-800">{{ demo.name }}</div>
            <div class="text-sm text-gray-500">{{ demo.description }}</div>
          </button>
        </div>
      </div>
      
      <div class="control-panel p-6">
        <div class="text-center mb-6">
          <h4 class="text-lg font-semibold text-gray-800 mb-2">{{ currentDemoInfo.name }}</h4>
          <div class="text-sm text-gray-500">{{ currentDemoInfo.description }}</div>
        </div>
        
        <div v-if="currentDemo === 'distributive'" class="space-y-6">
          <div class="text-center">
            <div class="text-2xl font-bold text-purple-600 mb-4">{{ currentDemoInfo.formula }}</div>
          </div>
          
          <div class="space-y-4">
            <div v-for="(step, index) in distributiveSteps" :key="index" 
              :class="['p-4 rounded-lg border-2 transition-all', 
                currentStep >= index ? 'border-green-500 bg-green-50' : 'border-gray-200 bg-gray-50']">
              <div class="flex items-center space-x-2 mb-2">
                <span class="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {{ index + 1 }}
                </span>
                <span class="font-medium text-gray-700">{{ step.title }}</span>
              </div>
              <div v-if="currentStep >= index" class="text-lg text-center py-4">
                <div v-html="step.content"></div>
              </div>
              <div v-else class="text-center py-4 text-gray-400">
                点击下一步查看
              </div>
            </div>
          </div>
          
          <div class="flex justify-center space-x-4 pt-4">
            <button @click="prevStep" :disabled="currentStep === 0" 
              :class="['px-6 py-2 rounded-lg transition-colors', 
                currentStep === 0 
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                  : 'bg-purple-600 text-white hover:bg-purple-700']">
              上一步
            </button>
            <button @click="nextStep" :disabled="currentStep >= distributiveSteps.length - 1"
              :class="['px-6 py-2 rounded-lg transition-colors', 
                currentStep >= distributiveSteps.length - 1 
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                  : 'bg-green-600 text-white hover:bg-green-700']">
              {{ currentStep >= distributiveSteps.length - 1 ? '完成' : '下一步' }}
            </button>
            <button @click="resetSteps" class="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
              重置
            </button>
          </div>
          
          <div v-if="showBalanceAnimation" class="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
            <div class="text-center text-amber-800 font-medium mb-4">⚖️ 天平演示</div>
            <div class="flex justify-around items-center">
              <div class="text-center">
                <div class="text-2xl font-bold text-purple-600 mb-2">{{ balanceLeft }}</div>
                <div class="w-20 h-4 bg-purple-200 rounded-full"></div>
              </div>
              <div class="text-4xl">⚖️</div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600 mb-2">{{ balanceRight }}</div>
                <div class="w-20 h-4 bg-green-200 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="currentDemo === 'area'" class="space-y-4">
          <div class="text-center mb-4">
            <div class="text-2xl font-bold text-purple-600">{{ currentDemoInfo.formula }}</div>
          </div>
          
          <div class="flex justify-center">
            <svg width="300" height="200" viewBox="0 0 300 200">
              <rect x="20" y="20" width="200" height="120" fill="none" stroke="#8b5cf6" stroke-width="2"/>
              <line x1="100" y1="20" x2="100" y2="140" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,4"/>
              <line x1="20" y1="80" x2="220" y2="80" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,4"/>
              
              <text x="60" y="55" fill="#8b5cf6" font-size="14">a</text>
              <text x="150" y="55" fill="#8b5cf6" font-size="14">b</text>
              <text x="15" y="105" fill="#8b5cf6" font-size="14">c</text>
              
              <text x="60" y="105" fill="#ef4444" font-size="12">a×c</text>
              <text x="150" y="105" fill="#ef4444" font-size="12">b×c</text>
              
              <rect x="20" y="20" width="80" height="60" :fill="showArea1 ? '#a78bfa' : 'none'" :opacity="showArea1 ? 0.5 : 0"/>
              <rect x="100" y="20" width="120" height="60" :fill="showArea2 ? '#c4b5fd' : 'none'" :opacity="showArea2 ? 0.5 : 0"/>
              <rect x="20" y="80" width="80" height="60" :fill="showArea3 ? '#d8b4fe' : 'none'" :opacity="showArea3 ? 0.5 : 0"/>
              <rect x="100" y="80" width="120" height="60" :fill="showArea4 ? '#e9d5ff' : 'none'" :opacity="showArea4 ? 0.5 : 0"/>
            </svg>
          </div>
          
          <button @click="animateArea" class="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            {{ areaAnimating ? '重置动画' : '播放动画' }}
          </button>
        </div>
        
        <div v-if="currentDemo === 'pythagorean'" class="space-y-4">
          <div class="text-center mb-4">
            <div class="text-2xl font-bold text-purple-600">{{ currentDemoInfo.formula }}</div>
          </div>
          
          <div class="flex justify-center">
            <svg width="300" height="300" viewBox="0 0 300 300">
              <rect x="50" y="100" width="100" height="100" fill="#ef4444" opacity="0.3"/>
              <rect x="150" y="200" width="100" height="100" fill="#3b82f6" opacity="0.3"/>
              <rect x="150" y="100" width="100" height="100" fill="#22c55e" opacity="0.3"/>
              
              <text x="100" y="155" fill="#ef4444" font-size="16">{{ pythagorean.a }}²</text>
              <text x="200" y="255" fill="#3b82f6" font-size="16">{{ pythagorean.b }}²</text>
              <text x="200" y="155" fill="#22c55e" font-size="16">{{ pythagorean.c }}²</text>
              
              <polygon points="50,200 150,200 50,100" fill="none" stroke="#8b5cf6" stroke-width="2"/>
              <line x1="150" y1="200" x2="150" y2="100" stroke="#ef4444" stroke-width="2"/>
              <line x1="50" y1="100" x2="150" y2="100" stroke="#3b82f6" stroke-width="2"/>
              
              <text x="95" y="215" fill="#8b5cf6" font-size="14">a</text>
              <text x="155" y="150" fill="#8b5cf6" font-size="14">b</text>
              <text x="95" y="145" fill="#8b5cf6" font-size="14">c</text>
            </svg>
          </div>
          
          <div class="grid grid-cols-3 gap-4 text-center">
            <div class="p-3 bg-red-50 rounded-lg">
              <div class="text-2xl font-bold text-red-600">{{ pythagorean.a * pythagorean.a }}</div>
              <div class="text-sm text-gray-500">a²</div>
            </div>
            <div class="p-3 bg-blue-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-600">{{ pythagorean.b * pythagorean.b }}</div>
              <div class="text-sm text-gray-500">b²</div>
            </div>
            <div class="p-3 bg-green-50 rounded-lg">
              <div class="text-2xl font-bold text-green-600">{{ pythagorean.c * pythagorean.c }}</div>
              <div class="text-sm text-gray-500">c²</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const currentDemo = ref('distributive')
const currentStep = ref(0)
const showBalanceAnimation = ref(true)
const balanceLeft = ref('3 × (2 + 5)')
const balanceRight = ref('3×2 + 3×5')

const showArea1 = ref(false)
const showArea2 = ref(false)
const showArea3 = ref(false)
const showArea4 = ref(false)
const areaAnimating = ref(false)

const pythagorean = ref({
  a: 3,
  b: 4,
  c: 5
})

const demos = [
  { id: 'distributive', name: '乘法分配律', description: 'a × (b + c) = a×b + a×c', formula: 'a × (b + c) = ab + ac' },
  { id: 'area', name: '长方形面积推导', description: '利用分割法推导面积公式', formula: 'S = (a + b) × c' },
  { id: 'pythagorean', name: '勾股定理', description: '直角三角形三边关系', formula: 'a² + b² = c²' }
]

const currentDemoInfo = computed(() => {
  return demos.find(d => d.id === currentDemo.value) || demos[0]
})

const distributiveSteps = [
  { title: '问题引入', content: '<div class="text-xl">假设我们有：</div><div class="text-2xl font-bold text-purple-600 mt-2">3 × (2 + 5)</div>' },
  { title: '分配律展开', content: '<div class="text-xl">根据分配律：</div><div class="text-2xl font-bold text-green-600 mt-2">3 × 2 + 3 × 5</div>' },
  { title: '分别计算', content: '<div class="text-xl">计算两部分：</div><div class="text-2xl font-bold text-blue-600 mt-2">6 + 15</div>' },
  { title: '得出结果', content: '<div class="text-xl">最终结果：</div><div class="text-3xl font-bold text-red-600 mt-2">21</div>' },
  { title: '验证等式', content: '<div class="text-xl">验证两边相等：</div><div class="text-xl mt-2">3 × 7 = 6 + 15</div><div class="text-2xl font-bold text-green-600 mt-2">21 = 21 ✓</div>' }
]

const selectDemo = (demoId) => {
  currentDemo.value = demoId
  currentStep.value = 0
}

const nextStep = () => {
  if (currentStep.value < distributiveSteps.length - 1) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const resetSteps = () => {
  currentStep.value = 0
}

const animateArea = () => {
  if (areaAnimating.value) {
    showArea1.value = false
    showArea2.value = false
    showArea3.value = false
    showArea4.value = false
    areaAnimating.value = false
    return
  }
  
  areaAnimating.value = true
  showArea1.value = true
  setTimeout(() => showArea2.value = true, 500)
  setTimeout(() => showArea3.value = true, 1000)
  setTimeout(() => showArea4.value = true, 1500)
}

watch(currentDemo, () => {
  currentStep.value = 0
})
</script>
