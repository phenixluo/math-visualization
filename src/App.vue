<template>
  <div class="min-h-screen">
    <nav class="bg-white/10 backdrop-blur-md border-b border-white/20">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-2">
            <svg class="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <span class="text-xl font-bold text-white">数学图形化展示</span>
          </div>
          <div class="flex items-center space-x-1">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              @click="currentTab = tab.id"
              :class="['nav-link text-white font-medium', currentTab === tab.id ? 'active' : '']"
            >
              {{ tab.name }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 py-6">
      <FunctionPlot v-if="currentTab === 'function'" />
      <GeometryModeler v-else-if="currentTab === 'modeler'" />
      <Geometry3D v-else-if="currentTab === '3d'" />
      <FormulaDemo v-else-if="currentTab === 'formula'" />
      <BalanceGame v-else-if="currentTab === 'balance'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FunctionPlot from './components/FunctionPlot.vue'
import GeometryModeler from './components/GeometryModeler.vue'
import Geometry3D from './components/Geometry3D.vue'
import FormulaDemo from './components/FormulaDemo.vue'
import BalanceGame from './components/BalanceGame.vue'

const currentTab = ref('modeler')

const tabs = [
  { id: 'function', name: '函数图像' },
  { id: 'modeler', name: '几何建模' },
  { id: '3d', name: '3D图形' },
  { id: 'formula', name: '公式推导' },
  { id: 'balance', name: '方程图形化' }
]
</script>
