<template>
  <div>
    <nav class="bg-white/5 backdrop-blur-md border-b border-white/10">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-end h-12">
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
import FunctionPlot from '../components/FunctionPlot.vue'
import GeometryModeler from '../components/GeometryModeler.vue'
import Geometry3D from '../components/Geometry3D.vue'
import FormulaDemo from '../components/FormulaDemo.vue'
import BalanceGame from '../components/BalanceGame.vue'

const currentTab = ref('modeler')

const tabs = [
  { id: 'function', name: '函数图像' },
  { id: 'modeler', name: '点-线-面-立体' },
  { id: '3d', name: '3D图形' },
  { id: 'formula', name: '公式推导' },
  { id: 'balance', name: '方程图形化' }
]
</script>
